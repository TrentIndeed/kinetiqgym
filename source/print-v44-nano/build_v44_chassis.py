"""V44 phase 3/4 mock: interfaces, printed base + aluminium flat bars, and a Nano-style shell in P2S pieces.

Run after mock_models.py (run_v44.sh does). World frame as everywhere: X along the shaft (motor at -X), -Y front, Z up,
base top Z 0. The shell follows the live demo's box rule (parts + 1 mm gap + 3 mm wall, front set by the fairlead plate):
exterior X -81..287.5, Y -137..5.5, Z -15.2..96.5 (368.5 x 142.5 x 111.7 mm).

MOCK, not a release: first-pass geometry for looks, fit and interfaces. Seam lips, cover screws, rib patterns, insert bosses
for every cover joint and all load paths (handle, rack puck) are not designed or checked for strength.

What it does
1. interfaces.json - every hole, insert, slot and cutout that meets the base or the shell, with world positions.
2. CAD updates - 12 mm grommet hole in the 4 mm motor face plate for the phase leads (route extended in mounts-rev11);
   battery lead exit + charge port allowances (rear of the pack, through the spacer window into a back-wall pocket).
3. Base - two printed PA-CF pieces (split X 98) on two 30 x 6 aluminium flat bars that tie them together; bolt holes,
   nut pockets in the bars, pedestal / saddle / fairlead inserts, ODrive encoder-gap slots, screen notch.
4. Shell - bottom pans (2), upper covers (3, seams X 98 / 172 in line with the front panels), end caps (2): motor end with the
   handle loop (replaces the V43 external handle), battery end with the small power switch. Front: screen window + vent ribs |
   square exit-module recess + journal hole + 4 standoff holes | vent grille. Top: vent band over the Pi and motor. Back: Pi
   service window, fan grille + 4 screws, 12 board-standoff bosses, rack puck boss, battery-lead pocket closed by a removable
   rear I/O panel (charge port, bond lug). Printed twist-lock rack puck.
5. Checks - exact BRep overlap of every new solid against every V44 part and allowance; P2S (256 mm) fit per printed piece.
"""
from pathlib import Path
import json, csv, math
import numpy as np
import cadquery as cq
import v44cache as VC                                   # round 8: cached clash checks (.cache/)

H = Path(__file__).resolve().parent; R = H.parent
# September 28: the base + shell mock below is superseded by V44_FIX_LIST.md decisions D1-D7 (bottom plate = product bottom, rear
# rack/handle plate, flush I/O, square exit frame). Until items S1-S6 and E1-E8 rebuild them, only the CAD updates run.
MOCK_SHELL = False
REV = {m: json.loads((H / m / 'revision.json').read_text()) for m in ('cnc', 'printed')}
X0E, X1E, Y0E, Y1E, Z0E, Z1E = -81.0, 287.5, -137.0, 5.5, -15.2, 96.5
W, RT, RB = 3.0, 9.0, 12.0                    # wall; exterior long-edge radii (top limited by the BMS corner, shell-clearance.json)
CAP = 10.0                                    # end-cap depth
SEAMS = (98.0, 172.0)                         # cover seams: clear of the Teensy bosses (X 97.5) and the exit plate (X 101.8..168.6)
ZS = -5.0                                     # pan / cover seam = base underside
X0B, X1B = X0E + CAP, X1E - CAP               # body between the caps

def box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))
def cyl(r, p, d, h): return cq.Solid.makeCylinder(r, h, cq.Vector(*p), cq.Vector(*d))
def ycyl(r, x, z, y0, y1): return cyl(r, (x, y0, z), (0, 1, 0), y1 - y0)
def zcyl(r, x, y, z0, z1): return cyl(r, (x, y, z0), (0, 0, 1), z1 - z0)
def prism(x0, x1, y0, y1, z0, z1, rt, rb):
    w = cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
    return w.edges('|X and >Z').fillet(rt).edges('|X and <Z').fillet(rb)
def comp(solids):
    """One tool from many (fused, so overlapping cutters - a bolt hole and its nut pocket - give a valid boolean)."""
    solids = list(solids)
    return solids[0] if len(solids) == 1 else solids[0].fuse(*solids[1:]).clean()
def bb(s): b = s.BoundingBox(); return np.array([b.xmin, b.ymin, b.zmin]), np.array([b.xmax, b.ymax, b.zmax])

parts = []        # (name, shape, group, kind, manufacture, colour, note)
def add(name, shp, group, kind, manu, col, note):
    shp = shp.clean() if hasattr(shp, 'clean') else shp
    assert shp.isValid(), name
    parts.append((name, shp, group, kind, manu, col, note))

# ---------------------------------------------------------------- interfaces (world positions)
I = []
def itf(name, kind, host, xyz, size, serves): I.append(dict(name=name, kind=kind, host=host, at=[round(float(v), 2) for v in xyz], size=size, serves=serves))
ROWS = {r['n']: r for r in json.loads((H / 'demo-placements-rev12.json').read_text(encoding='utf-8-sig'))['rows']}
def centre_xy(n): r = ROWS[n]; return (round((r['min'][0] + r['max'][0]) / 2, 2), round((r['min'][1] + r['max'][1]) / 2, 2))
MOTOR_FEET = [centre_xy(n) for n in ROWS if n.startswith('V43_B_motor_foot')]              # from the placed bolts (names are not positions)
PILLOW = [centre_xy(n) for n in ROWS if n.startswith('V43_B_bearing_foot')]
CARRIER = [(centre_xy(n)[0], round((ROWS[n]['min'][2] + ROWS[n]['max'][2]) / 2, 2)) for n in ROWS if n.startswith('FM10 Carrier_M3x25')]
PED = [(182.5, -115.0), (182.5, -100.5), (206.0, -116.5), (206.0, -102.5)]
ODRIVE_FEET = [(213.55, -102.5), (222.8, -33.0)]
SADDLES = [(180.5, -12.5), (215.5, -12.5)]
FAIRLEAD_PLATE = [(105.2, -125.0), (165.2, -125.0)]
for x, y in MOTOR_FEET: itf('motor gusset foot bolt', 'M4 through, nut in flat-bar pocket', 'base + flat bar', (x, y, 0), 'd4.5', 'V43 motor gussets')
for x, y in PILLOW: itf('6001 pillow block foot bolt', 'M4 through, nut in flat-bar pocket', 'base + flat bar', (x, y, 0), 'd4.5', 'V43 6001 cartridges')
for x, y in PED: itf('shaft-2 pedestal screw', 'M4 heat-set insert', 'base', (x, y, 0), 'd5.6', 'FM10 shaft-2 pedestals')
for x, y in ODRIVE_FEET: itf('ODrive bracket foot', 'M4 from below, slot +-2 mm in X (sets the 1 mm encoder gap)', 'base + flat bar', (x, y, 0), '4.5 x 8.5 slot', 'rev 12 ODrive bracket')
for x, y in SADDLES: itf('fuse saddle screw', 'M3 heat-set insert', 'base', (x, y, 0), 'd4.0', 'fuse holder saddles')
for x, y in FAIRLEAD_PLATE: itf('fairlead plate hold-down', 'M4 heat-set insert', 'base', (x, y, 0), 'd5.6', 'FM10 square back plate')
itf('screen notch', 'cut-out', 'base', (10.25, -123.75, 0), 'X -35..55.5, Y -132..-115.5', 'screen glass + bezel below Z 0')

# ---------------------------------------------------------------- base: two printed pieces on two aluminium flat bars
BY0, BY1 = -132.0, 0.5
def base_piece(x0, x1):
    w = cq.Workplane('XY').box(x1 - x0, BY1 - BY0, 5.0, centered=False).translate((x0, BY0, -5.0)).edges('|X and <Z').chamfer(2.0)
    s = w.val()
    cut = [zcyl(2.25, x, y, -5.1, 0.1) for x, y in MOTOR_FEET + PILLOW] + [zcyl(2.8, x, y, -5.1, 0.1) for x, y in PED + FAIRLEAD_PLATE]
    cut += [zcyl(2.0, x, y, -5.1, 0.1) for x, y in SADDLES]
    for x, y in ODRIVE_FEET:
        cut += [box(x - 2, x + 2, y - 2.25, y + 2.25, -5.1, 0.1), zcyl(2.25, x - 2, y, -5.1, 0.1), zcyl(2.25, x + 2, y, -5.1, 0.1)]
    cut.append(box(-35.0, 55.5, BY0 - 1, -115.5, -5.1, 0.1))                          # screen notch
    for x in (-60.0, -10.0, 90.0, 106.0, 140.0, 250.0, 275.0):                            # flat-bar screws (M4 from below into inserts)
        for y in (-91.5, -33.0):
            cut.append(zcyl(2.8, x, y, -5.1, -1.0))
    return s.cut(comp(cut))
add('S01_V44_PRINT_base_left', base_piece(-77.0, SEAMS[0]), 'base', 'part', 'PRINT PA-CF', [.18, .2, .23],
    'Printed base, motor end (X -77..98), 5 mm, on the two flat bars. Bolt holes for the motor gussets and left pillow block; screen notch. MOCK.')
add('S01_V44_PRINT_base_right', base_piece(SEAMS[0], 283.5), 'base', 'part', 'PRINT PA-CF', [.18, .2, .23],
    'Printed base, fairlead / ODrive / battery end (X 98..283.5). Pedestal, fairlead-plate and saddle inserts, ODrive encoder-gap slots. The flat bars tie it to the left piece. MOCK.')
itf('flat-bar screws', 'M4 from below into base inserts', 'base + flat bar', (0, 0, -5), '14 x d5.6', 'bars tie the two base pieces across X 98')
BARS = {'front': (-106.5, -76.5), 'rear': (-48.0, -18.0)}
for side, (y0, y1) in BARS.items():
    bar = box(-72.0, 278.0, y0, y1, -11.0, -5.0); cut = []
    for x, y in MOTOR_FEET + PILLOW:
        if y0 < y < y1: cut += [zcyl(2.25, x, y, -11.1, -4.9), zcyl(5.0, x, y, -9.2, -4.9)]          # bolt + nut/washer pocket
    for x, y in ODRIVE_FEET:
        if y0 < y < y1: cut += [box(x - 2, x + 2, y - 2.25, y + 2.25, -11.1, -4.9), zcyl(2.25, x - 2, y, -11.1, -4.9), zcyl(2.25, x + 2, y, -11.1, -4.9)]
    for x, y in PED:
        if y0 < y < y1: cut.append(zcyl(2.25, x, y, -11.1, -4.9))
    for x in (-60.0, -10.0, 90.0, 106.0, 140.0, 250.0, 275.0):
        cut.append(zcyl(2.25, x, (y0 + y1) / 2 if side == 'rear' else -91.5, -11.1, -4.9))
    add(f'S17_V44_AL_flat_bar_{side}', bar.cut(comp(cut)), 'base', 'part', 'Aluminium 6061 flat bar 30 x 6, 350 long (cut + drill)', [.76, .78, .81],
        f'{side.title()} load bar under the printed base (Z -11..-5, inside the old bolt-tip zone: no added height). Carries motor, pillow-block and fairlead loads between the base pieces; '
        'the V43 nuts sit in pockets in the bar. 30 wide (V42 used 25) so the motor-foot and pillow-block bolts both land on it. MOCK.')

# ---------------------------------------------------------------- shell
outer = prism(X0B, X1B, Y0E, Y1E, Z0E, Z1E, RT, RB).val()
inner = prism(X0B - 1, X1B + 1, Y0E + W, Y1E - W, Z0E + W, Z1E - W, RT - W, RB - W).val()
body = outer.cut(inner)
cut, addon = [], []
# front, screen panel
cut.append(box(-32.1, 52.9, Y0E - 1, Y0E + W + 1, -1.9, 83.2))                                   # screen window (bezel sits on the face)
cut += [box(x, x + 2.5, Y0E - 1, Y0E + W + 1, 12.0, 72.0) for x in list(np.arange(-66.0, -37.0, 5.0)) + list(np.arange(58.0, 92.0, 5.0))]
itf('screen window', 'cut-out', 'front cover left', (10.4, Y0E, 40.65), '85 x 85.1', 'Waveshare 4" DPI screen (bezel on the face)')
# front, exit module
EXC = (135.2, 40.0)
cut.append(ycyl(26.0, EXC[0], EXC[1], Y0E - 1, Y0E + W + 1))                                       # journal / rope passage
cut.append(box(101.3, 169.1, Y0E - 0.1, Y0E + 0.5, 6.1, 73.9))                                    # rear-mount-plate recess (0.5)
for x in (105.2, 165.2):
    for z in (5.25, 65.25):
        cut.append(ycyl(3.0, x, z, Y0E - 1, Y0E + W + 1)); itf('exit module standoff', 'M3 standoff through the front wall', 'front cover centre', (x, Y0E, z), 'd6', 'fairlead plate 7.5 mm standoffs')
for x, z in CARRIER:                                                                               # exit-module clamp screws, nuts inside the wall
    cut += [ycyl(1.7, x, z, Y0E - 1, Y0E + W + 1), ycyl(3.75, x, z, Y0E + 0.4, Y0E + W + 0.1)]
    itf('exit module clamp screw', 'M3 x 25 through the wall, nut in a pocket on the inside', 'front cover centre', (x, Y0E, z), 'd3.4 + d7.5 pocket', 'FM10 carrier / rear mount plate')
itf('exit passage', 'cut-out', 'front cover centre', (EXC[0], Y0E, EXC[1]), 'd52', 'carrier journal (rotating, 3.5 mm clear)')
# front, grille
cut += [box(x, x + 26.0, Y0E - 1, Y0E + W + 1, z, z + 2.5) for x in (182.0, 212.0, 242.0) for z in np.arange(10.0, 84.0, 6.0)]
# top vent band over the Pi and motor
cut += [box(x, x + 3.0, -100.0, -40.0, Z1E - W - 1, Z1E + 1) for x in np.arange(-62.0, 72.0, 6.0)]
# back
cut.append(box(20.0, 73.0, Y1E - W - 1, Y1E + 1, 70.0, 86.0)); itf('Pi service window', 'cut-out', 'back cover left', (46.5, Y1E, 78), '53 x 16', 'Pi 4 USB / Ethernet ports')
FAN = (211.0, 58.0)
for dx in np.arange(-15.0, 15.1, 6.0):
    for dz in np.arange(-15.0, 15.1, 6.0):
        if math.hypot(dx, dz) <= 16.0: cut.append(ycyl(2.0, FAN[0] + dx, FAN[1] + dz, Y1E - W - 1, Y1E + 1))
for dx in (-16, 16):
    for dz in (-16, 16):
        cut.append(ycyl(1.7, FAN[0] + dx, FAN[1] + dz, Y1E - W - 1, Y1E + 1)); itf('fan screw', 'M3 x 30 through the fan into the wall (insert)', 'back cover right', (FAN[0] + dx, Y1E, FAN[1] + dz), 'd3.4', 'Noctua fan + duct')
itf('fan grille', 'cut-out', 'back cover right', (FAN[0], Y1E, FAN[1]), 'd32 hole field', 'Noctua NF-A4x10 exhaust')
STANDOFFS = [(94.5, 52.5), (94.5, 69.3), (129.1, 52.5), (129.1, 69.3), (94.5, 24.5), (94.5, 37.9), (125.9, 24.5), (125.9, 37.9),
             (136.5, 32.5), (136.5, 56.9), (160.9, 32.5), (160.9, 56.9)]
for x, z in STANDOFFS:
    addon.append(ycyl(3.2, x, z, 1.6, Y1E - W + 0.5)); cut.append(ycyl(1.8, x, z, 1.5, Y1E - 0.8))
    itf('board standoff boss', 'M2.5 heat-set insert', 'back cover left/centre', (x, 1.6, z), 'd6.4 boss', 'Teensy / CAN / regulator perfboards')
PUCK = (135.2, 30.0)
addon.append(ycyl(32.0, PUCK[0], PUCK[1], Y1E - 1, Y1E + 4.0))
for a in (45, 135, 225, 315):
    t = math.radians(a); cut.append(ycyl(2.75, PUCK[0] + 24 * math.cos(t), PUCK[1] + 24 * math.sin(t), Y1E - W - 1, Y1E + 4.1))
itf('rack puck boss', '4 x M5 through the back wall', 'back cover centre', (PUCK[0], Y1E, PUCK[1]), 'd64 boss, M5 on r24', 'twist-lock rack puck; internal load path to the base NOT designed')
# battery-lead pocket (back of the right cover) closed by the removable rear I/O panel
PK = (248.0, 276.0, 2.0, 93.0)                 # X, Z of the pocket frame; interior X 251..273, Z 5..90, Y 2.5..16.5
cut.append(box(251.0, 273.0, Y1E - W - 1, Y1E + 1, 5.0, 90.0))
addon.append(box(PK[0], PK[1], Y1E - W, 16.5, PK[2], PK[3]).cut(box(251.0, 273.0, Y1E - W - 1, 16.6, 5.0, 90.0)))
itf('battery lead pocket', 'back-wall pocket 22 x 14 x 85 inside', 'back cover right', (262.0, 9.5, 47.5), 'pocket', 'TP2700 main + balance leads, charge port')
body = body.fuse(comp(addon)).cut(comp(cut))

def split(x0, x1, z0, z1): return body.intersect(box(x0, x1, Y0E - 5, 30.0, z0, z1))
COV = [.21, .22, .24]
add('V44_PRINT_cover_left_screen', split(X0B, SEAMS[0], ZS, Z1E + 5), 'covers', 'part', 'PRINT PETG-CF / PA-CF', COV,
    'Upper cover, motor end (X -71..98): 4" screen window with vertical vent ribs each side, top vent band over the Pi and motor, Pi service window at the back, Teensy/CAN boss row. Prints on its cut face. MOCK.')
add('V44_PRINT_cover_centre_exit', split(SEAMS[0], SEAMS[1], ZS, Z1E + 5), 'covers', 'part', 'PRINT PETG-CF / PA-CF', COV,
    'Upper cover, fairlead section (X 98..172): square exit-module recess, 52 mm journal passage and 4 standoff holes on the front; rack puck boss and regulator bosses on the back. MOCK.')
add('V44_PRINT_cover_right_grille', split(SEAMS[1], X1B, ZS, Z1E + 5), 'covers', 'part', 'PRINT PETG-CF / PA-CF', COV,
    'Upper cover, ODrive / battery end (X 172..277.5): vent grille on the front, fan grille and 4 fan screws on the back, battery-lead pocket for the rear I/O panel. MOCK.')
floor_vents = comp([box(x, x + 3.0, -95.0, -40.0, Z0E - 1, Z0E + W + 1) for x in np.arange(215.0, 246.0, 6.0)])
add('V44_PRINT_pan_left', split(X0B, SEAMS[0], Z0E - 1, ZS), 'covers', 'part', 'PRINT PETG-CF', [.15, .16, .17],
    'Bottom pan, motor end: rounded underside under the flat bars and bolt tips (1 mm clear). MOCK.')
add('V44_PRINT_pan_right', split(SEAMS[0], X1B, Z0E - 1, ZS).cut(floor_vents), 'covers', 'part', 'PRINT PETG-CF', [.15, .16, .17],
    'Bottom pan, fairlead / ODrive / battery end (X 98..277.5): intake slots under the ODrive. MOCK.')

def cap(x0, x1, end):
    w = prism(x0, x1, Y0E, Y1E, Z0E, Z1E, RT, RB)
    w = w.faces('<X' if end == 'motor' else '>X').edges().fillet(4.0)
    s = w.val()
    xi0, xi1 = (x0 + W, x1 + 1) if end == 'motor' else (x0 - 1, x1 - W)
    return s.cut(prism(xi0, xi1, Y0E + W, Y1E - W, Z0E + W, Z1E - W, RT - W, RB - W).val())
mcap = cap(X0E, X0B, 'motor')
grip = cyl(10.0, (-116.0, -105.0, 36.0), (0, 1, 0), 85.0)
arms = comp([box(-114.0, X0E + 1.0, y0, y1, 26.0, 46.0) for y0, y1 in ((-105.0, -97.0), (-28.0, -20.0))])
mcap = mcap.fuse(grip).fuse(arms).clean()
add('V44_PRINT_end_cap_motor_handle', mcap, 'covers', 'part', 'PRINT PA-CF', COV,
    'Motor-end cap with the integrated handle loop (same place as the demo handle, which it replaces): grip d20 across Y -105..-20 at X -116, 25 mm finger opening. '
    'Handle load path into the base is NOT designed (needs 2 bolts into the base end or the motor plate). MOCK.')
bcap = cap(X1B, X1E, 'battery')
SW = (-65.0, 86.0)
bcap = bcap.fuse(cyl(6.0, (X1E - 0.1, SW[0], SW[1]), (1, 0, 0), 0.9)).cut(cyl(3.6, (X1B - 1, SW[0], SW[1]), (1, 0, 0), CAP + 3))
add('V44_PRINT_end_cap_battery_switch', bcap, 'covers', 'part', 'PRINT PA-CF', COV,
    'Plain battery-end cap with the small power switch (7 mm hole at Y -65, Z 86, in the 8 mm free band above the BMS). The switch drives the BMS soft on/off or a latching MOSFET; it never carries motor current. MOCK.')
itf('power switch', '7 mm panel hole, 8.5 mm free depth behind', 'battery end cap', (X1E, SW[0], SW[1]), 'd7.2', 'small latching switch -> BMS soft switch')
io = box(PK[0], PK[1], 16.5, 19.5, PK[2], PK[3])
CP = (268.0, 75.0)
io = io.cut(box(CP[0] - 4.45, CP[0] + 4.45, 16.4, 19.6, CP[1] - 8.2, CP[1] + 8.2)).cut(ycyl(2.6, 258.0, 20.0, 16.4, 19.6))
for x in (250.0, 274.0):
    for z in (6.0, 89.0): io = io.cut(ycyl(1.2, x, z, 16.4, 19.6))
add('V44_PRINT_rear_IO_panel', io, 'covers', 'part', 'PRINT PETG', [.26, .27, .29],
    'Removable rear I/O panel closing the battery-lead pocket: XT60E-M charge port (vertical, X 268 Z 75), M5 bond lug (X 258 Z 20), 4 x M2.5 screws. MOCK.')
itf('charge port', 'XT60E-M panel mount, vertical', 'rear I/O panel', (CP[0], 19.5, CP[1]), '8.9 x 16.4', 'external charger')
itf('bond lug', 'M5', 'rear I/O panel', (258.0, 19.5, 20.0), 'd5.2', 'chassis bond')
puck = ycyl(35.0, PUCK[0], PUCK[1], Y1E + 4.0, Y1E + 14.0).cut(ycyl(12.0, PUCK[0], PUCK[1], Y1E + 9.0, Y1E + 14.1))
for a in (90, 210, 330):
    t = math.radians(a); c = (PUCK[0] + 38 * math.cos(t), PUCK[1] + 38 * math.sin(t))
    puck = puck.fuse(ycyl(6.0, c[0], c[1], Y1E + 10.0, Y1E + 14.0).fuse(box(PUCK[0] + 30 * math.cos(t) - 4, PUCK[0] + 30 * math.cos(t) + 4, Y1E + 10.0, Y1E + 14.0,
                                                                              PUCK[1] + 30 * math.sin(t) - 4, PUCK[1] + 30 * math.sin(t) + 4)))
for a in (45, 135, 225, 315):
    t = math.radians(a); puck = puck.cut(ycyl(2.75, PUCK[0] + 24 * math.cos(t), PUCK[1] + 24 * math.sin(t), Y1E + 3.9, Y1E + 14.1))
add('V44_PRINT_rack_twist_lock_puck', puck, 'rack', 'part', 'PRINT PA-CF (aluminium later)', [.35, .38, .42],
    'VOLTRA-style twist-lock rack puck behind the fairlead exit (X 135.2): d70, 3 bayonet lugs, 4 x M5 through the back wall. Printed for force tests; the load path inside the shell is NOT designed yet. MOCK.')

# ---------------------------------------------------------------- CAD updates on existing parts + new allowances
FP = 'V43_METAL_motor_face_4mm'
face = cq.Shape.importBrep(str(H / 'printed' / (FP + '.brep'))).cut(cyl(6.0, (5.0, -34.0, 54.5), (1, 0, 0), 6.0))   # 1.7 mm web to the Pi-bracket M3 holes, 2.8 to motor bolt 3
# Fix L8: the rear gusset and its two web bolts sit at Y -30, but the plate's holes were left at Y -24: move them.
face = face.fuse(cyl(2.2, (6.0, -24.0, 16.0), (1, 0, 0), 4.0)).fuse(cyl(2.2, (6.0, -24.0, 30.0), (1, 0, 0), 4.0)).clean()
face = face.cut(cyl(2.2, (5.0, -30.0, 16.0), (1, 0, 0), 6.0)).cut(cyl(2.2, (5.0, -30.0, 30.0), (1, 0, 0), 6.0))
# Round 8: top edge lowered under the Pi (it slides 14 mm toward the screen centre): Z 80.5 (8 mm above the top motor bolt at Z 72.5),
# Z 70.5 at the back corner under the Pi's USB/Ethernet stack.
face = face.cut(box(5.9, 10.1, -108.1, -20.9, 80.5, 89.1)).cut(box(5.9, 10.1, -57.0, -35.9, 70.5, 89.1))   # round 12: the notch follows the Pi 15 mm toward the screen
itf('phase-lead grommet hole', 'd12 through the 4 mm motor face plate', 'motor face plate', (8.0, -34.0, 54.5), 'd12', 'motor phase leads (route in mounts-rev11)')
ALLOW_OLD = {'RESERVE_battery_lead_exit': (comp([box(252.0, 262.0, -3.5, 16.0, 10.0, 59.0), box(252.0, 262.0, 2.5, 16.0, 59.0, 89.0), box(252.0, 262.0, -4.0, 2.5, 66.5, 89.0)]),
                                       'TP2700 main + balance lead exit: out of the rear end faces through the rear-spacer window, bend into the back-wall pocket, up, and back in over the spacer (Z > 66) to the BMS wiring. The leads cannot exit at the front (0.5 mm to the wall).'),
         'RESERVE_charge_port_XT60E': (box(263.5, 272.5, 3.0, 16.5, 66.5, 83.5), 'XT60E-M charge port body + solder cups behind the rear I/O panel.')}
ALLOW = {}                                        # fix L1: the battery-lead and rear-I/O allowances are demo parts now (mounts-rev11)
if not MOCK_SHELL: parts.clear()

# ---------------------------------------------------------------- checks
existing = {}
for n in REV['printed']['parts'] + [a['name'] for a in REV['printed'].get('allowances', [])]:
    f = H / 'printed' / (n + '.brep')
    if not f.exists(): f = H / 'allowances' / (n + '.brep')
    if f.exists(): existing[n] = cq.Shape.importBrep(str(f))
existing[FP] = face
for n, (s, _) in ALLOW.items(): existing[n] = s
eb = {n: bb(s) for n, s in existing.items()}
DESIGNED = {('S01_V44_PRINT_base_left', 'V43_B_motor_foot'), ('S01_V44_PRINT_base_right', 'V43_B_bearing_foot')}
clash = []
new = [(n, s) for n, s, *_ in parts] + [(n, s) for n, (s, _) in ALLOW.items()]
for n, s in new:
    lo, hi = bb(s)
    for m, t in existing.items():
        if m == n or m == 'V43_PRINT_motor_side_handle': continue
        l2, h2 = eb[m]
        if (lo - 0.01 > h2).any() or (l2 - 0.01 > hi).any(): continue
        v = VC.clash_volume(s, t)
        if abs(v) > 1e-3: clash.append(dict(new=n, part=m, overlap_mm3=round(v, 3)))
for i, (n, s) in enumerate(new):                                        # new vs new (touching faces give 0)
    for m, t in new[i + 1:]:
        l1, h1 = bb(s); l2, h2 = bb(t)
        if (l1 - 0.01 > h2).any() or (l2 - 0.01 > h1).any(): continue
        v = VC.clash_volume(s, t)
        if abs(v) > 1e-3: clash.append(dict(new=n, part=m, overlap_mm3=round(v, 3)))
fit = []
for n, s, g, k, manu, *_ in parts:
    lo, hi = bb(s); d = sorted(hi - lo)
    fit.append(dict(part=n, size_mm=[round(float(v), 1) for v in hi - lo], fits_p2s=bool(d[-1] <= 256 and d[1] <= 256) if 'PRINT' in manu else None))
env = outer.fuse(prism(X0E, X0B, Y0E, Y1E, Z0E, Z1E, RT, RB).faces('<X').edges().fillet(4.0).val()).fuse(prism(X1B, X1E, Y0E, Y1E, Z0E, Z1E, RT, RB).faces('>X').edges().fillet(4.0).val())
vol_body = env.Volume() / 1e6
vol_pocket = (PK[1] - PK[0]) * (19.5 - Y1E) * (PK[3] - PK[2]) / 1e6
report = dict(exterior_box_mm=[X1E - X0E, Y1E - Y0E, Z1E - Z0E], box_volume_L=round((X1E - X0E) * (Y1E - Y0E) * (Z1E - Z0E) / 1e6, 3),
              rounded_shell_volume_L=round(vol_body, 3), battery_pocket_L=round(vol_pocket, 3), radii_mm=dict(top=RT, bottom=RB, end_faces=4.0),
              clashes=clash, p2s_fit=fit)
(H / 'chassis-report.json').write_text(json.dumps(report, indent=1))
(H / 'interfaces.json').write_text(json.dumps(dict(superseded=None if MOCK_SHELL else 'Shell and base entries belong to the September 28 mock and are superseded by V44_FIX_LIST.md D1-D7; regenerated in items S1-S6 / E1-E8.', note='World frame (X shaft, -Y front, Z up, base top Z 0). V44 mock base + shell; every entry is a hole, insert, slot or cut-out in the base or the shell.',
                                                    interfaces=I), indent=1))

# ---------------------------------------------------------------- write into the V44 revision
for mode in ('cnc', 'printed'):
    r = REV[mode]; d = H / mode
    face.exportStep(str(d / (FP + '.step'))); face.exportBrep(str(d / (FP + '.brep')))
    # round 13: the real KHK worm is threaded over its full 30 mm (r 7.8); the back plate's bore narrowed to r 8.0 over X 151..156.2
    # (0.2 mm to the thread tips - a printed part would rub). Open it to r 9.0 like the rest of the bore (1.2 mm clearance).
    BP = 'FM10_Square_back_plate_4-screw_enclosure_mount'
    if (d / (BP + '.brep')).exists():
        bp = cq.Shape.importBrep(str(d / (BP + '.brep'))).cut(cyl(9.0, (149.5, -105.0, 11.8), (1, 0, 0), 156.6 - 149.5)).clean()
        bp.exportStep(str(d / (BP + '.step'))); bp.exportBrep(str(d / (BP + '.brep')))
        r['meta'][BP]['note'] = (r['meta'][BP]['note'].split(' Round 13:')[0] + ' Round 13: worm bore opened to d18 up to the right bearing (the real worm is threaded full length).')[:400]
    tag = ' V44: 12 mm grommet hole for the motor phase leads at Y -34, Z 54.5; rear-gusset holes at Y -30 (fix L8).'
    r['meta'][FP]['note'] = (r['meta'][FP]['note'].split(' V44: 12 mm grommet')[0] + tag)[:400]
    old = 'V43_PRINT_motor_side_handle'                                  # replaced by the motor end cap's handle loop
    if old in r['parts']:
        r['parts'].remove(old); r['meta'].pop(old); r['colors'].pop(old, None)
        for v in r['views'].values():
            if old in v: v.remove(old)
        for ext in ('.step', '.brep'): (d / (old + ext)).unlink(missing_ok=True)
        r.setdefault('excluded', {})[old] = 'obsolete: the handle moves to the rear plate with the rack mount (V44 fix list D4)'
    for n, s, g, k, manu, col, note in parts:
        if n not in r['parts']: r['parts'].append(n)
        r['meta'][n] = dict(group=g, kind=k, note=note[:400], manufacture=manu, demo_name='', source='build_v44_chassis.py (mock)')
        r['colors'][n] = col
        s.exportStep(str(d / (n + '.step'))); s.exportBrep(str(d / (n + '.brep')))
    shell = [n for n, s, g, *_ in parts if g == 'covers']
    base = [n for n, s, g, *_ in parts if g == 'base']
    for n, *_ in parts:
        if n not in r['views']['complete']: r['views']['complete'].append(n)
    r['views']['open'] = [n for n in r['views']['complete'] if n not in shell or n.startswith('V44_PRINT_pan')]
    if MOCK_SHELL: r['views']['handle'] = sorted(set(r['views']['handle'] + ['V44_PRINT_end_cap_motor_handle']))
    r['views']['io_access'] = [n for n in r['views']['complete'] if n != 'V44_PRINT_rear_IO_panel']
    r['views']['drivetrain'] = sorted(set(r['views']['drivetrain'] + base))
    r['allowances'] = [a for a in r.get('allowances', []) if a['name'] not in ALLOW] + [dict(name=n, note=t[:200], demo_name='') for n, (_, t) in ALLOW.items()]
    r['status'] = ('V44 phase 1d + fix list L1-L4 (battery saddles, back step for leads and rear I/O, square exit frame); base and shell being redesigned (fix list S/E).') if not MOCK_SHELL else ('V44 phase 1d + chassis mock: design layout rev 12 (176 mm drum shaft) as real CAD, plus a MOCK printed base on two aluminium flat bars '
                   'and a Nano-style shell in P2S pieces. Mock = looks, fit and interfaces only; load paths and seams not designed.')
    (d / 'revision.json').write_text(json.dumps(r, indent=1))
    with open(d / 'hardware.csv', 'w', newline='', encoding='utf-8') as fh:
        wr = csv.DictWriter(fh, fieldnames=['part', 'group', 'kind', 'size', 'source', 'note']); wr.writeheader(); wr.writerows(r['hardware'])
for n, (s, _) in ALLOW.items():
    s.exportStep(str(H / 'allowances' / (n + '.step'))); s.exportBrep(str(H / 'allowances' / (n + '.brep')))
print(json.dumps({k: v for k, v in report.items() if k != 'p2s_fit'}, indent=1))
print('P2S:', [(f['part'], f['size_mm'], f['fits_p2s']) for f in fit])
print('interfaces', len(I), '| parts now', len(REV['printed']['parts']))
