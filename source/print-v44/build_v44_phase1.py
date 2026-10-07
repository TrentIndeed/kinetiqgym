"""V44 phase 1: every current live-demo part as real CAD in the workbench source format (like print-v42).

world solid = M (S(source) - c): M and c from the page (demo-placements-rev12.json, design layout rev 12), S from register_sources.py.
Parts without a CAD source (battery, BMS, allowances, perfboard footprints) are rebuilt as solids from the demo
mesh (boxes, or sewn triangles). Stale sources (motor face plate, anchor rope) are trimmed to the demo's bounds.
Changes against the demo, per the V44 decisions: the rigid Ruland envelope is replaced by the user's flexible
coupler from V42, and the base placeholder is left out (a new chassis replaces it in phase 3).
Writes {cnc,printed}/revision.json + <name>.step/.brep + hardware.csv. Engineering preview: no release checks yet.
"""
from pathlib import Path
import json, sys, gzip, re, csv, shutil
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeSolid
from OCP.gp import gp_Pnt
from OCP.TopoDS import TopoDS
from OCP.TopAbs import TopAbs_SHELL
from OCP.TopExp import TopExp_Explorer

HERE = Path(__file__).resolve().parent; R = HERE.parent
PL = json.loads((HERE / 'demo-placements-rev12.json').read_text(encoding='utf-8-sig'))['rows']
SRC = json.loads((HERE / 'sources.json').read_text())['sources']
MODEL = {p['name']: p for p in json.loads(gzip.decompress((R / 'workbench/public/stock-battery-fit/editor-model-tp2700.json.gz').read_bytes()))['parts']}
EXCLUDE = {'TRIAL_base_placeholder': 'replaced by the new V44 chassis (phase 3)',
           'V43_REF_Ruland_MCLX_12_10_F_ENVELOPE': 'replaced by the user-confirmed flexible coupler (V42)'}
TRIM = ('V43_METAL_motor_face_4mm', 'V27_REF_anchor_cable')      # source older than the demo: trim to the demo bounds
TRIM_SRC = {n: R / 'prototype-v43' / (n + '.brep') for n in TRIM}

def safe(n):
    s = re.sub(r'[^A-Za-z0-9_.-]+', '_', n.replace('×', 'x').replace('—', '-')).strip('_.')
    return re.sub(r'_+', '_', s)[:96]

def world_matrix(row):
    el = row['m']; A = np.array([[el[j * 4 + i] for j in range(4)] for i in range(4)])     # three.js column-major
    T = np.eye(4); T[:3, 3] = -np.array(row['c'])
    return A @ T

def apply(shape, A):
    """Rigid transform. The page's matrices are rounded to 6 decimals: re-orthogonalise the rotation (SVD) first."""
    from OCP.gp import gp_Trsf
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    U, _, Vt = np.linalg.svd(A[:3, :3]); Rm = U @ Vt
    if np.linalg.det(Rm) < 0: raise ValueError('mirror transform')
    t = A[:3, 3]; tr = gp_Trsf()
    tr.SetValues(*[float(x) for x in (Rm[0, 0], Rm[0, 1], Rm[0, 2], t[0], Rm[1, 0], Rm[1, 1], Rm[1, 2], t[1], Rm[2, 0], Rm[2, 1], Rm[2, 2], t[2])])
    out = cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, tr, True).Shape())
    fch = sys.modules.get('fchist_rec')                                # FreeCAD history (FCHIST=1): record the move
    if fch: fch.tag_xform(out, shape, [[Rm[i, 0], Rm[i, 1], Rm[i, 2], t[i]] for i in range(3)])
    return out

def box_from(b):
    return cq.Solid.makeBox(b[3] - b[0], b[4] - b[1], b[5] - b[2], cq.Vector(b[0], b[1], b[2]))

def sew(vis):
    v = np.array(vis['vertices'], float).reshape(-1, 3); t = np.array(vis['triangles']).reshape(-1, 3)
    if len(t) == 12: return box_from([*v.min(0), *v.max(0)])
    sw = BRepBuilderAPI_Sewing(1e-3)
    for a, b, c in t:
        pa, pb, pc = (gp_Pnt(*map(float, v[k])) for k in (a, b, c))
        if pa.Distance(pb) < 1e-6 or pb.Distance(pc) < 1e-6 or pa.Distance(pc) < 1e-6: continue
        poly = BRepBuilderAPI_MakePolygon(pa, pb, pc, True); sw.Add(BRepBuilderAPI_MakeFace(poly.Wire()).Face())
    sw.Perform(); ex = TopExp_Explorer(sw.SewedShape(), TopAbs_SHELL); solids = []
    while ex.More():
        ms = BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(ex.Current()))
        if ms.IsDone():
            s = cq.Solid(ms.Solid())
            if s.isValid() and abs(s.Volume()) > 1e-3: solids.append(s if s.Volume() > 0 else cq.Solid(s.wrapped.Reversed()))
        ex.Next()
    return cq.Compound.makeCompound(solids) if solids else box_from([*v.min(0), *v.max(0)])

VEND = R / 'rectangular-body-study/vendor'
COMPOSITE = {'TRIAL_Pololu5571': VEND / 'pololu.brep', 'TRIAL_CAN_headers': VEND / 'waveshare-can.brep', 'TRIAL_Teensy': VEND / 'teensy40.brep'}   # vendor board + perfboard box

def register_vendor(shape, visuals):
    """Place a vendor-frame solid on the demo's board mesh: best of 24 axis rotations by surface distance."""
    import itertools, trimesh
    vs, ts, k = [], [], 0
    for vis in visuals:
        a = np.array(vis['vertices'], float).reshape(-1, 3); vs.append(a); ts.append(np.array(vis['triangles']).reshape(-1, 3) + k); k += len(a)
    mesh = trimesh.Trimesh(np.vstack(vs), np.vstack(ts), process=False); mlo, mhi = mesh.bounds
    v, _ = shape.tessellate(.2, .3); sp = np.array([q.toTuple() for q in v])
    sp = sp[np.random.default_rng(0).choice(len(sp), min(1500, len(sp)), replace=False)]
    best = None
    for perm in itertools.permutations(range(3)):
        for sg in itertools.product((1, -1), repeat=3):
            Rm = np.zeros((3, 3))
            for i, (j, s) in enumerate(zip(perm, sg)): Rm[i, j] = s
            if np.linalg.det(Rm) < .5: continue
            q = sp @ Rm.T; lo, hi = q.min(0), q.max(0)
            if np.abs((hi - lo) - (mhi - mlo)).max() > 1.5: continue
            t = (mlo + mhi) / 2 - (lo + hi) / 2
            sc = np.percentile(trimesh.proximity.closest_point(mesh, q + t)[1], 95)
            if best is None or sc < best[0]: best = (sc, Rm, t)
    if best is None: raise ValueError('vendor board does not match the demo mesh')
    A = np.eye(4); A[:3, :3] = best[1]; A[:3, 3] = best[2]
    return apply(shape, A), best[0]

def model_shape(n):
    """Shape in the demo's model frame."""
    p = MODEL[n]
    if n in COMPOSITE:
        vis = p.get('visual_parts') or [p]
        boxes = [sew(v) for v in vis if len(v['triangles']) == 36]
        try:
            board, fit = register_vendor(cq.Shape.importBrep(str(COMPOSITE[n])), [v for v in vis if len(v['triangles']) != 36])
        except ValueError:                                           # vendor board does not match the demo's drawing-based mesh
            return cq.Compound.makeCompound([sew(v) for v in vis]), 'rebuilt from the demo mesh (vendor board did not match)'
        return cq.Compound.makeCompound([board, *boxes]), f'CAD: vendor {COMPOSITE[n].name} (fit {fit:.2f} mm) + perfboard footprint rebuilt from the demo'
    if n in SRC and (SRC[n]['status'] == 'exact' or n == 'TRIAL_Pi4_upright'):     # Pi: demo box includes a cooler allowance
        s = SRC[n]; f = R / s['file']
        shp = cq.Shape.importBrep(str(f)) if f.suffix == '.brep' else cq.importers.importStep(str(f)).val()
        Rm = np.array(s['rot']); A = np.eye(4); A[:3, :3] = Rm; A[:3, 3] = s['t']
        return apply(shp, A), 'CAD: ' + s['file']
    if n in TRIM:
        shp = cq.Shape.importBrep(str(TRIM_SRC[n])); return shp.intersect(box_from(p['bounds'])), 'CAD trimmed to the demo edit: ' + str(TRIM_SRC[n].relative_to(R))
    parts = [sew(v) for v in (p.get('visual_parts') or [p])]
    return (parts[0] if len(parts) == 1 else cq.Compound.makeCompound(parts)), 'rebuilt from the demo mesh (no CAD source)'

def group_of(n, row):
    g = row['g']; a = row['asm'] or ''
    if n.startswith('FM10 ') or n.startswith('FM9 Drum') : return 'fairlead' if not n.startswith(('FM9 Drum', 'FM10 Drum')) else 'drivetrain'
    if n.startswith('MOUNT '): return 'mounts'
    if n.startswith('ROUTE ') or g == 'reserve': return 'wiring'
    if a in ('assembly:battery', 'assembly:bms', 'assembly:TRIAL_protection_and_connections') or n == 'RESERVE_battery_connections': return 'power'
    if n == 'V43_PRINT_motor_side_handle': return 'handle'
    if a in ('assembly:drivetrain',): return 'drivetrain'
    return 'electronics'

def kind_of(n, g):
    if g == 'wiring': return 'reference'
    if re.match(r'(FM10 )?(B_|N_|W_|I_|V43_B_|V43_N_|V43_W_|B_V|I_V)', n) or re.search(r'M\d+x\d+|_nut|_washer|Axle_M4', n): return 'fastener'
    if 'spacer' in n.lower(): return 'spacer'
    if re.search(r'6001_2RS|6809|625ZZ|6808|1611|1601', n): return 'bearing_reference'
    if n.startswith(('REF_', 'V3_REF', 'V43_REF', 'CATALOG', 'RESERVE')): return 'reference'
    if 'SUPPLIER' in n or n.startswith(('TRIAL_Pi4', 'TRIAL_driver_fan', 'TRIAL_Waveshare', 'TRIAL_Pololu', 'TRIAL_Teensy', 'TRIAL_CAN')): return 'electronics_reference'
    return 'part'

def manufacture_of(n, row):
    if n.startswith('MOUNT '): return re.search(r'Material: ([^.]+)', MODEL[n].get('description', '')).group(1) if 'Material:' in MODEL[n].get('description', '') else 'PRINT'
    if 'PRINT' in n or 'Printed' in n: return 'PRINT'
    if 'METAL' in n or 'CNC' in n: return 'CNC / cut metal'
    return ''

def main():
    for mode in ('cnc', 'printed'):
        (HERE / mode).mkdir(exist_ok=True)
    names, colors, meta, hardware, report, used = [], {}, {}, [], [], set()
    rows = [r for r in PL if r['n'] not in EXCLUDE]
    coupler = dict(n='REF_coupler_APPROX_10_to_12mm', g='drivetrain', asm='assembly:drivetrain')
    import v44cache as C
    script = C.file_sha(__file__); hits = 0
    def part_key(n, row):
        if n == coupler['n']: return C.sha(script, n, C.file_sha(R / 'print-v42/printed/REF_coupler_APPROX_10_to_12mm.step'))
        files = []
        if n in COMPOSITE: files.append(COMPOSITE[n])
        if n in SRC: files.append(R / SRC[n]['file'])
        if n in TRIM: files.append(TRIM_SRC[n])
        return C.sha(script, n, row['m'], row['c'], row['min'], row['max'], MODEL.get(n), SRC.get(n), [C.file_sha(f) for f in files])
    for row in rows + [coupler]:
        n = row['n']
        v44 = safe(n)
        while v44 in used: v44 += '_x'
        used.add(v44)
        key = part_key(n, row); rec = C.part_get(v44, key)
        if n == coupler['n']:
            p = {'color': [0.72, 0.74, 0.78], 'description': 'USER CONFIRMED flexible aluminium coupling OD25 L30, bores 10/12. Replaces the rigid Ruland envelope of the demo.'}
        else:
            p = MODEL[n]
        if rec:                                                          # unchanged part: reuse the cached solid
            C.part_restore(v44, [HERE / 'cnc', HERE / 'printed']); origin, dev, valid = rec['origin'], rec['dev'], rec['valid']; hits += 1
        else:
            if n == coupler['n']:
                shp = cq.importers.importStep(str(R / 'print-v42/printed/REF_coupler_APPROX_10_to_12mm.step')).val(); origin = 'CAD: print-v42 (user-confirmed flexible coupler OD25 x L30, bores 10/12)'
            else:
                shp, origin = model_shape(n); shp = apply(shp, world_matrix(row))
            if not shp.isValid(): shp = shp.fix()
            bb = shp.BoundingBox(); dev = None
            if n != coupler['n']:
                dev = float(np.abs(np.array([bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax]) - np.array(row['min'] + row['max'])).max())
            for mode in ('cnc', 'printed'):
                shp.exportStep(str(HERE / mode / (v44 + '.step'))); shp.exportBrep(str(HERE / mode / (v44 + '.brep')))
            valid = shp.isValid()
            C.part_put(v44, key, HERE / 'printed' / (v44 + '.brep'), HERE / 'printed' / (v44 + '.step'), dict(origin=origin, dev=dev, valid=valid))
        g = group_of(n, row) if n != coupler['n'] else 'drivetrain'; k = kind_of(n, g)
        names.append(v44); colors[v44] = [round(float(c), 3) for c in (p.get('color') or [.7, .7, .7])[:3]]
        meta[v44] = dict(group=g, kind=k, note=(p.get('description') or '')[:400], manufacture=manufacture_of(n, row) if n != coupler['n'] else 'Buy',
                         demo_name=n, source=origin)
        if k in ('fastener', 'spacer', 'bearing_reference'): hardware.append(dict(part=v44, group=g, kind=k, size=n, source='', note=(p.get('description') or '')[:160]))
        report.append(dict(name=v44, demo=n, origin=origin, bbox_dev_mm=None if dev is None else round(dev, 3), valid=valid))
        print(f'{len(names):3d} {v44[:60]:60s} dev={dev if dev is None else round(dev, 3)} {"cached " if rec else ""}{origin[:40]}', flush=True)
    print(f'part cache: {hits} of {len(names)} parts reused', flush=True)
    views = dict(complete=names, open=names,
                 drivetrain=[n for n in names if meta[n]['group'] in ('drivetrain', 'mounts')],
                 fairlead_rack=[n for n in names if meta[n]['group'] in ('fairlead',) or meta[n]['demo_name'].startswith(('FM9 Drum', 'REF_drum_shaft', 'FM10 Drum'))],
                 handle=[n for n in names if meta[n]['group'] in ('handle',) or 'motor_face' in n or 'motor_gusset' in n],
                 wiring=[n for n in names if meta[n]['group'] in ('electronics', 'power', 'wiring', 'mounts')])
    rev = dict(mode='', parts=names, colors=colors, meta=meta, joints=[], hardware=hardware, views=views, expected_interference=[],
               insert_reference=json.loads((R / 'print-v42/printed/revision.json').read_text())['insert_reference'],
               status='V44 phase 1 engineering preview: every live-demo part (design layout rev 12, 176 mm drum shaft) as real CAD. New base, enclosure and rack puck not built yet; no release checks.',
               engineering_preview=True, parent_revision='V42', source_layout='workbench/public/stock-battery-fit/design-layout-rev12.json',
               excluded=EXCLUDE, printer=dict(model='Bambu Lab P2S', build_volume_mm=[256, 256, 256]))
    for mode in ('cnc', 'printed'):
        (HERE / mode / 'revision.json').write_text(json.dumps(dict(rev, mode=mode), indent=1))
        with open(HERE / mode / 'hardware.csv', 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=['part', 'group', 'kind', 'size', 'source', 'note']); w.writeheader(); w.writerows(hardware)
    (HERE / 'phase1-report.json').write_text(json.dumps(report, indent=1))
    bad = [r for r in report if r['bbox_dev_mm'] is not None and r['bbox_dev_mm'] > 0.5 or not r['valid']]
    print('parts', len(names), 'bbox deviations > 0.5 mm or invalid:', len(bad))
    for r in bad: print('  CHECK', r)

if __name__ == '__main__':
    main()
