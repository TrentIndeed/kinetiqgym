"""Audit for build_voltra_fairlead.py: top-routing rope tangency and winding, sampled exact
sweep of the carrier against the removable mount/drive/drum, rope-envelope proximity.
Geometric model only. Run with few workers (AUDIT_WORKERS, default 4): each holds ~600 MB."""
from pathlib import Path
import gzip, json, math, os
import numpy as np
from scipy.optimize import root
import cadquery as cq
import trimesh

R = Path(__file__).resolve().parent.parent
P = R / 'workbench/public/stock-drive-study/voltra-module10-model.json.gz'
O = R / 'real-fairlead-revision/voltra-module10'
g = json.loads((O / 'geometry.json').read_text())
X0, ZP = g['pivot']; _, Y1, Z1 = g['sheave_center']; _, Y2, Z2 = g['roller_center']; RATIO = float(g['ratio'])
YD, ZD, ROPE = -62.5, 43.0, 3.175; RR = ROPE / 2
DR, SR, R2 = 23.5 + RR, 15.374 - 4 + RR, 8 + RR
WIDTH = (95.75 + RR + 3 * 3.3, 158.75 + 6.0 - RR)   # tracked zone: 3 hand-wound dead wraps at the anchor end, drum widened 6 mm
T1, T2 = Z1 - ZP, Z2 - ZP                     # sheave / roller centres in the carrier plane (y, t)

def tangent(a_deg):
    """Upper tangent from the drum section (ellipse in the tilted carrier plane) to the top of the sheave groove."""
    co = math.cos(math.radians(a_deg)); dc = np.array([YD, (ZD - ZP) / co]); S = np.array([Y1, T1])
    D = lambda al: dc + np.array([DR * math.cos(al), DR / co * math.sin(al)])
    def f(x):
        al, be = x; Q = S + SR * np.array([math.cos(be), math.sin(be)]); v = Q - D(al)
        return [v @ np.array([math.cos(al), co * math.sin(al)]), v @ np.array([math.cos(be), math.sin(be)])]
    best = None
    for g0 in [(math.pi / 2, math.pi / 2), (1.3, 1.7), (1.8, 1.4)]:
        r = root(f, g0)
        if r.success and np.linalg.norm(f(r.x)) < 1e-8:
            Dp = D(r.x[0]); Q = S + SR * np.array([math.cos(r.x[1]), math.sin(r.x[1])])
            if Q[1] > T1 and (best is None or Dp[1] > best[0][1]): best = (Dp, Q)
    if best is None: raise ValueError(f'no tangent at {a_deg}')
    return best
def station(a): return X0 + math.sin(math.radians(a)) * tangent(a)[0][1]
def world(pts, a_deg):
    a = math.radians(a_deg); return np.array([[X0 + math.sin(a) * t, y, ZP + math.cos(a) * t] for y, t in pts])
def arcp(c, r, p, q, ccw):
    a0 = math.atan2(p[1] - c[1], p[0] - c[0]); a1 = math.atan2(q[1] - c[1], q[0] - c[0])
    da = (a1 - a0) % (2 * math.pi) if ccw else -((a0 - a1) % (2 * math.pi))
    return [(c[0] + r * math.cos(t), c[1] + r * math.sin(t)) for t in np.linspace(a0, a0 + da, max(8, int(abs(da) * r / .8)))]
def line(p, q):
    p, q = np.array(p, float), np.array(q, float); n = max(2, int(np.linalg.norm(q - p) / .8) + 1)
    return [tuple(p + (q - p) * s) for s in np.linspace(0, 1, n)]

def winding_law():
    A = np.arange(-55, 55.01, 0.25); ST = np.array([station(a) for a in A]); o = np.argsort(ST)
    a_lo, a_hi = sorted([float(np.interp(WIDTH[1], ST[o], A[o])), float(np.interp(WIDTH[0], ST[o], A[o]))])
    step = 360 / RATIO; aa = np.arange(a_lo, a_hi - step + 1e-9, 0.25)
    pitch = np.abs(np.interp(aa + step, A, ST) - np.interp(aa, A, ST)); turns = (a_hi - a_lo) / step
    mono = bool(np.all(np.diff(ST) < 0) or np.all(np.diff(ST) > 0))
    return a_lo, a_hi, dict(ratio=f'1/{RATIO:.0f}', sweep_deg=[round(a_lo, 2), round(a_hi, 2)], drum_turns=round(turns, 2),
                            rope_capacity_m=round(turns * 2 * math.pi * DR / 1000, 3), pitch_mm=[round(pitch.min(), 3), round(pitch.max(), 3)],
                            monotonic=mono, tracking_pass=bool(mono and pitch.min() >= ROPE))

FIXED = ['Square back plate (4-screw enclosure mount)', '6809-2RS pivot bearing', 'KHK SW0.8-R1 worm, module 0.8, 1 start',
         'Worm shaft 6mm D (envelope)', 'Worm shaft 1601 bearing 0', 'Worm shaft 1601 bearing 1',
         'goBILDA 2303-1006-0020 20T D-bore worm-shaft gear', 'goBILDA 2303-4008-0020 20T shaft-2 gear', 'Owned 2302-0014-0060 60T shaft-2 gear',
         'Shaft 2 8mm REX (envelope)', 'Shaft 2 1611 bearing 0', 'Shaft 2 1611 bearing 1', 'Shaft 2 60T hub (owned, envelope)',
         'Shaft 2 bearing pedestal 0 (printed, base-mounted)', 'Shaft 2 bearing pedestal 1 (printed, base-mounted)']
BODY = 'Printed PA-CF carrier - 53T m0.8 worm-wheel ring + journal + sheave fork'
INTENDED_MOVING = {(BODY, 'KHK SW0.8-R1 worm, module 0.8, 1 start'), (BODY, '6809-2RS pivot bearing')}
INTENDED_FIXED = [('plate', 'bearing'), ('worm', 'Worm shaft 8mm'), ('D-bore worm-shaft', 'Worm shaft 6mm'), ('20T', 'Shaft 2 8mm'), ('60T shaft-2', 'Shaft 2 8mm'),
                  ('D-bore worm-shaft', '20T shaft-2'), ('Shaft 2 8mm', 'Shaft 2 1611'), ('Worm shaft 6mm', 'Worm shaft 1601'), ('Worm shaft 1601', 'worm'), ('worm', 'Worm shaft 6mm'),
                  ('Shaft 2 1611', 'pedestal'), ('Shaft 2 8mm', '60T hub'), ('60T shaft-2', '60T hub')]

def bb_near(a, b, m=3.0):
    A_, B_ = a.BoundingBox(), b.BoundingBox()
    return not (A_.xmax + m < B_.xmin or B_.xmax + m < A_.xmin or A_.ymax + m < B_.ymin or B_.ymax + m < A_.ymin or A_.zmax + m < B_.zmin or B_.zmax + m < A_.zmin)
def load_all():
    global rot, fixed, mesh, d
    ld = lambda n: cq.importers.importStep(str(O / (n + '.step'))).val()
    rot = {n: ld(n) for n in g['moving']}
    fixed = {n: ld(n) for n in FIXED}
    fixed['Drum (widened 6 mm)'] = cq.Shape.importBrep(str(O / 'Drum_V8_widened_6mm.brep'))
    for side in ('left', 'right'):
        fixed[f'6001 cartridge {side}'] = ld(f'6001 pillow block {side} (moved {"+5" if side == "left" else "+1"} mm)')
    d = json.loads(gzip.decompress(P.read_bytes()))
    mesh = {p['name']: trimesh.Trimesh(np.array(p['vertices']).reshape(-1, 3), np.array(p['triangles']).reshape(-1, 3), process=True) for p in d['parts']}
def static_checks():
    out, fx = [], list(fixed)
    for i in range(len(fx)):
        for j in range(i + 1, len(fx)):
            a, b = fx[i], fx[j]
            if not bb_near(fixed[a], fixed[b], .5): continue
            v = fixed[a].intersect(fixed[b]).Volume()
            if v > .05:
                ok = any((k1 in a and k2 in b) or (k1 in b and k2 in a) for k1, k2 in INTENDED_FIXED)
                out.append(dict(a=a, b=b, common_mm3=round(v, 3), classification='intended fit/mesh' if ok else 'CLASH'))
    return out

LIMITS = (-37.0, 37.0)
def _init(lim):
    global LIMITS
    LIMITS = lim
    if os.name == 'nt':
        import ctypes; ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
ROPE_ROT = [BODY, 'sheave axle 8 mm (bolt + nut envelope)', 'roller axle ISO7379 5 mm shoulder bolt']
ROPE_FIXED = FIXED + ['V43_PRINT_6001_cartridge_left', 'V43_PRINT_6001_cartridge_right', 'Printed_oval_ring_carrier', 'Fixed_bearing_housing', 'Rear_mount_plate_4mm']
def sweep(ang):
    if 'rot' not in globals(): load_all()
    a_lo, a_hi = LIMITS; C = (X0, 0, ZP); table, findings, patches = [], [], []
    Dp, Q = tangent(ang)
    sv = (Y1 - SR, T1); r_in = (Y2 + R2, T2); r_bot = (Y2, 0.0)
    local = line(Dp, Q) + arcp((Y1, T1), SR, Q, sv, True) + line(sv, r_in) + arcp((Y2, T2), R2, r_in, r_bot, False) + line(r_bot, (-240.0, 0.0))
    pts = world(local, ang); st = X0 + math.sin(math.radians(ang)) * Dp[1]
    inside = a_lo - 1e-6 <= ang <= a_hi + 1e-6
    findings.append(f'Drum departure station X={st:.2f} mm ({"inside" if inside else "outside"} the required sweep {a_lo:.1f}..{a_hi:.1f}°).')
    for rn, rs in rot.items():
        q = rs.rotate(C, (X0, 1, ZP), ang)
        for fn, fs in fixed.items():
            if (rn, fn) in INTENDED_MOVING or not bb_near(q, fs): continue
            common = q.intersect(fs); v = common.Volume(); gap = q.distance(fs) if v <= .05 else 0.0
            if v > .05 or gap < 1.0: table.append(dict(angle_deg=ang, a=rn, b=fn, overlap_mm3=round(v, 3), gap_mm=round(gap, 3), in_required_sweep=inside))
            if v > .05:
                findings.append(f'{rn} intersects {fn}: {v:.2f} mm³.'); vv, tt = common.tessellate(.2, .25)
                patches.append(dict(vertices=[c for p_ in vv for c in p_.toTuple()], triangles=[k for t in tt for k in t]))
    for n in ROPE_ROT + ROPE_FIXED:
        if n not in mesh: continue
        m = mesh[n]
        if n in ROPE_ROT: m = m.copy(); m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(ang), [0, 1, 0], C))
        _, dist, _ = trimesh.proximity.closest_point(m, pts)
        if (dist < RR - .05).any(): findings.append(f'Rope envelope within {RR:.2f} mm of {n}: {int((dist < RR - .05).sum())} sampled points, min {dist.min():.2f} mm.')
    return table, dict(angle_deg=ang, paths=[dict(name='Drum top → sheave → 625 stack → pivot axis → exit', points=np.round(pts, 4).tolist(), color=[.95, .55, .08])],
                       findings=findings, patches=patches, drum_station_mm=round(st, 4))

if __name__ == '__main__':
    import multiprocessing as mp
    a_lo, a_hi, winding = winding_law(); print(json.dumps(winding), flush=True)
    load_all(); static = static_checks(); print('static', json.dumps(static), flush=True)
    angles = list(range(-44, 45, 2)); part = O / 'audit_partial.jsonl'; done = {}
    if part.exists():
        for ln in part.read_text().splitlines():
            t, smp = json.loads(ln); done[smp['angle_deg']] = (t, smp)
    todo = [a for a in angles if a not in done]
    with mp.Pool(int(os.environ.get('AUDIT_WORKERS', 4)), initializer=_init, initargs=((a_lo, a_hi),)) as pool, part.open('a') as fh:
        for t, smp in pool.imap_unordered(sweep, todo):
            done[smp['angle_deg']] = (t, smp); fh.write(json.dumps([t, smp]) + '\n'); fh.flush()
            print('angle', smp['angle_deg'], 'findings', len(smp['findings']) - 1, flush=True)
    res = [done[a] for a in angles]; table = [r for t, _ in res for r in t]; samples = [s for _, s in res]
    clash = [t for t in table if t['overlap_mm3'] > .05 and t['in_required_sweep']]
    d['motion']['samples'] = samples
    d['motion']['note'] = (f'Carrier rotates about +Y through the pivot (Z {ZP}). Required sweep {a_lo:.1f}..{a_hi:.1f}°; samples to ±44°. '
                           'Rope tangent solved in the carrier plane (zero fleet angle). Worm/ring and gear meshes are envelopes shown static. Geometric model only.')
    d['audit'].update(winding=winding, static_fixed_overlaps=static,
                      sampled_sweep_module=dict(scope='45 poses, 2° steps, -44..44°. Exact BRep rotating-vs-fixed where bounding boxes come within 3 mm; intended meshes/fits excluded.',
                                         overlaps_in_required_sweep=len(clash), near_or_overlap=table))
    P.write_bytes(gzip.compress(json.dumps(d, separators=(',', ':')).encode(), mtime=0))
    (O / 'audit.json').write_text(json.dumps(dict(winding=winding, static_fixed_overlaps=static, sweep=table, overlaps_in_required_sweep=len(clash),
                                                 stations=[dict(angle_deg=s['angle_deg'], station_mm=s['drum_station_mm'], findings=s['findings']) for s in samples]), indent=2))
    print(json.dumps(dict(winding=winding, overlaps_in_required_sweep=len(clash), clashes=[c for c in clash][:20]), indent=1))
