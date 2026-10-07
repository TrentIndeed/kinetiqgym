"""V44 fix list S1-S12 (round 2): bottom plate, minimal Amazon metal, rear rack wall + clevis, end handle. Run after build_v44_chassis.py.

Decisions (V44_FIX_LIST.md D1-D10): the bottom plate is the product bottom and the enclosure (same for both variants) bolts onto it.
The printed prototype is the CNC model's parts printed, with the minimum metal you can buy on Amazon and only drill (no cutting,
no tapping, no welding): two 6061 flat bars 1 x 1/4 x 12 in at stock length under the printed plate, through-bolted with nuts below.
PRINT: bottom plate in two P2S pieces (split X 75). The right piece has the rear rack wall printed in - 16 mm thick, the CNC rear plate
(6) plus the clevis flange (10) in one - with the clevis cheeks, shaft-2 pedestals, fuse cradles and battery saddles. The left piece
carries the end handle loop off its back at the motor end (round 5).
CNC: one 6061 plate (same outline, tapped), a 6 mm 6061 rear plate welded on, the printed clevis R07 bolted to it; blocks separate.
Both: no rubber feet. No front upright, no spacers, no top tie (D8, D10).
World frame: X shaft (motor -X), -Y front, Z up, plate top Z 0.
"""
from pathlib import Path
import json, csv, math
import numpy as np
import cadquery as cq
import v44cache as VC
import back_wall as BW                                   # round 9: stepped back wall                                   # round 8: cached clash checks (.cache/)

H = Path(__file__).resolve().parent; R = H.parent
REV = {m: json.loads((H / m / 'revision.json').read_text()) for m in ('cnc', 'printed')}
ROWS = {r['n']: r for r in json.loads((H / 'demo-placements-rev12.json').read_text(encoding='utf-8-sig'))['rows']}
def box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))
def zcyl(r, x, y, z0, z1): return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1))
def ycyl(r, x, z, y0, y1): return cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))
def xcyl(r, y, z, x0, x1): return cq.Solid.makeCylinder(r, x1 - x0, cq.Vector(x0, y, z), cq.Vector(1, 0, 0))
def fuse(solids):
    solids = list(solids); return solids[0] if len(solids) == 1 else solids[0].fuse(*solids[1:]).clean()
def bb(s): b = s.BoundingBox(); return np.array([b.xmin, b.ymin, b.zmin]), np.array([b.xmax, b.ymax, b.zmax])
def cxy(n): r = ROWS[n]; return (round((r['min'][0] + r['max'][0]) / 2, 2), round((r['min'][1] + r['max'][1]) / 2, 2))
def cur(mode, n): return cq.Shape.importBrep(str(H / mode / (n + '.brep')))

# ---------------------------------------------------------------- geometry inputs
X0E, X1E, Y0E, Y1E = -81.0, 290.0, -137.0, 5.5
STEP = (248.0, 20.5)
SPLIT = 75.0                                                           # printed plate split (rear wall X 80..188 stays in one piece)
# R3-3: D-loop at the motor end, at the back edge: lower leg bolted down to the plate (+ rear bar), upper leg into the end cap
# R4-6: rear plate - one plate along the whole back (X -81..248, Y 2.5..8.5, up to the cover ceiling Z 93.5), continuing
# Covers screw to it from the back.
# Round 5: the handle is a short loop standing off the BACK of the rear plate at the motor end, flush with the end face: a 10 mm
# thin loop in the end-face plane (thin side faces rear), 40 mm deep, hand slot 26 x 66 through it, grip bar 14 deep x 10 thin.
RP = dict(x=(-81.0, 248.0), y=(2.5, 8.5), top=93.45)
HANDLE = dict(x=(-81.0, -71.0), y=(5.5 + BW.dy(-80), 48.5 + BW.dy(-80)), z=(-5.0, 93.45), slot=(8.5 + BW.dy(-80), 34.5 + BW.dy(-80), 14.0, 80.0), r_out=12.0, r_slot=6.0, edge=3.0)   # round 9: moves with wall zone A
COVER_SCREWS = [-60.0, -25.0, 72.0, 205.0, 235.0]                       # M3 from the back through the plate into cover bosses (Z 90); round 9: clear of the Pi hood
FAN = (221.0, 58.0)                                                    # round 8: fan 10 mm toward the battery
FEET = [cxy(n) for n in ROWS if n.startswith(('V43_B_motor_foot', 'V43_B_bearing_foot'))]
ODRIVE_FEET = [(213.55, -102.5), (222.8, -33.0)]
BAR = dict(len=304.8, w=25.4, t=6.35, x0=-75.0, front=-105.0, rear=-46.0)      # 6061 1 x 1/4 x 12 in, uncut, within the plate length (R3-2)
BAR_Z = (-5.0 - BAR['t'], -5.0)
BARS = {'front': (BAR['front'], BAR['front'] + BAR['w']), 'rear': (BAR['rear'], BAR['rear'] + BAR['w'])}
BAR_X = (BAR['x0'], BAR['x0'] + BAR['len'])
BAR_SCREWS = [(x, (y0 + y1) / 2) for x in (-40.0, -10.0, 45.0, 70.0, 80.0, 110.0, 150.0) for y0, y1 in BARS.values()]
REAR = dict(x=(80.0, 181.0), y=(2.5 + BW.dy(100), 18.5 + BW.dy(100)), top=93.45)   # round 9: moves with wall zone B                 # printed rack zone of the rear plate (16 = CNC plate 6 + clevis flange 10)
REAR_CNC_Y = (2.5 + BW.dy(100), 8.5 + BW.dy(100))
CLEV = dict(gap=76.2, cheek=6.7, depth=67.0, pin_r=14.5, x=129.7, pin=(REAR['y'][1] + 38.1, 40.0), z=(-5.0, 90.0))
CLEVIS_M6 = [(98.5, 8.0), (160.5, 40.0), (98.5, 80.0), (160.5, 80.0)]   # round 11: clevis 5.5 mm toward the motor (clear of the zone B/C step wall)  # CNC: R07 flange to the tapped rear plate; clear of the fuse leads
STANDOFFS = []                                                          # round 6: the boards moved to the front board plate
JUNCTION_SCREWS = [(186.0, 34.0), (186.0, 63.0)]   # round 11: WAGO bracket beside the fan                         # round 7: power junction bracket, M3 into rear-plate inserts (X, Z)
BOARD_PLATE_SCREWS = [(-70.0, -127.5), (-46.0, -127.5)]                  # round 6: front board plate foot, M3 up into its inserts
FRAME_DOWN = [(110.0, -128.75), (160.0, -128.75)]                     # square back plate (Y -137..-120.5), M4 from below (R4-1)
FUSED = ['FM10_Shaft_2_bearing_pedestal_0_printed_base-mounted', 'FM10_Shaft_2_bearing_pedestal_1_printed_base-mounted',
         'MOUNT_fuse_holder_saddles_printed_base-mounted', 'MOUNT_battery_saddle_front_printed_PA-CF', 'MOUNT_battery_saddle_rear_printed_PA-CF']
BLOCK_SCREWS = [(197.5, -11.5), (232.5, -11.5),   # round 11: fuse cradles under the fan and WAGO
                (182.5, -113.0), (182.5, -102.8), (206.0, -115.0), (206.0, -104.0)]
UNDER_NUTS = [n for n in REV['printed']['parts'] if n.startswith(('V43_N_motor_foot', 'V43_W_nut_motor_foot', 'V43_N_bearing_foot', 'V43_W_nut_bearing_foot'))]
FOOT_BOLTS = [n for n in REV['printed']['parts'] if n.startswith(('V43_B_motor_foot', 'V43_B_bearing_foot'))]

def outline(z0, z1):
    zs = BW.ZONES
    pts = [(X0E, Y0E), (X1E, Y0E), (X1E, STEP[1]), (STEP[0], STEP[1]), (STEP[0], Y1E + zs[2][2]), (zs[2][0], Y1E + zs[2][2]),
           (zs[1][1], Y1E + zs[1][2]), (zs[1][0], Y1E + zs[1][2]), (zs[0][1], Y1E + zs[0][2]), (X0E, Y1E + zs[0][2])]   # round 9: stepped back
    pts = [p for i, p in enumerate(pts) if p != pts[i - 1]]
    return cq.Workplane('XY', origin=(0, 0, z0)).polyline(pts).close().extrude(z1 - z0).edges('|Z').fillet(2.0).val()
def slot(x, y, z0, z1, r=2.25, half=2.0): return fuse([box(x - half, x + half, y - r, y + r, z0, z1), zcyl(r, x - half, y, z0, z1), zcyl(r, x + half, y, z0, z1)])

def cheeks(fillet_root=True):
    """Clevis cheeks straddling a 3 in upright, filleted (S10): 2.5 mm on the outer edges, 6 mm at the root, R15 back corners."""
    out = []
    for xa in (CLEV['x'] - CLEV['gap'] / 2 - CLEV['cheek'], CLEV['x'] + CLEV['gap'] / 2):
        c = cq.Workplane('XY').box(CLEV['cheek'], CLEV['depth'], CLEV['z'][1] - CLEV['z'][0], centered=False).translate((xa, REAR['y'][1] - 0.01, CLEV['z'][0]))
        c = c.edges('|X and >Y').fillet(15.0).edges('>Y').fillet(2.5).val()
        out.append(c)
        if fillet_root:
            for x_face, sgn in ((xa, -1), (xa + CLEV['cheek'], 1)):
                wedge = box(min(x_face, x_face + 6 * sgn), max(x_face, x_face + 6 * sgn), REAR['y'][1] - 0.01, REAR['y'][1] + 6, CLEV['z'][0], CLEV['z'][1])
                out.append(wedge.cut(cq.Solid.makeCylinder(6.0, CLEV['z'][1] - CLEV['z'][0] + 2, cq.Vector(x_face + 6 * sgn, REAR['y'][1] + 6, CLEV['z'][0] - 1), cq.Vector(0, 0, 1))))
    s = fuse(out)
    x0 = CLEV['x'] - CLEV['gap'] / 2 - CLEV['cheek'] - 8
    return s.cut(xcyl(CLEV['pin_r'], CLEV['pin'][0], CLEV['pin'][1], x0, x0 + CLEV['gap'] + 2 * CLEV['cheek'] + 16))

def handle():
    """Round 5: end handle - a thin loop standing off the back of the rear plate, in the end-face plane. It starts 3 mm
    inside the plate (Y 5.5) so the fuse is solid; its edges are rounded 3 mm except where it enters the plate."""
    (x0, x1), (y0, y1), (z0, z1) = HANDLE['x'], HANDLE['y'], HANDLE['z']; sy0, sy1, sz0, sz1 = HANDLE['slot']
    loop = cq.Workplane('YZ', origin=(x0, 0, 0)).center((y0 + y1) / 2, (z0 + z1) / 2).rect(y1 - y0, z1 - z0).extrude(x1 - x0)         .edges('|X and >Y').fillet(HANDLE['r_out'])
    hole = cq.Workplane('YZ', origin=(x0 - 1, 0, 0)).center((sy0 + sy1) / 2, (sz0 + sz1) / 2).rect(sy1 - sy0, sz1 - sz0).extrude(x1 - x0 + 2)         .edges('|X').fillet(HANDLE['r_slot'])
    loop = loop.cut(hole)
    edges = [e for e in loop.faces('<X or >X').edges().vals() if e.Center().y > y0 + 0.5]
    for r in (HANDLE['edge'], 2.0):
        try:
            h = loop.newObject(edges).fillet(r).val()
            if h.isValid(): return h
        except Exception: pass
    return loop.val()

def rear_plate(mode):
    """R4-6: the rear plate along the whole back + the round 5 handle loop off its back at the motor end. PRINT: 6 mm (16 mm in the
    rack zone with the clevis cheeks), fused into the bottom-plate pieces. CNC: 6061 6 mm, welded to the bottom plate, handle loop 6061
    10 mm welded to its back; the R07 clevis bolts on."""
    z0 = -5.0 if mode == 'printed' else 0.0
    # round 9: stepped rear plate (zones + 6 mm connector walls); lowered to the Pi hood floor in zone A over the Pi
    main = fuse([box(x0, x1, BW.INNER0 + d, BW.OUTER0 + d, z0, RP['top']) for x0, x1, d in BW.ZONES]
                + [box(cx0, cx1, cy0, cy1, z0, RP['top']) for cx0, cx1, cy0, cy1 in BW.connectors()])
    if BW.PI_HOOD: main = main.cut(box(*BW.PI_HOOD['x'], -60.0, 40.0, BW.PI_HOOD['z_floor'], RP['top'] + 1))
    parts = [main, handle()]
    if mode == 'printed':
        zone = cq.Workplane('XY').box(REAR['x'][1] - REAR['x'][0], REAR['y'][1] - REAR['y'][0], REAR['top'] + 5.0, centered=False) \
            .translate((REAR['x'][0], REAR['y'][0], -5.0)).edges('|Y and >Z').fillet(4.0).val()
        root = box(REAR['x'][0], 94.0, REAR['y'][0] - 8.0, REAR['y'][0] + 0.01, 0.0, 8.0).cut(xcyl(8.0, REAR['y'][0] - 8.0, 8.0, REAR['x'][0] - 1, 95.0))   # round 9: stops before the fuse pocket
        parts += [zone, root, cheeks()]
    s_ = fuse(parts)
    def ya(x): return BW.inner(x) - 0.1                                                                   # round 9: per-zone plate faces
    def yb(x): return (REAR['y'][1] if (mode == 'printed' and REAR['x'][0] <= x <= REAR['x'][1]) else BW.outer(x)) + 0.1
    cut = [ycyl(1.8 if mode == 'printed' else 1.03, x, z, ya(x), ya(x) + 5.1) for x, z in STANDOFFS]     # board standoffs (insert / tapped)
    cut += [ycyl(2.0, FAN[0] + dx, FAN[1] + dz, ya(FAN[0]), yb(FAN[0])) for dx in range(-15, 16, 6) for dz in range(-15, 16, 6) if dx * dx + dz * dz <= 256]
    cut += [ycyl(1.7, FAN[0] + dx, FAN[1] + dz, ya(FAN[0]), yb(FAN[0])) for dx in (-16, 16) for dz in (-16, 16)]   # fan exhaust grille + screws
    cut += [ycyl(1.7, x, 90.0, ya(x), yb(x)) for x in COVER_SCREWS]                                      # covers: M3 from the back
    cut += [ycyl(1.8 if mode == 'printed' else 1.25, x, z, ya(x), ya(x) + 5.1) for x, z in JUNCTION_SCREWS]   # WAGO bracket (insert / tapped)
    if mode == 'cnc':
        cut += [ycyl(2.5, x, z, ya(x), yb(x)) for x, z in CLEVIS_M6]
    return s_.cut(fuse(cut))

def bottom_plate(mode):
    s = outline(-5.0, 0.0); cut = []
    tap = mode == 'cnc'
    cut += [zcyl(1.65 if tap else 2.25, x, y, -5.1, 0.1) for x, y in FEET]                    # PRINT: through, nut under the bar
    cut += [slot(x, y, -5.1, 0.1) for x, y in ODRIVE_FEET]
    cut += [zcyl(2.25, x, y, -5.1, 0.1) for x, y in FRAME_DOWN]
    cut.append(box(-32.1, 52.9, Y0E - 0.1, -116.7, -2.0, 0.1))                                    # pocket under the screen glass
    cut += [zcyl(1.7, x, y, -5.1, 0.1) for x, y in BOARD_PLATE_SCREWS]                            # round 6: front board plate, M3 x 10 from below
    cut += [zcyl(3.0, x, y, -5.1, -3.0) for x, y in BOARD_PLATE_SCREWS]                           #   head counterbore (flush bottom)
    if mode == 'printed':
        cut += [zcyl(2.8, x, y, -5.1, -1.0) for x, y in BAR_SCREWS]                                 # M4 inserts, screws up through the bars
    else:
        cut += [zcyl(1.7, x, y, -5.1, 0.1) for x, y in BLOCK_SCREWS]                                # printed blocks screwed from below
    return s.cut(fuse(cut))

def flat_bar(side):
    y0, y1 = BARS[side]; s = box(*BAR_X, y0, y1, *BAR_Z)
    holes = [(x, y) for x, y in FEET + FRAME_DOWN if BAR_X[0] + 3 < x < BAR_X[1] - 3 and y0 + 2.0 < y < y1 - 2.0]
    holes += [(x, y) for x, y in BAR_SCREWS if y0 < y < y1]
    cut = [zcyl(2.25, x, y, BAR_Z[0] - .1, BAR_Z[1] + .1) for x, y in holes]
    cut += [cq.Solid.makeCone(4.2, 2.0, 2.2, cq.Vector(x, y, BAR_Z[0] - 0.01), cq.Vector(0, 0, 1)) for x, y in holes]   # drilled countersinks: flat heads flush (R3-1)
    cut += [slot(x, y, BAR_Z[0] - .1, BAR_Z[1] + .1) for x, y in ODRIVE_FEET if BAR_X[0] < x < BAR_X[1] and y0 < y < y1]
    return s.cut(fuse(cut))

def printed_plate_pieces():
    plate = bottom_plate('printed')
    extra = []
    for n in FUSED:
        s = cur('printed', n); root = s.translate(cq.Vector(0, 0, -0.55)).intersect(box(-1e3, 1e3, -1e3, 1e3, -0.1, 0.6))
        extra.append(s.fuse(root))
    rp = rear_plate('printed')
    left = plate.intersect(box(X0E - 1, SPLIT, -200, 50, -6, 1)).fuse(rp.intersect(box(X0E - 1, SPLIT, -200, 60, -6, 100))).clean()
    right = plate.intersect(box(SPLIT, X1E + 1, -200, 50, -6, 1)).fuse(fuse(extra + [rp.intersect(box(SPLIT, X1E + 1, -200, 90, -6, 100))])).clean()
    return left, right

def cnc_clevis():
    fl = cq.Workplane('XY').box(94.0, 10.0, CLEV['z'][1] - CLEV['z'][0], centered=False).translate((88.0, REAR_CNC_Y[1], CLEV['z'][0])) \
        .edges('|Y').fillet(4.0).val()
    s = fuse([fl, cheeks()])
    cut = []
    for x, z in CLEVIS_M6:
        cut += [ycyl(3.3, x, z, REAR_CNC_Y[1] - .1, REAR['y'][1] + .1), cq.Solid.makeCone(3.3, 6.2, 3.0, cq.Vector(x, REAR['y'][1] - 3.0, z), cq.Vector(0, 1, 0))]
    s = s.cut(fuse(cut))
    b0, b1 = BW.connectors()[0][1], BW.connectors()[1][0]                 # round 11: stays between the step walls (zone B back face)
    return s.intersect(box(b0 + 0.1, b1 - 0.1, -60.0, 120.0, -20.0, 120.0))

def reversed_foot_bolt(n, mode):
    """R3-1 (PRINT): countersunk M4 from below, head flush in the bar, nut + washer on top of the part foot (was: nut under the bar)."""
    lo, hi = bb(cur(mode, n)); x, y = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    head = cq.Solid.makeCone(4.0, 2.0, 2.0, cq.Vector(x, y, BAR_Z[0]), cq.Vector(0, 0, 1))
    shank = zcyl(2.0, x, y, BAR_Z[0], 9.0)
    nut = cq.Workplane('XY', origin=(x, y, 4.8)).polygon(6, 7.0 / math.cos(math.pi / 6)).extrude(3.2).val().cut(zcyl(2.0, x, y, 4.7, 8.1))
    return fuse([head, shank]).fuse(nut)

# ---------------------------------------------------------------- parts per variant
AL, PR, AL_PLATE = [.76, .78, .81], [.18, .2, .23], [.70, .72, .75]
L_, Rr = printed_plate_pieces()
NEW = {
 'printed': [
  ('S01_V44_PRINT_bottom_plate_left', L_, 'PRINT PA-CF', PR, 'Bottom plate X -81..75 with the rear plate printed in (6 mm, up to the cover ceiling) and the handle loop standing 40 mm off its back at the motor end, flush with the end face (round 5); 2 x M3 holes for the front board plate (round 6). On the two flat bars.'),
  ('S01_V44_PRINT_bottom_plate_right', Rr, 'PRINT PA-CF', PR,
   'Bottom plate X 75..290 with the rear plate printed in (6 mm; 16 mm in the rack zone = CNC plate 6 + clevis flange 10), fan exhaust grille, filleted clevis cheeks '
   '(3 in upright, d29 pin at the rope height), shaft-2 pedestals, fuse cradles and battery saddles. Prints flat.'),
  ('S17_V44_AL_flat_bar_front_1x0.25x12in', flat_bar('front'), 'Amazon: 6061 flat bar 1 x 1/4 x 12 in, drill only', AL,
   'Stock length, uncut, within the plate length. Drilled + countersunk: flat-head M4 from below, nuts on top inside (flush bottom, no feet). Carries the motor, pillow blocks and plate split.'),
  ('S17_V44_AL_flat_bar_rear_1x0.25x12in', flat_bar('rear'), 'Amazon: 6061 flat bar 1 x 1/4 x 12 in, drill only', AL,
   'Stock length, uncut, as the front bar.')],
 'cnc': [
  ('S01_V44_CNC_bottom_plate_6061_5mm', bottom_plate('cnc'), 'CNC / laser 6061 5 mm, tapped', AL_PLATE,
   'CNC bottom plate: same outline and top face as the printed plate; tapped M4 (use M4 x 14); printed blocks screwed from below.'),
  ('S17_V44_CNC_rear_plate_6061_6mm', rear_plate('cnc'), 'CNC / laser 6061 6 mm, welded to the bottom plate', AL,
   'Rear plate along the whole back (R4-6) with the handle loop (6061 10 mm, welded to its back at the motor end, round 5), fan grille, tapped M6 for the clevis.'),
  ('R07_V44_PRINT_rack_clevis_rear', cnc_clevis(), 'PRINT PA-CF (aluminium later)', [.35, .38, .42],
   'R06 clevis on the rear plate, filleted (S10): cheeks 76.2 apart straddle a vertical 3 in upright, d29 pin left-right at the rope height; 4 countersunk M6.')]}

# ---------------------------------------------------------------- checks + write
report = dict(clashes={}, p2s_fit={}, loads={})
for mode in ('cnc', 'printed'):
    r = REV[mode]; d = H / mode
    drop = list(UNDER_NUTS) + (FUSED if mode == 'printed' else [])
    for n in drop:
        if n in r['parts']:
            r['parts'].remove(n); r['meta'].pop(n, None); r['colors'].pop(n, None)
            for v in r['views'].values():
                if n in v: v.remove(n)
            for ext in ('.step', '.brep'): (d / (n + ext)).unlink(missing_ok=True)
            r.setdefault('excluded', {})[n] = 'printed into the bottom plate (fix S6)' if n in FUSED else 'nut moved under the flat bar (PRINT) / tapped plate (CNC)'
    for n in FOOT_BOLTS:
        s = reversed_foot_bolt(n, mode) if mode == 'printed' else cur(mode, n).intersect(box(-1e3, 1e3, -1e3, 1e3, -5.0, 1e3))
        s.exportStep(str(d / (n + '.step'))); s.exportBrep(str(d / (n + '.brep')))
    existing = {n: cur(mode, n) for n in r['parts'] if not n.startswith(('S01_V44', 'S17_V44', 'R07_V44', 'V44_rubber', 'V44_PRINT_handle'))}
    for old in [m for m in r['parts'] if m.startswith(('V44_PRINT_handle', 'V44_rubber'))]:                   # superseded handle / feet
        r['parts'].remove(old); r['meta'].pop(old, None); r['colors'].pop(old, None)
        for v in r['views'].values():
            if old in v: v.remove(old)
    eb = {n: bb(s) for n, s in existing.items()}
    clash = []
    for n, s, *_ in NEW[mode]:
        lo, hi = bb(s)
        for m, t in existing.items():
            if m in FOOT_BOLTS and n.startswith(('S01_V44_CNC', 'S17_V44_AL_flat_bar')): continue   # threaded / countersunk seat
            l2, h2 = eb[m]
            if (lo - .01 > h2).any() or (l2 - .01 > hi).any(): continue
            v = VC.clash_volume(s, t)
            if abs(v) > 1e-3: clash.append((n, m, round(v, 3)))
    for i, (n, s, *_) in enumerate(NEW[mode]):
        for m, t, *_ in NEW[mode][i + 1:]:
            l1, h1 = bb(s); l2, h2 = bb(t)
            if (l1 - .01 > h2).any() or (l2 - .01 > h1).any(): continue
            v = VC.clash_volume(s, t)
            if abs(v) > 1e-3: clash.append((n, m, round(v, 3)))
    report['clashes'][mode] = clash
    for n, s, manu, col, note in NEW[mode]:
        if n not in r['parts']: r['parts'].append(n)
        r['meta'][n] = dict(group='base' if not n.startswith(('R07', 'V44_PRINT_handle')) else ('rack' if n.startswith('R07') else 'handle'),
                            kind='part', note=note[:400], manufacture=manu, demo_name='', source='build_v44_structure.py (round 2)')
        r['colors'][n] = col
        s.exportStep(str(d / (n + '.step'))); s.exportBrep(str(d / (n + '.brep')))
        for v in ('complete', 'open', 'drivetrain'):
            if n not in r['views'][v]: r['views'][v].append(n)
        if n.startswith('V44_PRINT_handle') and n not in r['views']['handle']: r['views']['handle'].append(n)
        lo, hi = bb(s); dims = sorted((hi - lo).tolist())
        report['p2s_fit'][f'{mode}:{n}'] = dict(size_mm=[round(float(v), 1) for v in (hi - lo)], fits_p2s=bool(dims[1] <= 256 and dims[2] <= 256) if 'PRINT' in manu else None)
    r['status'] = ('V44 + fix list round 2: ' + ('PRINT prototype - printed CNC parts + two uncut Amazon flat bars (drill only)' if mode == 'printed'
                   else 'CNC - 6061 bottom plate + rear plate') + '; printed rear rack wall / R06 clevis, end handle, Pi and BMS on the ceilings.')
    (d / 'revision.json').write_text(json.dumps(r, indent=1))
    with open(d / 'hardware.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['part', 'group', 'kind', 'size', 'source', 'note']); w.writeheader(); w.writerows([h for h in r['hardware'] if h['part'] in r['parts']])

# S12 load check at 890 N (100 lb x 2): rope at the pivot (X 135.2, Z 40) -> rack pin (Z 40) through printed parts + 2 flat bars
F = 890.0
Zw = (REAR['x'][1] - REAR['x'][0]) * (REAR['y'][1] - REAR['y'][0]) ** 2 / 6
report['loads'] = dict(design_force_N=F,
    rear_wall_root=dict(moment_Nm=round(F * 0.040, 1), section='108 x 16 printed', stress_MPa=round(F * 40 / Zw, 1),
                        note='PA-CF across layers ~25-35 MPa; wall printed flat (layers along the wall) so the root bends across layers'),
    fairlead=dict(path='rope enters the fairlead from the drum (sheave top, Z ~68, toward +Y) and leaves at the exit (Z 40, toward -Y): the module sees a couple, the net pull goes drum -> pillow blocks -> plate -> rear wall -> rack pin',
                  couple_Nm=round(F * 0.028, 1), section='square back plate 70 x 13.5 (reaches the wall, R3-4)', stress_MPa=round(F * 28 / (70 * 13.5 ** 2 / 6), 1),
                  front_bolts_N_each=round(F * 28 / 34.75 / 2)),
    plate_in_plane_MPa=round(F / (5 * 100), 1),
    clevis_pin_bearing_MPa=round(F / (2 * CLEV['cheek'] * 2 * CLEV['pin_r']), 1),
    handle=dict(carry_x3_N=159.0, note='loop off the back of the rear plate, carried hanging (load along X, across the 10 mm loop): legs bend as cantilevers from the plate; the plate takes it in-plane',
                root_arm_mm=33.0, legs_root_bending_MPa=round(159 * 33.0 / ((19.0 + 13.45) * 10.0 ** 2 / 6), 1), grip_bending_MPa=round(159 * 66 / 8 / (14 * 10.0 ** 2 / 6), 1)),
    metal='2 x 6061 1 x 1/4 x 12 in flat bar, uncut, drilled + countersunk; flat-head M4 from below, nuts on top; no welding, cutting or tapping')
report['joints'] = dict(FEET=FEET, ODRIVE_FEET=ODRIVE_FEET, BAR_SCREWS=BAR_SCREWS, FRAME_DOWN=FRAME_DOWN, BOARD_PLATE_SCREWS=BOARD_PLATE_SCREWS,   # round 13: for build_v44_fasteners.py
                        COVER_SCREWS=COVER_SCREWS, FAN=FAN, JUNCTION_SCREWS=JUNCTION_SCREWS, CLEVIS_M6=CLEVIS_M6, BLOCK_SCREWS=BLOCK_SCREWS, SPLIT=SPLIT,
                        BAR_Z=BAR_Z, REAR_CNC_Y=REAR_CNC_Y, REAR=REAR)
(H / 'structure-report.json').write_text(json.dumps(report, indent=1))
print(json.dumps(dict(clashes=report['clashes'], loads=report['loads']), indent=1))
print('P2S', {k: v for k, v in report['p2s_fit'].items() if v['fits_p2s'] is not None})
