"""V44 phase 1: find the real CAD source for every active live-demo part and its source->model transform.

demo-placements-rev12.json (design layout rev 12) holds, per active part, the page's matrixWorld M and pivot c (world = M (v_model - c)).
Here we find S (source -> model): a translation when the source is already in the model frame (project CAD,
moved copies), or one of 24 axis rotations + translation for vendor-frame files, verified against the model
mesh bounds. Output: sources.json {name: {file, rot: 3x3, t: [..], status}}. Unmatched parts are listed.
"""
from pathlib import Path
import json, gzip, re, itertools
import numpy as np
import cadquery as cq
import trimesh

R = Path(__file__).resolve().parent.parent
PL = json.loads((R / 'print-v44-nano/demo-placements-rev12.json').read_text(encoding='utf-8-sig'))['rows']
MODEL = {p['name']: p for p in json.loads(gzip.decompress((R / 'workbench/public/stock-battery-fit/editor-model-tp2700.json.gz').read_bytes()))['parts']}
M10 = R / 'real-fairlead-revision/voltra-module10'
VEND = R / 'rectangular-body-study/vendor'
FIXED = {
    'TRIAL_Pi4_upright': VEND / 'pi4.step', 'TRIAL_driver_fan': VEND / 'fan/NF-A4x10_public-CAD.stp',
    'TRIAL_Waveshare_DSI_E_portrait': R / 'supplier-cad/waveshare-4dpi-c/4inch-dpi-lcd_c.stp',
    'FM9 Drum V8 widened 6 mm': M10 / 'Drum_V8_widened_6mm.brep',
    'V43_PRINT_6001_cartridge_left_FM6': M10 / '6001 pillow block left (moved +5 mm).step',
    'V43_PRINT_6001_cartridge_right_FM9': M10 / '6001 pillow block right (moved +1 mm).step',
    'REF_drum_shaft_12mm_176mm': R / 'rev12-176-shaft/REF_drum_shaft_12mm_176mm.brep',       # rev 12: user shaft cut to 176 mm
}
STEMS = {}
for d in ('fairlead-bearing-study', 'fairlead-stock-parts', 'fairlead-oval-study', 'fairlead-metal-retention-study'):
    for f in sorted((R / d).glob('**/*.st*p')): STEMS.setdefault(f.stem, f)
FIXED['FM10 Drum input gear 2302-0014-0060 / 60T'] = R / 'stock-drive-study/2302-0014-0060/2302-0014-0060.STEP'
FIXED['FM10 Drum hub 1301-0016-0012 / 12mm round / inner-face mounted'] = R / 'stock-drive-study/1301-0016-0012/1301-0016-0012 assembly.STEP'
def candidates(n):
    if n in FIXED: yield FIXED[n]; return
    if n.startswith('FM10 ') and (M10 / (n[5:] + '.step')).exists(): yield M10 / (n[5:] + '.step')   # R14: the module's own CAD first
    if n.startswith('FM10 ') and n[5:] in STEMS: yield STEMS[n[5:]]
    if n.startswith(('MOUNT ', 'ROUTE ')): yield R / 'mounts-rev11/step' / (n.replace('/', '-') + '.step')
    if n.startswith('FM10 '): yield M10 / (n[5:] + '.step')
    base = re.sub(r'_FM(6|9)$', '', n)
    for ext in ('.brep', '.step'):
        yield R / 'prototype-v43' / (base + ext)
        yield R / 'prototype-v43' / (n + ext)

ROTS = []
for perm in itertools.permutations(range(3)):
    for signs in itertools.product((1, -1), repeat=3):
        m = np.zeros((3, 3))
        for i, (j, s) in enumerate(zip(perm, signs)): m[i, j] = s
        if abs(np.linalg.det(m) - 1) < 1e-9: ROTS.append(m)

def mverts(p):
    return np.vstack([np.array(v['vertices'], float).reshape(-1, 3) for v in (p.get('visual_parts') or [p])])

def load(f):
    s = cq.Shape.importBrep(str(f)) if f.suffix == '.brep' else cq.importers.importStep(str(f)).val()
    return s

def register(src, model_pts):
    global MESH
    """Best S = (Rm, t) mapping source vertices onto the model mesh; exact bbox match required."""
    v, tri = src.tessellate(.2, .3); sp = np.array([q.toTuple() for q in v]); spf = sp.copy(); tri = np.array(tri)
    global SRCMESH_rot, MODEL_SAMPLE
    SRCMESH_rot = lambda Rm, t: trimesh.Trimesh(spf @ Rm.T + t, tri, process=False)
    MODEL_SAMPLE = MESH.sample(1500, return_index=False) if len(MESH.faces) else model_pts[:1500]
    if len(sp) > 4000: sp = sp[np.random.default_rng(0).choice(len(sp), 4000, replace=False)]
    mlo, mhi = model_pts.min(0), model_pts.max(0)
    from scipy.spatial import cKDTree
    best = None
    for Rm in ROTS:
        q = sp @ Rm.T; lo, hi = q.min(0), q.max(0)
        if np.abs((hi - lo) - (mhi - mlo)).max() > 1.0: continue
        t = (mlo + mhi) / 2 - (lo + hi) / 2
        d1 = trimesh.proximity.closest_point(MESH, (q + t)[:1500])[1]                  # source -> model surface
        d2 = trimesh.proximity.closest_point(SRCMESH_rot(Rm, t), MODEL_SAMPLE)[1]       # model -> source surface (catches flipped bores)
        score = max(np.percentile(d1, 99.5), np.percentile(d2, 99.5))
        if best is None or score < best[0]: best = (score, Rm, t)
    return best

# Round 8: registration depends only on the source file and the page mesh, so each result is cached (.cache/register.json)
import v44cache as VC
_rc_file = VC.CACHE / 'register.json'
_rc = json.loads(_rc_file.read_text()) if (VC.ENABLED and _rc_file.exists()) else {}
_script = VC.file_sha(__file__); _hits = 0
out, missing = {}, []
for row in PL:
    n = row['n']; p = MODEL.get(n)
    if p is None: missing.append((n, 'not in model')); continue
    f = next((c for c in candidates(n) if c.exists()), None)
    if f is None: missing.append((n, 'no source file')); continue
    _key = VC.sha(_script, n, str(f), VC.file_sha(f), p.get('visual_parts') or [p.get('vertices'), p.get('triangles')])
    if _key in _rc:
        _hits += 1
        if _rc[_key].get('missing'): missing.append((n, _rc[_key]['missing']))
        else: out[n] = _rc[_key]['out']
        continue
    try:
        vs, ts, k = [], [], 0
        for vis in (p.get('visual_parts') or [p]):
            a_ = np.array(vis['vertices'], float).reshape(-1, 3); vs.append(a_); ts.append(np.array(vis['triangles']).reshape(-1, 3) + k); k += len(a_)
        MESH = trimesh.Trimesh(np.vstack(vs), np.vstack(ts), process=False)
        best = register(load(f), mverts(p))
    except Exception as e:
        missing.append((n, f'load error {e}'[:80])); _rc[_key] = dict(missing=missing[-1][1]); continue
    if best is None: missing.append((n, f'size mismatch with {f.name}')); _rc[_key] = dict(missing=missing[-1][1]); continue
    score, Rm, t = best
    out[n] = dict(file=str(f.relative_to(R)).replace('\\', '/'), rot=Rm.tolist(), t=t.tolist(), fit95=round(float(score), 3),
                  status='exact' if score < 0.5 else 'approx')
    _rc[_key] = dict(out=out[n])
if VC.ENABLED:
    VC.CACHE.mkdir(parents=True, exist_ok=True); _rc_file.write_text(json.dumps(_rc))
print('register cache:', _hits, 'reused')
(R / 'print-v44-nano/sources.json').write_text(json.dumps(dict(sources=out, missing=missing), indent=1))
print('matched', len(out), 'exact', sum(v['status'] == 'exact' for v in out.values()), 'missing', len(missing))
for n, why in missing: print('  MISSING', n[:70], '|', why)
for n, v in out.items():
    if v['status'] != 'exact': print('  APPROX', n[:60], v['fit95'], v['file'][-50:])
