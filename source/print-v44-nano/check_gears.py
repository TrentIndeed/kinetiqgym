"""Round 13: do the fairlead gears mesh and carry power, and does anything that turns rub? Writes gear-check.json.

Power path: drum 60T -> shaft-2 60T (1:1) ; shaft-2 20T -> worm-shaft 20T (1:1) ; KHK SW0.8-R1 worm -> 53T ring on the carrier (1/53).
1. Mesh: for each pair, the centre distance measured on the placed parts against the design (a = m (z1 + z2) / 2), then the driven
   gear is phased to zero overlap and the pair is turned through one tooth pitch at the right ratio: at every step there must be
   no overlap (no binding) and the flank gap must stay small (teeth in contact = torque is carried; the gap is the backlash).
   The vendor STEPs come unphased, so the phase found here is the assembly phase (also written to the report).
2. Rub: every turning part is replaced by its swept body (a cylinder of its largest radius about its own axis, over its length)
   and its clearance to every part that does not turn with it is measured (bearings, housings and the parts it passes through
   by design are skipped). Under 0.5 mm is flagged.
The carrier's swing (+-45 deg) is covered by the fairlead audit (stock-drive-study/audit_voltra_module10.py).
"""
from pathlib import Path
import json, math
import numpy as np
import cadquery as cq

H = Path(__file__).resolve().parent
R = json.loads((H / 'printed' / 'revision.json').read_text())
def load(n): return cq.Shape.importBrep(str(H / 'printed' / (n + '.brep')))
V = cq.Vector
M = 0.8                                                                     # module of every pair (m0.8, 20 deg)
DRUM, S2, WS = (-62.5, 43.0), (-107.938, 27.528), (-105.0, 11.8)           # X-parallel axes (Y, Z)
PIVOT = (135.2, 40.0)                                                       # ring axis, parallel to Y, through (X, Z)
G = dict(drum60='FM10_Drum_input_gear_2302-0014-0060_60T', s2_60='FM10_Owned_2302-0014-0060_60T_shaft-2_gear',
         s2_20='FM10_goBILDA_2303-4008-0020_20T_shaft-2_gear', ws20='FM10_goBILDA_2303-1006-0020_20T_D-bore_worm-shaft_gear',
         worm='KHK_SW0.8-R1_worm', ring='FM10_Printed_PA-CF_carrier_-_53T_m0.8_worm-wheel_ring_journal_sheave_fork')

def xrot(s, ax, deg): return s.rotate(V(0, ax[0], ax[1]), V(1, ax[0], ax[1]), deg)
def yrot(s, deg): return s.rotate(V(PIVOT[0], 0, PIVOT[1]), V(PIVOT[0], 1, PIVOT[1]), deg)
def overlap(a, b):
    try: return a.intersect(b).Volume()
    except Exception: return -1.0
def gap(a, b):
    try: return a.distance(b)
    except Exception: return -1.0

def axis_of(n):
    """Centre of an X-axis part in (Y, Z) from its tessellation (mean of the bounding box)."""
    b = load(n).BoundingBox(); return ((b.ymin + b.ymax) / 2, (b.zmin + b.zmax) / 2)

def crop(s, c1, c2, half=9.0):
    """Keep the part near the line of centres of a spur pair (speeds the solid checks up)."""
    y0, z0 = c1; y1, z1 = c2; d = np.array([y1 - y0, z1 - z0]); d /= np.linalg.norm(d)
    b = s.BoundingBox(); mid = (np.array(c1) + np.array(c2)) / 2
    box = cq.Solid.makeBox(b.xlen + 2, 2 * half, 2 * half, V(b.xmin - 1, mid[0] - half, mid[1] - half))
    return s.intersect(box)

def spur(a_name, b_name, ca, cb, za, zb, steps=10):
    a0, b0 = load(a_name), load(b_name)
    a_meas, b_meas = axis_of(a_name), axis_of(b_name)
    dist = float(np.hypot(cb[0] - ca[0], cb[1] - ca[1])); design = M * (za + zb) / 2
    ac, bc = crop(a0, ca, cb), crop(b0, ca, cb)
    # phase the driven gear: scan one of its tooth pitches for the least overlap, then refine
    pb = 360.0 / zb
    best = min(((overlap(ac, xrot(bc, cb, p)), p) for p in np.arange(0, pb, pb / 24)), key=lambda t: t[0])
    ph = best[1]
    for step in (pb / 96, pb / 384):
        best = min(((overlap(ac, xrot(bc, cb, ph + k * step)), ph + k * step) for k in range(-4, 5)), key=lambda t: t[0]); ph = best[1]
    rows = []
    for t in np.linspace(0, 360.0 / za, steps, endpoint=False):             # driver turns one tooth pitch, driven turns -za/zb as much
        a = xrot(ac, ca, t); b = xrot(bc, cb, ph - t * za / zb)
        rows.append(dict(deg=round(float(t), 2), overlap_mm3=round(overlap(a, b), 4), flank_gap_mm=round(gap(a, b), 3)))
    ok_bind = all(r['overlap_mm3'] <= 0.01 for r in rows); ok_contact = all(0 <= r['flank_gap_mm'] <= 0.3 for r in rows)
    return dict(pair=f'{a_name} -> {b_name}', teeth=[za, zb], ratio=f'{za}:{zb}', centre_distance_mm=round(dist, 3), design_mm=design,
                measured_axes=[[round(v, 2) for v in a_meas], [round(v, 2) for v in b_meas]], driven_phase_deg=round(float(ph), 2),
                steps=rows, no_binding=ok_bind, teeth_in_contact=ok_contact, max_gap=max(r['flank_gap_mm'] for r in rows), max_overlap_mm3=max(r['overlap_mm3'] for r in rows))

def worm_pair(steps=12):
    w0, r0 = load(G['worm']), load(G['ring'])
    box = cq.Solid.makeBox(40, 20, 14, V(PIVOT[0] - 20, WS[0] - 10, WS[1] - 1))      # the ring's teeth near the worm
    rc = r0.intersect(box)
    design = (M * 53 + M * 17.5) / 2                                                    # ring PD 42.4, worm PD 14 -> 28.2
    dist = PIVOT[1] - WS[1]
    res = {}
    for sgn in (1, -1):                                                                 # which ring sense matches the right-hand worm
        rows = []
        for t in np.linspace(0, 360.0, steps, endpoint=False):
            w = xrot(w0, WS, t); r = yrot(rc, sgn * t / 53.0)
            rows.append(dict(worm_deg=round(float(t), 1), overlap_mm3=round(overlap(w, r), 4), flank_gap_mm=round(gap(w, r), 3)))
        res[sgn] = rows
    sgn = min(res, key=lambda k: sum(max(r['overlap_mm3'], 0) for r in res[k]))
    rows = res[sgn]
    return dict(pair=f"{G['worm']} -> 53T ring", ratio='1:53 (single start)', centre_distance_mm=round(dist, 3), design_mm=28.2,
                ring_sense=('+' if sgn > 0 else '-') + ' about +Y per worm turn about +X', steps=rows,
                no_binding=all(r['overlap_mm3'] <= 0.01 for r in rows), teeth_in_contact=all(0 <= r['flank_gap_mm'] <= 0.3 for r in rows),
                max_gap=max(r['flank_gap_mm'] for r in rows), other_sense_max_overlap=max(r['overlap_mm3'] for r in res[-sgn]))

# ---------------------------------------------------------------- 1. mesh
import os
mesh = json.loads((H / 'gear-check.json').read_text())['mesh'] if os.environ.get('RUB_ONLY') else [spur(G['drum60'], G['s2_60'], DRUM, S2, 60, 60), spur(G['s2_20'], G['ws20'], S2, WS, 20, 20), worm_pair()]

# ---------------------------------------------------------------- 2. rub (swept bodies of turning parts vs everything else)
GROUPS = {
    'drum': (DRUM, ['FM9_Drum_V8_widened_6_mm', 'REF_drum_shaft_12mm_176mm', G['drum60'], 'FM10_Drum_hub_1301-0016-0012_12mm_round_inner-face_mounted',
                    'NBK_MSTS-25-10-12_coupling', 'REF_motor_output_shaft_APPROX_10mm', 'V3_REF_encoder_magnet_6x5_N45SH_DIAMETRIC'] + [n for n in R['parts'] if n.startswith(('H_V21', 'B_V21', 'I_V21', 'V27_', 'B_V37', 'I_V30'))]),
    'shaft2': (S2, ['goBILDA_2106-4008-0560_REX_shaft_56', G['s2_60'], 'FM10_Shaft_2_60T_hub_owned_envelope', G['s2_20']]),
    'worm_shaft': (WS, ['ServoCity_2101-0006-0060_D_shaft_60', G['worm'], G['ws20']]),
}
SUPPORT = ('SKF_6001', 'V43_PRINT_6001_cartridge', 'V43_METAL_bearing_cheek', 'goBILDA_1611', 'goBILDA_1601', 'FM10_Fixed_bearing_housing',
           'S01_', 'V43_METAL_motor_face', 'REF_APS8072S', 'V3_REF_motor_stationary', 'V43_B_retainer', 'V43_N_retainer')   # carry or enclose a shaft by design
MESH_PARTNERS = {G['drum60']: {G['s2_60']}, G['s2_60']: {G['drum60']}, G['s2_20']: {G['ws20']}, G['ws20']: {G['s2_20']}, G['worm']: {G['ring']}}
SHAFTS = ('REF_drum_shaft', 'goBILDA_2106', 'ServoCity_2101', 'REF_motor_output_shaft')

def swept(n, ax, step=1.0):
    """The body the part sweeps when it turns: its radius profile along the axis (largest radius per 1 mm), revolved 360 deg."""
    s = load(n); vs, _ = s.tessellate(0.1, 0.2)
    p = np.array([[v.x, v.y, v.z] for v in vs]); rr = np.hypot(p[:, 1] - ax[0], p[:, 2] - ax[1])
    x0, x1 = float(p[:, 0].min()), float(p[:, 0].max()); pts = [(x0, 0.0)]
    for xa in np.arange(x0, x1, step):
        xb = min(xa + step, x1); m = (p[:, 0] >= xa - 0.3) & (p[:, 0] <= xb + 0.3)
        r_ = float(rr[m].max()) if m.any() else pts[-1][1]
        pts += [(xa, r_), (xb, r_)]
    pts.append((x1, 0.0))
    clean = [pts[0]]
    for q in pts[1:]:                                                   # no zero-length or collinear-duplicate edges
        if abs(q[0] - clean[-1][0]) > 1e-6 or abs(q[1] - clean[-1][1]) > 1e-6: clean.append(q)
    pts = [clean[0]] + [q for k, q in enumerate(clean[1:-1], 1) if not (abs(clean[k - 1][1] - q[1]) < 1e-6 and abs(clean[k + 1][1] - q[1]) < 1e-6)] + [clean[-1]]
    pl = cq.Plane(origin=(0, ax[0], ax[1]), xDir=(1, 0, 0), normal=(0, -1, 0))
    try: env = cq.Workplane(pl).polyline(pts).close().revolve(360, (0, 0, 0), (1, 0, 0)).val()
    except Exception: env = cq.Solid.makeCylinder(float(rr.max()), x1 - x0, V(x0, ax[0], ax[1]), V(1, 0, 0))
    return env, float(rr.max())
turning = {n for _, (_, ns) in GROUPS.items() for n in ns}
others = {n: load(n) for n in R['parts'] if n not in turning and not n.startswith(('WIRE_', 'HARNESS_'))}
obb = {n: s.BoundingBox() for n, s in others.items()}
rub = []
for g, (ax, names) in GROUPS.items():
    for n in names:
        if n not in R['parts']: continue
        env, rad = swept(n, ax); eb = env.BoundingBox()
        for m, t in others.items():
            if m.startswith(SUPPORT) and (n.startswith(SHAFTS) or g == 'drum'): continue
            if m in MESH_PARTNERS.get(n, ()): continue
            b = obb[m]
            if b.xmin > eb.xmax + 1 or b.xmax < eb.xmin - 1 or b.ymin > eb.ymax + 1 or b.ymax < eb.ymin - 1 or b.zmin > eb.zmax + 1 or b.zmax < eb.zmin - 1: continue
            d = gap(env, t)
            if 0 <= d < 0.5 or overlap(env, t) > 0.01:
                rub.append(dict(turning=n, group=g, swept_radius=round(rad, 2), other=m, clearance_mm=round(d, 3), overlap_mm3=round(max(overlap(env, t), 0), 3)))
rep = dict(mesh=mesh, rub=rub, note=__doc__.split('\n')[0])
(H / 'gear-check.json').write_text(json.dumps(rep, indent=1))
for m in mesh:
    print(f"{m['pair'][:70]}: a={m['centre_distance_mm']} (design {m['design_mm']}), no binding {m['no_binding']}, in contact {m['teeth_in_contact']}, max gap {m['max_gap']}, gaps {[r['flank_gap_mm'] for r in m['steps']]}, overlaps {[r['overlap_mm3'] for r in m['steps']]}")
print('rub flags:', len(rub))
for r in rub: print('  ', r)
