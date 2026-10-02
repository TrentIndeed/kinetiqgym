"""Voltra-style fairlead module, revision 10: gear train moved to the free right end of the drum shaft (old 2GT pulley slot), clear of the motor coupler.

Rope leaves the drum top, wraps the sheave above the cable-lead ring, drops into the ring
bore, turns under a 2x625 roller inside the bore and leaves along the pivot axis (Z 28)
through the frame. Rotating: front sheave arm + printed PA-CF 50T worm-wheel ring + rear
hub/journal in two 6809 bearings seated in the square frame. The worm and its shaft sit on
lugs at the bottom of the frame. Drive: new drum 80T -> owned 60T on shaft 2 -> 20T ->
40T on the worm shaft -> module-1 worm -> 50T ring. 80/60 x 20/40 x 1/50 = 1/75.
Ring and worm have real tooth geometry (involute ring with worm-lead helix and throat,
swept ZA worm thread). Mechanism review only, not a manufacturing release.
Rev 12 (September 27, drum shaft cut to 176 mm, ODrive 24 mm closer): the shaft-2 60T hub goes inboard of the 60T, the
outer 1611 pedestal moves 10 mm in (1 mm from the 60T face) and is trimmed to Y -99.1 at the back (ODrive bracket post),
and the 56 mm REX shaft moves 5 mm in (X 158..214).
V44 fix L4 (September 28): the round rear mount plate with 4 disc lugs is replaced by a 6 mm square exit frame the size of the
square back plate inside the enclosure. The frame clamps the front wall to the back plate with 4 corner M4 through 8 mm spacers;
the exit swivel housing screws into M3 heat-set inserts in the frame (its loose nuts are gone). The swivel stack moves 2.5 mm out.
Round 13 (September 30): hard stops - a lug on the carrier journal and two blocks on the back plate face stop the carrier at
+-48.4 deg (needed +-45.4). Exit rollers are the user's uxcell U625ZZ nylon U-groove pulleys (5 x 20 x 7): axles re-spaced so the
rope runs in both grooves with 0.45 mm play and cannot slip out between the flanges; 2 mm spacers.
"""
from pathlib import Path
import gzip, json, math
import numpy as np
import cadquery as cq
from scipy.spatial import ConvexHull

R = Path(__file__).resolve().parent.parent
SD = R / 'stock-drive-study'
P = R / 'workbench/public/stock-drive-study'
O = R / 'real-fairlead-revision/voltra-module10'
O.mkdir(exist_ok=True)
src = json.loads(gzip.decompress((P / 'supported-wheel-model.json.gz').read_bytes()))

WIDEN = 6.0                                   # drum barrel widened toward +X (right pillow block moves with it)
DEAD = 3; DEAD_PITCH = 3.3                    # hand-wound dead wraps at the anchor (left) end, outside the tracked zone
TRACK = (95.75 + 1.5875 + DEAD * DEAD_PITCH, 158.75 + WIDEN - 1.5875)
X0 = round(sum(TRACK) / 2, 3)                 # pivot centred on the tracked zone
YD, ZD, RD = -62.5, 43.0, 23.5
ROPE = 3.175; RR = ROPE / 2
OLD_Z0 = 62.708376112296975
ZP = 40.0                                     # pivot raised so the worm and its gear sit above the 5 mm base (costs rope capacity)
ZT = ZD + RD + RR                             # rope centre leaving the drum top
SR = 15.374 - 4 + RR                          # saved sheave: rope-centre radius
Y1, Z1 = -105.0, ZT - SR                      # sheave centre: as close to the drum as clearance allows
YV = Y1 - SR                                  # vertical rope drop
R2 = 8 + RR                                   # 625 roller rope-centre radius
Y2, Z2 = YV - R2, ZP + R2
# Rotating stack along -Y: ring teeth, then the journal back through the frame plate.
RING = (-101.0, -109.0)                       # 48T ring, mid-plane directly under the sheave centre (Y1)
JOURNAL = (-109.0, -135.8)                    # R14: 0.5 mm clear of the exit's rear inner-race retainer (exit 1.5 mm forward)
PLATE = (-137.0, -120.5)                      # R4-1: square back plate runs to the enclosure face (flush in the wall opening)
FRAME = (-120.5, -129.5)                      # 9 mm back plate right behind the rope drop
BRG = (-122.5, -129.5)                        # 6809-2RS 45x58x7 seat, 2 mm front lip
M = 0.8; PA = math.radians(20)                # ring and worm: module 0.8 (KHK SW0.8-R1 worm)
RING_N = 53; RING_PD = RING_N * M; RING_TIP = RING_PD / 2 + M - 0.2; RING_BORE = 18.5
BACKLASH = 0.40                               # printed PA-CF running clearance: circular backlash at the pitch circle (mm)
WORM_PD, WORM_OD, WORM_THREAD, WORM_HUB, WORM_HUB_R, WORM_BORE = 14.0, 15.6, 18.0, 12.0, 6.0, 3.0
A_W = (RING_PD + WORM_PD) / 2                 # 29
YW, ZW = sum(RING) / 2, ZP - A_W              # worm axis (parallel to X)
BOLT_R, BOLT_A = 21.5, []
WORM_BRG = (X0 - WORM_THREAD / 2 - 7.2, X0 + WORM_THREAD / 2 + WORM_HUB + 1)   # 6 mm D-shaft bearings: between the 24T and the worm, and past the worm hub                      # ring is part of the printed carrier: no bolt pattern
# Drive: owned drum 60T / owned 60T on shaft 2 (48 mm), 20T / 20T D-bore on the worm shaft (16 mm)
D = np.array([YD, ZD]); W = np.array([YW, ZW]); dd = np.linalg.norm(W - D)
a_ = (48.0**2 - 16.0**2 + dd**2) / (2 * dd); h_ = math.sqrt(48.0**2 - a_**2); n_ = np.array([-(W - D)[1], (W - D)[0]]) / dd
S2 = max((D + a_ * (W - D) / dd + h_ * n_, D + a_ * (W - D) / dd - h_ * n_), key=lambda s: s[1])   # higher solution
PB = 5.0                                      # pillow blocks moved this far toward the drum (hub bolt heads limit)
# Rev 10: the drum 60T sat inside the Ruland motor coupler (X 14-59). The whole gear train now uses the free
# right end of the drum shaft: the old 2GT belt pulley slot between the right pillow block and the encoder magnet.
GEAR_X = (196.5, 202.5)                       # drum 60T plane: 1.7 mm past the right retainer bolt ends (X 194.8), pillow block is only its 4 mm flange here
SRC_GEAR_X0 = 38.0                            # drum 60T face in the saved supported-wheel model
BC_X = (172.0, 178.0)                         # 20T/20T teeth, just right of the square frame; hubs point back toward the frame
S2_BRG = (180.0, 203.5)                       # shaft-2 1611 bearings in printed base pedestals: between the 20T and the 60T hub, and 1 mm past the 60T (rev 12)
S2_HUB_X = GEAR_X[0] - 10                     # rev 12: 60T hub inboard (X 186.5..196.5), between pedestal 0 and the 60T
S2_X = (158.0, 214.0)                         # rev 12: goBILDA 2106-4008-0560 56 mm REX

rows, solids, moving = [], {}, []
def cy(r, h, p, axis=(0, 1, 0)): return cq.Solid.makeCylinder(r, h, cq.Vector(*p), cq.Vector(*axis))
def tube(ro, ri, h, p, axis=(0, 1, 0)): return cy(ro, h, p, axis).cut(cy(ri, h, p, axis))
def box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))
def step(sku, i=0): return cq.importers.importStep(str(next((SD / sku).glob('*.STEP')))).solids().vals()[i]
def add(name, s, col, group, role, rotate=False):
    assert s.isValid(), name
    solids[name] = s; s.exportStep(str(O / (name + '.step')))
    v, t = s.tessellate(.08, .15); a = np.array([q.toTuple() for q in v])
    rows.append(dict(name=name, vertices=np.round(a, 4).ravel().tolist(), triangles=np.array(t).ravel().tolist(),
                     bounds=[*a.min(0), *a.max(0)], color=col, group=group, role=role))
    if rotate: moving.append(name)
def x_gear(s, yz, x0=None, xmax=None):  # vendor MOD0.8 gear (axis X): face at x0, or far face at xmax
    b = s.BoundingBox(); dx = (xmax - b.xmax) if xmax is not None else (x0 - b.xmin)
    return s.moved(cq.Location(cq.Vector(dx, yz[0] - (b.ymin + b.ymax) / 2, yz[1] - (b.zmin + b.zmax) / 2)))
def pinion(sku):  # REX pinion: teeth at vendor +Z -> +X; hub points -X. Location keeps the vendor solid valid.
    return step(sku).moved(cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), 90))

# ---- Tooth geometry ----
def worm_solid():
    """ZA worm (KHK SW0.8-R1 envelope), axial module 0.8, single start, thread along +Z from z=0, hub on the +Z end."""
    p = math.pi * M; r_p = WORM_PD / 2; r_t = r_p + M; r_r = r_p - 1.25 * M
    wt = p / 2 - 2 * math.tan(PA) * M; wr = p / 2 + 2 * math.tan(PA) * 1.25 * M
    helix = cq.Wire.makeHelix(p, WORM_THREAD + 2 * p, r_r - 0.3, center=cq.Vector(0, 0, -p))
    thread = (cq.Workplane('XZ', origin=(0, 0, -p)).polyline([(r_r - 0.3, -wr / 2), (r_t, -wt / 2), (r_t, wt / 2), (r_r - 0.3, wr / 2)])
              .close().sweep(cq.Workplane().add(helix), isFrenet=True).val())
    thread = thread.intersect(cq.Solid.makeCylinder(r_t + 1, WORM_THREAD, cq.Vector(0, 0, 0)))
    w = cq.Solid.makeCylinder(r_r + 0.02, WORM_THREAD, cq.Vector(0, 0, 0)).fuse(thread)
    w = w.fuse(cq.Solid.makeCylinder(WORM_HUB_R, WORM_HUB, cq.Vector(0, 0, WORM_THREAD)))
    return w.cut(cq.Solid.makeCylinder(WORM_BORE, WORM_THREAD + WORM_HUB, cq.Vector(0, 0, 0))).clean()
def involute(N, pts=12):
    rp = N * M / 2; rb = rp * math.cos(PA); ra = rp + M - 0.2; rf = rp - 1.25 * M
    tmax = math.sqrt((ra / rb) ** 2 - 1); half = math.pi / (2 * N) + (math.tan(PA) - PA) - BACKLASH / (2 * rp); out = []   # thinned for backlash
    for k in range(N):
        c = 2 * math.pi * k / N
        side = [(rb * math.sqrt(1 + t * t), half - (t - math.atan(t))) for t in np.linspace(0, tmax, pts)]
        out += [(rf, c - math.pi / N)] + [(max(r, rf), c - a) for r, a in side] + [(max(r, rf), c + a) for r, a in reversed(side)]
    return [(r * math.cos(a), r * math.sin(a)) for r, a in out]
def ring_solid():
    """Worm wheel along +Z (face 8): involute teeth, helix = worm lead angle, throated to the worm root."""
    face = RING[0] - RING[1]; lead_angle = math.atan(M / WORM_PD)
    g = cq.Workplane('XY').polyline(involute(RING_N)).close().twistExtrude(face, math.degrees(face * math.tan(lead_angle) / (RING_PD / 2))).val()
    g = g.cut(cq.Solid.makeTorus(A_W, A_W - RING_TIP, cq.Vector(0, 0, face / 2), cq.Vector(0, 0, 1)))
    g = g.cut(cq.Solid.makeCylinder(RING_BORE, face, cq.Vector(0, 0, 0)))
    for a in BOLT_A:
        t = math.radians(a); g = g.cut(cq.Solid.makeCylinder(1.7, face, cq.Vector(BOLT_R * math.cos(t), -BOLT_R * math.sin(t), 0)))   # z_to_y maps +y to -Z
    return g.clean()
def z_to_y(s, y0):   # part built along +Z from 0 -> along +Y from y0, centred on the pivot axis
    return s.rotate((0, 0, 0), (1, 0, 0), -90).translate((X0, y0, ZP))

def fillet_cap(s):
    """Round 5: oval retaining cap - 2.5 mm on its four corners, 0.8 mm on the outer front edges (the back face seats on the housing)."""
    b = s.BoundingBox()
    corners = [e for e in s.Edges() if e.geomType() == 'LINE' and abs((e.endPoint() - e.startPoint()).normalized().y) > 0.99
               and min(abs(e.Center().x - b.xmin), abs(e.Center().x - b.xmax)) < 0.01 and min(abs(e.Center().z - b.zmin), abs(e.Center().z - b.zmax)) < 0.01]
    try:
        t = s.fillet(2.5, corners)
        if t.isValid(): s = t
    except Exception:
        pass
    front = [f for f in s.Faces() if f.geomType() == 'PLANE' and f.normalAt().y < -0.99 and abs(f.Center().y - b.ymin) < 0.01]
    for e in [e for f in front for e in f.outerWire().Edges()]:
        try:
            t = s.fillet(0.8, [e])
            if t.isValid(): s = t
        except Exception:
            pass
    return s

# ---- Context ----
EXIT = ('6808_sealed_bearing', 'Carrier_M3', 'Fixed_bearing_housing', 'Front_outer_race', 'Rear_mount_plate',
        'Hub_retainer', 'Rear_inner_race', 'Owned_exit_625', 'JY_MARINE', 'Oval_clamp', 'Printed_oval',
        'Stock_M5_spacer', 'ISO7379_5x25_M4_shoulder', 'Axle_M4')
EXIT_SHIFT = (X0 - 127.25, -136.0 - 0.5 - (-126.5) + 3.5 - 1.5, ZP - OLD_Z0)     # R4-1: housing on the plate face; R14: 1.5 mm forward
EXIT_FWD = 1.5                                                                       # R14: the housing gets 1.5 mm more at its back
EXIT_CAD = ('Fixed_bearing_housing', 'Rear_inner_race_retainer', 'Hub_retainer_M3x8')   # R14: rebuilt as CAD below (thicker back, countersunk screws)
EXIT_DROP = EXIT_CAD + ('Rear_mount_plate', 'Carrier_M3_nut', 'Printed_oval_ring_carrier',     # plate replaces the frame; ring carrier rebuilt filleted below
             'Owned_exit_625', 'ISO7379_5x25_M4_shoulder', 'Stock_M5_spacer', 'Axle_M4')   # round 13: rebuilt for the U625ZZ pulleys
OLD_AXLES = {}                                                                          # round 13: the saved exit axles (world, after EXIT_SHIFT)
EXIT_BOX = {}
for p in src['parts']:
    if p['name'].startswith(EXIT_CAD):
        a = np.array(p['vertices']).reshape(-1, 3) + EXIT_SHIFT; EXIT_BOX[p['name']] = (a.min(0), a.max(0), tuple(p['color']), p['group'], p.get('role') or '')
    if p['name'].startswith('ISO7379_5x25_M4_shoulder'):
        a = np.array(p['vertices']).reshape(-1, 3) + EXIT_SHIFT; OLD_AXLES[p['name']] = (a.min(0), a.max(0))
    if p['name'] == 'Drum_V8_smooth_single_layer':
        continue                                                   # replaced by the widened drum below
    if p['group'] == 'context' and 'right' in p['name'] and p['name'].startswith(('H_V21', 'B_V21', 'I_V21')):
        q = dict(p); a = np.array(p['vertices']).reshape(-1, 3) + (WIDEN, 0, 0); q['vertices'] = a.ravel().tolist(); q['bounds'] = [*a.min(0), *a.max(0)]
        q['role'] = (p.get('role') or '') + f' Moved {WIDEN:+.0f} mm with the widened drum.'; rows.append(q); continue
    if p['name'].startswith(('Drum hub', 'Drum input gear')) or (p['group'] == 'context' and ('left' in p['name'] or 'right' in p['name']) and p['name'].startswith(('V43_REF_6001', 'V43_METAL_bearing_cheek', 'REV_M3x16', 'V43_N_retainer', 'V43_B_retainer'))):
        q = dict(p); dx = (GEAR_X[0] - SRC_GEAR_X0) if p['name'].startswith(('Drum hub', 'Drum input gear')) else (-PB + WIDEN) if 'right' in p['name'] else PB
        a = np.array(p['vertices']).reshape(-1, 3) + (dx, 0, 0); q['vertices'] = a.ravel().tolist(); q['bounds'] = [*a.min(0), *a.max(0)]
        q['role'] = (p.get('role') or '') + f' Moved {dx:+.0f} mm in X with its pillow block / drum gear.'; rows.append(q)
    elif p['group'] == 'context':
        rows.append(p)
    elif p['name'].startswith(EXIT_DROP):
        continue
    elif p['name'].startswith('Printed_oval_retaining_cap'):                      # round 5: rebuilt from its STEP with rounded edges
        a = np.array(p['vertices']).reshape(-1, 3) + EXIT_SHIFT
        cap = fillet_cap(cq.importers.importStep(str(R / 'fairlead-oval-study' / (p['name'] + '.step'))).val())
        cb = cap.BoundingBox(); cap = cap.translate(cq.Vector(*(a.min(0) - np.array([cb.xmin, cb.ymin, cb.zmin]))))
        add(p['name'], cap, tuple(p['color']), p['group'], (p.get('role') or '') + ' Existing exit swivel part, moved unchanged behind the frame and down to the new axis; '
            'corners rounded 2.5 mm and the front edges 0.8 mm (round 5).')
    elif p['name'].startswith(EXIT):
        q = dict(p); a = np.array(p['vertices']).reshape(-1, 3) + EXIT_SHIFT
        q['vertices'] = a.ravel().tolist(); q['bounds'] = [*a.min(0), *a.max(0)]
        q['role'] = (p.get('role') or '') + ' Existing exit swivel, moved unchanged behind the frame and down to the new axis.'
        rows.append(q)
# R14 (October 1): the exit swivel moves 1.5 mm forward. The carrier's rope-turn roller swept 0.7 mm into the rear inner-race retainer
# and the hub screws' hex heads stood 3 mm into the path of the roller and fork cheeks (the swivel turns on its own, the carrier
# swings +-45 deg). The bearing housing gets 1.5 mm more at its back (still on the plate face, no loose spacer); the hub screws are
# countersunk M3 x 8 (ISO 10642), flush in the 2 mm retainer.
def exit_step(name):
    s = cq.importers.importStep(str(R / 'fairlead-bearing-study' / (name + '.step'))).val(); b = s.BoundingBox()
    lo, hi = EXIT_BOX[name][:2]
    assert np.allclose([b.xlen, b.ylen, b.zlen], hi - lo, atol=0.3), (name, [b.xlen, b.ylen, b.zlen], hi - lo)
    return s.translate(cq.Vector(*(lo - np.array([b.xmin, b.ymin, b.zmin]))))
hs = exit_step('Fixed_bearing_housing'); yb = hs.BoundingBox().ymax
back = [f for f in hs.Faces() if f.geomType() == 'PLANE' and f.normalAt().y > 0.99 and abs(f.Center().y - yb) < 1e-3]
hs = hs.fuse(*[cq.Solid.extrudeLinear(f.outerWire(), f.innerWires(), cq.Vector(0, EXIT_FWD, 0)) for f in back]).clean()
_, _, col, grp, role = EXIT_BOX['Fixed_bearing_housing']
add('Fixed_bearing_housing', hs, col, grp, role + ' Existing exit swivel housing, 1.5 mm thicker at its back (R14: the swivel moved 1.5 mm forward, the housing still sits on the plate face).')
ret = exit_step('Rear_inner_race_retainer_2mm'); yr = ret.BoundingBox().ymax
for i in (1, 2, 3):
    n = f'Hub_retainer_M3x8_{i}'; lo, hi = EXIT_BOX[n][:2]; cx, cz = (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2
    ret = ret.cut(cq.Solid.makeCone(3.15, 1.6, 1.55, cq.Vector(cx, yr + 0.01, cz), cq.Vector(0, -1, 0))).cut(cy(1.7, 4.0, (cx, yr - 3.0, cz), (0, 1, 0)))
    scr = cq.Solid.makeCone(3.0, 1.5, 1.5, cq.Vector(cx, yr, cz), cq.Vector(0, -1, 0)).fuse(cy(1.5, 8.0, (cx, yr - 8.0, cz), (0, 1, 0)))
    add(n, scr.clean(), EXIT_BOX[n][2], EXIT_BOX[n][3], 'R14: countersunk M3 x 8 (ISO 10642), head flush in the rear inner-race retainer (was a hex head 3 mm proud); same nut.')
_, _, col, grp, role = EXIT_BOX['Rear_inner_race_retainer_2mm']
add('Rear_inner_race_retainer_2mm', ret.clean(), col, grp, role + ' R14: 3 countersinks for the flush hub screws.')
for side in ('left', 'right'):
    dxp = (-PB + WIDEN) if side == 'right' else PB
    s = cq.Shape.importBrep(str(R / 'prototype-v43' / f'V43_PRINT_6001_cartridge_{side}.brep')).translate((dxp, 0, 0))
    add(f'6001 pillow block {side} (moved {dxp:+.0f} mm)', s, (.55, .6, .64), 'context', 'Saved 6001 cartridge; left moved 5 mm toward the drum, right follows the 6 mm wider drum (net +1 mm, about 1 mm from the hub bolt heads to the bearing cheek).')
add('Drum V8 widened 6 mm', cq.Shape.importBrep(str(O / 'Drum_V8_widened_6mm.brep')), (.87, .66, .25), 'context',
    'Saved smooth single-layer drum with a 6 mm barrel section added before the right flange (same section as the barrel). 3 dead wraps hand-wound at the anchor end; the fairlead tracks the rest.')
# Motor and battery from the saved packing base model, for orientation only.
ed = json.loads(gzip.decompress((R / 'workbench/public/stock-battery-fit/editor-model-tp2700.json.gz').read_bytes()))
for p in ed['parts']:
    if p['name'] in ('REF_APS8072S_motor_body_APPROX_80x82', 'CATALOG_stock-battery-fit'):
        q = dict(p); q['group'] = 'context'; q['color'] = (.35, .36, .4) if 'motor' in p['name'] else (.3, .45, .3)
        q['role'] = 'Orientation reference from the saved packing base model (motor end = gear end).'; rows.append(q)

# ---- Rotating assembly ----
sh = cq.Shape.importBrep(str(R / 'prototype-v43/V9_CNC_single_guide_sheave_D31.brep'))
tor = next(f for f in sh.Faces() if f.geomType() == 'TORUS')._geomAdaptor().Torus().Axis().Location()
sh = sh.translate((-tor.X(), -tor.Y(), -tor.Z())).rotate((0, 0, 0), (0, 1, 0), 26.5).translate((X0, Y1, Z1))
sh = sh.cut(cy(4.25, 40, (X0 - 20, Y1, Z1), (1, 0, 0)))              # round 8: 688ZZ (8 x 16 x 5, same pockets as 625ZZ), bore opened to 8.5
add('Top sheave (saved D31 CNC design)', sh, (.72, .74, .78), 'proposal', 'Above the ring; rope from the drum top wraps over it and drops into the ring bore. Runs on 2 x 688ZZ (8 x 16 x 5) on the 8 mm axle; bore between them opened to 8.5 (round 8).', True)
for i in range(2):
    add(f'Roller 625ZZ {i}', tube(8, 2.5, 5, (X0 - 5 + 5 * i, Y2, Z2), (1, 0, 0)), (.6, .64, .7), 'proposal', '625ZZ inside the ring bore; turns the rope onto the pivot axis.', True)
def yz_hull(x0, x1, pts):
    pts = np.array(pts); hv = ConvexHull(pts).vertices
    return cq.Workplane(cq.Plane(origin=(x0, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))).polyline([tuple(pts[k]) for k in hv]).close().extrude(x1 - x0).val()
def circ(y, z, r, n=40): return [(y + r * math.cos(t), z + r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, n, endpoint=False)]
# One printed PA-CF rotating body, Voltra style: worm-wheel ring + 45 mm journal + a fork of two
# cheeks rising straight up to the sheave. The cheeks are anchored into the ring centre and tied by
# a cross-web under the sheave; the sheave runs on an 8 mm axle supported by both cheeks.
# Journal: 43 mm where it passes over the worm (clears the worm top), 45 mm from there back into the 6809.
J_STEP = -113.5
body = z_to_y(ring_solid(), RING[1]).fuse(cy(19.8, JOURNAL[0] - J_STEP, (X0, J_STEP, ZP))).fuse(cy(22.5, J_STEP - JOURNAL[1], (X0, JOURNAL[1], ZP)))
body = body.cut(cy(19, J_STEP - JOURNAL[1], (X0, JOURNAL[1], ZP)))                       # rope / roller passage behind the worm; solid neck over it
fork_pts = circ(Y1, Z1, 8) + circ(Y2, Z2, 6.5) + [(RING[0], ZP - 16.0), (RING[1], ZP - 16.0), (RING[1], ZP + 24), (RING[0], ZP + 24)]   # cheeks anchor inside the ring root, above the worm
for x0, x1 in ((X0 + 6.5, X0 + 11), (X0 - 11, X0 - 6.5)):
    ch = yz_hull(x0, x1, fork_pts)
    # Behind the plate face the cheeks must stay inside the journal (r22.5) so they clear the plate bore.
    ch = ch.intersect(box(X0 - 30, X0 + 30, FRAME[0] + 1.0, 0, -60, 120)).fuse(ch.intersect(cy(22.4, 40, (X0, FRAME[0] - 39.99, ZP))))
    body = body.fuse(ch)
body = body.fuse(box(X0 - 11, X0 + 11, -113.0, -104.0, 34.0, 39.5))                      # middle cross-web, in front of the rope drop
body = body.cut(cy(4.1, 30, (X0 - 15, Y1, Z1), (1, 0, 0))).cut(cy(2.6, 30, (X0 - 15, Y2, Z2), (1, 0, 0)))
# round 8: the sheave-axle head and nut sit in the top of the ring rim (never meshes with the worm): pockets outside the cheeks
body = body.cut(cy(7.0, 4.8, (X0 - 15.8, Y1, Z1), (1, 0, 0))).cut(cy(7.0, 4.8, (X0 + 11.0, Y1, Z1), (1, 0, 0)))
body = body.cut(box(X0 - 6.5, X0 + 6.5, RING[1] - .01, RING[0] + .01, ZP + 17, ZP + 30))       # ring top slot between the fork cheeks: the sheave turns in it
body = body.cut(box(X0 - 4, X0 + 4, -121.0, RING[1] + .01, ZP + 17, ZP + 33))                  # hub top slot: the rope drops straight down through it
# Front centre plate across the ring bore (Voltra's centre piece) with a window for the sheave, rope and roller.
ctr = cy(19.6, 2, (X0, RING[0] - 2, ZP)).cut(box(X0 - 7.5, X0 + 7.5, RING[0] - 2.01, RING[0] + .01, ZP - 7, ZP + 40))
for a in (45, 135, 225, 315):
    t = math.radians(a); ctr = ctr.cut(cy(1.7, 2, (X0 + 14 * math.cos(t), RING[0] - 2, ZP + 14 * math.sin(t))))
body = body.fuse(ctr)
body = body.cut(cy(4.1, 30, (X0 - 15, Y1, Z1), (1, 0, 0))).cut(cy(7.0, 4.8, (X0 - 15.8, Y1, Z1), (1, 0, 0))).cut(cy(7.0, 4.8, (X0 + 11.0, Y1, Z1), (1, 0, 0)))   # round 8: axle bore + head/nut pockets also through the centre plate
# Round 13: hard stops. The carrier must turn +-45.4 deg (the tracked rope zone); a lug on the journal (bottom, between the ring and the
# back plate face) meets two blocks on the plate face at +-48.4 deg (3 deg margin). Angles from the bottom (-Z) toward +X, about the pivot.
STOP_REQ, STOP_MARGIN, LUG_HALF, BLK_HALF = 45.4, 3.0, 7.0, 6.0
STOP_AT = STOP_REQ + STOP_MARGIN
LUG_Y = (-119.5, -114.5)
def sector(r0, r1, a0, a1, y0, y1, n=24):
    ang = np.radians(np.linspace(a0, a1, n))
    pts = [(X0 + r1 * math.sin(t), ZP - r1 * math.cos(t)) for t in ang] + [(X0 + r0 * math.sin(t), ZP - r0 * math.cos(t)) for t in ang[::-1]]
    return cq.Workplane('XZ', origin=(0, y1, 0)).polyline(pts).close().extrude(y1 - y0).val()
body = body.fuse(sector(22.0, 29.0, -LUG_HALF, LUG_HALF, *LUG_Y))
# R14: the sheave ran 666 mm3 into the neck and journal below the ring slot. Pocket: the sheave's swept disc + 1 mm radial, 0.75 mm each
# side (narrower than the 13 mm between the fork cheeks, so the cheeks and the axle bosses are untouched).
_sb = sh.BoundingBox(); SH_R, SH_W = _sb.zlen / 2, _sb.xlen
body = body.cut(cy(SH_R + 1.0, SH_W + 1.5, (X0 - (SH_W + 1.5) / 2, Y1, Z1), (1, 0, 0)))
body = body.cut(cy(4.8, 3.3, (X0 - 14.15, Y2, Z2), (1, 0, 0)))                         # R14: pocket for the roller-axle head (it dipped into the journal wall)
add('Printed PA-CF carrier - 53T m0.8 worm-wheel ring + journal + sheave fork', body.clean(), (.18, .2, .23), 'drive',
    'Round 13: stop lug on the journal (bottom) - the plate blocks stop it at +-48.4 deg. One printed rotating body. Ring: module 0.8, 53T, top slotted for the rope drop (the worm only ever engages the bottom), involute with the worm lead angle, throated to the worm. Journal runs in one 6809 in the back plate. Fork cheeks 4.5 mm, anchored into the ring centre, cross-web under the sheave; sheave on an 8 mm axle supported both sides.', True)
ax = cy(6.5, 3, (X0 - 14, Y1, Z1), (1, 0, 0)).fuse(cy(4, 25, (X0 - 11, Y1, Z1), (1, 0, 0))).fuse(cy(6.5, 4, (X0 + 11, Y1, Z1), (1, 0, 0)))
add('sheave axle 8 mm (bolt + nut envelope)', ax, (.64, .68, .7), 'support', 'Through both fork cheeks (double shear); head and nut sit in pockets in the top of the ring rim (round 8). The sheave runs on 2 x 688ZZ.', True)
ax = cy(4.5, 3, (X0 - 14, Y2, Z2), (1, 0, 0)).fuse(cy(2.5, 25, (X0 - 11, Y2, Z2), (1, 0, 0))).fuse(cy(2, 3, (X0 + 11, Y2, Z2), (1, 0, 0)))
add('roller axle ISO7379 5 mm shoulder bolt', ax, (.64, .68, .7), 'support', 'Nominal shoulder-bolt envelope.', True)

# ---- Stationary: small back plate (4-screw enclosure mount), 6809 seat, worm brackets and housing ----
FX = (X0 - 35, X0 + 35); FZ = (0.5, ZP + 30)                                                # 70 wide x 69.5 tall, all above the base (Z 0)
frame = cq.Workplane('XY').box(FX[1] - FX[0], PLATE[1] - PLATE[0], 74.0 - FZ[0], centered=False).translate((FX[0], PLATE[0], FZ[0])) \
    .edges('|Y').fillet(6.0).faces('<Y').edges().fillet(1.5).val().cut(cy(24, PLATE[1] - PLATE[0], (X0, PLATE[0], ZP)))   # R4-1: one clean plate, curved edges
frame = frame.cut(cy(29, BRG[0] - PLATE[0], (X0, PLATE[0] - 0.01, ZP)))                        # 6809 seat, open to the front (fits from the front)
# R4-7: no corner holes (the plate bolts down to the bottom plate; the exit housing screws into inserts below)
# Worm housing (Voltra's box under the ring): open on top where the ring teeth come down; floor at Z -5.
housing = box(X0 - 17, X0 + 21, -113.0, -97.0, 0.5, ZW + 5).cut(cy(9, 50, (X0 - 25, YW, ZW), (1, 0, 0)))
housing = housing.cut(box(X0 - 17, X0 + 21, -121, -90, ZW + 1.5, ZW + 6))
frame = frame.fuse(housing).fuse(box(X0 + 17, X0 + 21, FRAME[0] - .5, -113.0, 0.5, ZW))    # tie the housing back to the plate
for x in WORM_BRG:
    frame = frame.fuse(box(x, x + 5, FRAME[0] - 1, YW + 7, 0.5, ZW)).cut(cy(7, 5, (x, YW, ZW), (1, 0, 0)))   # open cradles
# R4-1: the exit housing sits on the plate face: 4 x M3 heat-set inserts (diamond r 29), 2 x M4 inserts from below.
for dx, dz in ((29, 0), (-29, 0), (0, 29), (0, -29)):
    frame = frame.cut(cy(2.0, 6.0, (X0 + dx, PLATE[0] - 0.01, ZP + dz)))
for x in (110.0, 160.0):
    frame = frame.cut(cq.Solid.makeCylinder(2.8, 7.0, cq.Vector(x, (PLATE[0] + PLATE[1]) / 2, FZ[0] - 0.01), cq.Vector(0, 0, 1)))
for sgn in (1, -1):                                                                          # round 13: the two stop blocks on the plate face
    a_in = STOP_AT + LUG_HALF; a_out = a_in + 2 * BLK_HALF
    frame = frame.fuse(sector(23.5, 30.5, min(sgn * a_in, sgn * a_out), max(sgn * a_in, sgn * a_out), FRAME[0] - 0.5, LUG_Y[1] - 0.5))   # 0.9 mm from shaft 2's swept body
add('Square back plate (4-screw enclosure mount)', frame.clean(), (.42, .5, .45), 'support',
    'Round 13: two stop blocks on its face stop the carrier lug at +-48.4 deg. 70 x 73.5 plate from the enclosure face (Y -137) to Y -120.5, curved edges (R4-1): the carrier journal and rope-turn roller turn inside its front 7.5 mm, the 6809 seat is open to the front, the exit housing screws onto its face (4 x M3 inserts). 2 x M4 down into the bottom plate. Whole module lifts out.')
# R4-2: printed oval ring carrier (exit swivel), rebuilt from its STEP with filleted outer edges and trimmed 1.2 mm at the back
# (1 mm clear of the carrier journal end). The STEP frame is offset from the saved model: model = step + (-5.75, 16.5, -11.29).
rc = cq.importers.importStep(str(R / 'fairlead-oval-study/Printed_oval_ring_carrier.step')).val()
edges = [e for f in rc.Faces() if f.geomType() == 'PLANE' and abs(f.normalAt().y) > 0.99 for e in f.outerWire().Edges()]
for e in edges:
    try:
        t = rc.fillet(1.2, [e])
        if t.isValid(): rc = t
    except Exception:
        pass
rc = rc.translate(cq.Vector(-5.75 + EXIT_SHIFT[0], 16.5 + EXIT_SHIFT[1], -11.29 + EXIT_SHIFT[2]))
rc = rc.cut(box(X0 - 60, X0 + 60, JOURNAL[1] - 0.8, 0.0, -50, 150))                    # >= 0.8 mm clear of the journal end
# Round 13: the user's exit rollers are uxcell U625ZZ nylon U-groove pulleys, 5 x 20 x 7, groove about 4.5 wide x 1.25 deep (bottom d17.5).
# The saved axles were spaced for plain 625ZZ (d16): the pulleys would touch each other. New spacing: groove bottoms 0.45 mm more than the
# rope apart, so the rope runs in both grooves and the flanges (1.1 mm apart) keep it from slipping out sideways. 2 mm spacers (7 mm wide).
U_OD, U_W, U_BORE, U_GD, U_GW = 20.0, 7.0, 5.0, 17.5, 4.5
PLAY = 0.45
AX_HALF = (U_GD + ROPE + PLAY) / 2
old = sorted(OLD_AXLES.values(), key=lambda t: t[0][2])
AY = float((old[0][0][1] + old[0][1][1]) / 2)                                           # axle Y (unchanged)
AXZ_OLD = [float((a[0][2] + a[1][2]) / 2) for a in old]
AXZ = [ZP - AX_HALF, ZP + AX_HALF]
HX0, SH0, SH1, TX1 = float(old[0][0][0]), float(old[0][0][0]) + 4.0, float(old[0][0][0]) + 29.0, float(old[0][1][0])   # head (k 4, on the recess floor) / 25 shoulder / M4 thread
WALL_IN = (X0 - 5.5, X0 + 5.5)                                                           # carrier inner faces (11 mm between them, as before)
for zo in AXZ_OLD:                                                                       # fill the old axle holes, drill the new ones
    rc = rc.fuse(cy(2.65, WALL_IN[0] - (SH0 + 0.1), (SH0 + 0.1, AY, zo), (1, 0, 0))).fuse(cy(2.65, (SH1 - 0.6) - WALL_IN[1], (WALL_IN[1], AY, zo), (1, 0, 0)))
for z in AXZ:
    rc = rc.cut(cy(2.6, TX1 - HX0 + 2, (HX0 - 1, AY, z), (1, 0, 0)))                      # d5.2 for the 5 mm shoulder (printed)
    rc = rc.cut(cy(U_OD / 2 + 0.8, WALL_IN[1] - WALL_IN[0] - 1.0, (WALL_IN[0] + 0.5, AY, z), (1, 0, 0)))   # 0.8 mm round the pulley
    rc = rc.cut(cy(4.3, WALL_IN[1] - WALL_IN[0], (WALL_IN[0], AY, z), (1, 0, 0)))                         # 0.3 mm round the 2 mm spacers
add('Printed_oval_ring_carrier (filleted)', rc if rc.isValid() else rc.fix(), (.2, .22, .25), 'support',
    'Exit swivel ring carrier (saved oval study), outer edges filleted 1.2 mm (R4-2), kept 0.8 mm clear of the carrier journal end. '
    'Round 13: axle holes moved for the U625ZZ pulleys (Z %.2f / %.2f), pulley pocket opened to d21.6.' % tuple(AXZ))
def u_pulley(x0, y, z):
    b = cy(U_OD / 2, U_W, (x0, y, z), (1, 0, 0))
    rg = U_GW / 2; rc_ = U_GD / 2 + rg                                                   # U groove: a torus cut, bottom at d17.5
    b = b.cut(cq.Solid.makeTorus(rc_, rg, cq.Vector(x0 + U_W / 2, y, z), cq.Vector(1, 0, 0)))
    return b.cut(cy(U_BORE / 2, U_W, (x0, y, z), (1, 0, 0)))
for k, z in enumerate(AXZ):
    add(f'Exit_pulley_U625ZZ_{k}', u_pulley(X0 - U_W / 2, AY, z), (.93, .93, .9), 'support',
        'uxcell U625ZZ nylon U-groove pulley bearing 5 x 20 x 7 (GCr15, ABEC3): the rope runs in its groove, between the two pulleys.', True)
    axle = cy(4.5, SH0 - HX0, (HX0, AY, z), (1, 0, 0)).fuse(cy(2.5, SH1 - SH0, (SH0, AY, z), (1, 0, 0))).fuse(cy(2.0, TX1 - SH1, (SH1, AY, z), (1, 0, 0)))
    add(f'Exit_axle_ISO7379_5x25_M4_shoulder_{k}', axle, (.64, .68, .7), 'support', 'ISO 7379 shoulder bolt, 5 mm x 25 shoulder, M4 thread: the pulley axle through both carrier walls.')
    for j, x in enumerate((WALL_IN[0], X0 + U_W / 2)):
        add(f'Exit_axle_M5_spacer_2mm_{k}_{j}', tube(4.0, 2.6, 2.0, (x, AY, z), (1, 0, 0)), (.7, .72, .74), 'support', 'M5 x 2 mm spacer between the carrier wall and the pulley inner race.')
    add(f'Exit_axle_M4_washer_{k}', tube(4.5, 2.6, 0.8, (SH1, AY, z), (1, 0, 0)), (.7, .72, .74), 'support', 'Washer under the axle nut.')
    nut = cq.Workplane('YZ', origin=(SH1 + 0.8, 0, 0)).center(AY, z).polygon(6, 7.0 / math.cos(math.pi / 6)).extrude(3.2).val().cut(cy(2.0, 3.2, (SH1 + 0.8, AY, z), (1, 0, 0)))
    add(f'Exit_axle_M4_nut_{k}', nut, (.7, .72, .74), 'support', 'M4 nut on the axle thread.')
add('6809-2RS pivot bearing', tube(29, 22.5, 7, (X0, BRG[1], ZP)), (.82, .83, .85), 'support', '45x58x7 sealed bearing (Amazon uxcell 6809-2RS) carrying the ring journal.')
wm = worm_solid().rotate((0, 0, 0), (0, 1, 0), 90).translate((X0 - WORM_THREAD / 2, YW, ZW))   # thread centred under the ring, hub outboard (+X)
wm = wm.rotate((0, YW, ZW), (1, YW, ZW), 100)   # thread phase with zero interference against the ring teeth
add('KHK SW0.8-R1 worm, module 0.8, 1 start', wm, (.66, .7, .74), 'drive', 'KHK SW0.8-R1: PD 14, OD 15.6, 18 thread + 12 hub = 30 long, 6 mm bore, M4 set screw, S45C. Thread modelled as ZA.')
add('Worm shaft 6mm D (envelope)', cy(3, BC_X[1] - (WORM_BRG[0] - 1), (WORM_BRG[0] - 1, YW, ZW), (1, 0, 0)), (.7, .72, .74), 'drive', 'goBILDA 6 mm D-shaft envelope, about 60 mm.')
for i, x in enumerate(WORM_BRG):
    add(f'Worm shaft 1601 bearing {i}', tube(7, 3, 5, (x, YW, ZW), (1, 0, 0)), (.8, .8, .82), 'support', 'goBILDA 1601 flanged bearing 6 mm ID x 14 x 5.')
add('goBILDA 2303-1006-0020 20T D-bore worm-shaft gear', x_gear(pinion('2303-1006-0020'), (YW, ZW), xmax=BC_X[1]), (.34, .38, .42), 'drive',
    'Vendor STEP, 6 mm D-bore, just right of the frame. Meshes the shaft-2 20T when the module is bolted in.')
# ---- Stays in the enclosure ----
add('goBILDA 2303-4008-0020 20T shaft-2 gear', x_gear(pinion('2303-4008-0020'), tuple(S2), xmax=BC_X[1]), (.34, .38, .42), 'drive', 'Vendor STEP; right of the frame, in front of the right drum hub.')
add('Owned 2302-0014-0060 60T shaft-2 gear', x_gear(step('2302-0014-0060'), tuple(S2), x0=GEAR_X[0]), (.6, .66, .72), 'drive', 'Your second owned 60T; meshes the owned drum 60T at 48 mm centres, in the old 2GT pulley slot.')
add('Shaft 2 60T hub (owned, envelope)', tube(12, 4, 10, (S2_HUB_X, *S2), (1, 0, 0)), (.55, .58, .62), 'drive', 'Hub for the owned 60T on the 8 mm REX shaft (24 mm envelope), inboard of the gear (rev 12); confirm which owned hub is used.')
add('Shaft 2 8mm REX (envelope)', cy(4, S2_X[1] - S2_X[0], (S2_X[0], *S2), (1, 0, 0)), (.7, .72, .74), 'drive', 'goBILDA 8 mm REX shaft envelope, about 56 mm.')
for i, x in enumerate(S2_BRG):
    add(f'Shaft 2 1611 bearing {i}', tube(7, 4, 5, (x, *S2), (1, 0, 0)), (.8, .8, .82), 'support', 'goBILDA 1611 flanged bearing 8 mm REX x 14 x 5.')
    y0, y1 = (S2[0] - 10, S2[0] + 10) if i == 0 else (S2[0] - 12, -99.1)      # rev 12: outer pedestal clears the ODrive bracket post (Y -98.5)
    ped = box(x, x + 5, y0, y1, 0.5, S2[1] + 10).cut(cy(7, 5, (x, *S2), (1, 0, 0)))
    add(f'Shaft 2 bearing pedestal {i} (printed, base-mounted)', ped, (.42, .5, .45), 'support',
        'Printed block screwed to the base (two M4 into the base plate), holds one 1611. Stays in the enclosure when the module lifts out.')

def arc(c, r, a0, a1): return [(X0, c[0] + r * math.cos(t), c[1] + r * math.sin(t)) for t in np.linspace(a0, a1, 24)]
path = [(X0, YD, ZT)] + arc((Y1, Z1), SR, math.pi / 2, math.pi) + arc((Y2, Z2), R2, 0, -math.pi / 2) + [(X0, -240.0, ZP)]
geo = dict(revision='voltra-module-10', pivot=[X0, ZP], sheave_center=[X0, Y1, Z1], roller_center=[X0, Y2, Z2], branch='top', ratio=53.0,
           shaft2=[float(S2[0]), float(S2[1])], worm_axis=[YW, ZW], ratio_text='60/60 x 20/20 x 1/53 = 1/53 carrier turn per drum turn',
           exit_stack_shift=list(EXIT_SHIFT), cable_diameter_mm=ROPE,
           drum=dict(y=YD, z=ZD, r=RD + RR, x0=TRACK[0], x1=TRACK[1], turns=13.4, sweep=[-45.4, 45.4], dead_wraps=DEAD))
out = dict(parts=rows, metadata=dict(geo, scope='Voltra-style fairlead on the square frame. Not a manufacturing release. Saved packing unchanged.'),
           cablePaths=[dict(name='Neutral rope path', points=[list(map(float, p)) for p in path])],
           audit={'mesh_checks': [], 'solid_checks': [], 'unresolved': [
               'Ring teeth are an involute/helix/throat approximation of a hobbed worm wheel; confirm against the purchased worm before printing. Ring is now part of the printed carrier (replace the whole part when teeth wear).',
               'Frame wall, bearing retention, screw bosses and print orientation are not detailed.',
               'Shaft-2 pedestals are simple printed blocks: bearing retention and base screws not detailed. A guard over the 60T pair is still to do.',
               'Sheave is the saved custom CNC D31; the 625 roller bend radius is small for Amsteel.',
               'Exit swivel moved as an unchanged block; integrating it into the frame is still to do.']},
           motion={'center': [X0, 0.0, ZP], 'rotatingParts': moving, 'samples': [], 'note': 'Pending audit.'})
(P / 'voltra-module10-model.json.gz').write_bytes(gzip.compress(json.dumps(out, separators=(',', ':')).encode(), mtime=0))
(O / 'geometry.json').write_text(json.dumps(dict(geo, moving=moving), indent=2))
print(json.dumps(dict(parts=len(rows), moving=len(moving), shaft2=np.round(S2, 2).tolist(), worm=[YW, ZW], frame_z=FZ, frame_x=FX)))
