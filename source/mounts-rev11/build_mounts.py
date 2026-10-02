"""Rev 11 mounts: printed / stock supports for every part that was floating in the packing layout.

Authored in world coordinates of the design layout (make_design_layout.py): X along the shaft, Y front = -Y,
Z up, base top Z 0. Each part is exported as STEP (step/) and as a world mesh with its host group
(mounts.json); publish_mounts_rev11.py converts each mesh into its host group's model frame so it moves with
that group. Base-mounted parts start at Z 0.5 like the fairlead pedestals. Enclosure-wall interfaces (bosses,
inserts) stop at the envelope planes: back Y 1.5, front clearance plane Y -133.
Geometry review only: wall thicknesses and fasteners are first-pass, not load-qualified.
Rev 12 (176 mm drum shaft): coordinates below stay in the rev 11b world; each mount is moved with its host at export
(ODrive / fan / battery -24 mm in X, fuse saddles -17 mm, regulator standoffs +13 mm in Z). The ODrive bracket feet
and tie bar are redesigned for the tighter shaft end, and the phase-lead route is re-run (world rev 12 coordinates).
"""
from pathlib import Path
import json, math
import numpy as np
import front_boards as FB
import power_parts as PP
import cadquery as cq

HERE = Path(__file__).resolve().parent
OUT = HERE / 'step'; OUT.mkdir(exist_ok=True)
rows = []
PRINT, STOCK, FOAM, ROUTE = (.30, .55, .62), (.72, .74, .76), (.35, .35, .38), (.95, .55, .15)

def box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))
def cyl(r, p0, p1):
    p0, p1 = np.array(p0, float), np.array(p1, float); d = p1 - p0
    return cq.Solid.makeCylinder(r, float(np.linalg.norm(d)), cq.Vector(*p0), cq.Vector(*(d / np.linalg.norm(d))))
def hexpocket(af, depth, p, axis):   # hex nut pocket, flats across `af`, along +axis from p
    w = cq.Workplane(cq.Plane(origin=tuple(p), xDir=(0, 1, 0) if axis[0] else (1, 0, 0), normal=tuple(axis)))
    return w.polygon(6, af / math.cos(math.pi / 6)).extrude(depth).val()
DX12 = -24.0                                                   # rev 12: ODrive, fan, battery, BMS 24 mm toward the motor
# V44 fix list round 2 (September 28): the BMS moves to the right cover's ceiling (tray gone; the saddle bars hold the battery),
# the Pi moves to the left cover's ceiling (brackets on the motor plate gone), and the battery rear spacer becomes part of the right
# cover (L6/L7). Their geometry below is kept for history but no longer emitted.
ROUND2_DROP = {'MOUNT BMS tray + battery hold-down (printed PA-CF)', 'MOUNT Pi carrier brackets on the motor face plate (printed PA-CF)',
               'MOUNT battery rear spacer (printed)'}
def add(name, host, host_piece, group, s, col, role, material, boxes, contacts=(), move=(0, 0, 0), extra=None):
    """boxes: solid world boxes (x0,x1,y0,y1,z0,z1) for the page's collision check (holes ignored).
    host_piece: the part this mount bolts to; the design layout keeps the mount's pose relative to it.
    contacts: parts in other groups (or re-posed parts) this mount touches by design (screwed / clamped faces).
    move: rev 11b -> rev 12 world move of the host (applied to the solid and the boxes)."""
    if name in ROUND2_DROP: return
    assert s.isValid(), name
    if any(move):
        s = s.translate(cq.Vector(*move)); mx, my, mz = move
        boxes = [(x0 + mx, x1 + mx, y0 + my, y1 + my, z0 + mz, z1 + mz) for x0, x1, y0, y1, z0, z1 in boxes]
    s = s.clean(); s.exportStep(str(OUT / (name.replace('/', '-') + '.step')))   # '/' would become a folder
    v, t = s.tessellate(.05, .2); a = np.array([q.toTuple() for q in v])
    rows.append(dict(name=name, host=host, host_piece=host_piece, group=group, color=col, role=role, material=material,
                     collision_boxes=[list(map(float, bx)) for bx in boxes], contacts=list(contacts),
                     vertices=np.round(a, 4).ravel().tolist(), triangles=np.array(t).ravel().tolist(),
                     bounds=[*a.min(0).round(3), *a.max(0).round(3)], volume_mm3=round(s.Volume(), 1), extra=extra or {}))

# ---------- 1. ODrive Pro bracket (host: odrive) ----------
# Heat-spreader corner holes: 4 x d4.3 on a 60 x 60 square, Y -92.48/-32.48, Z 13.01/73.01, spreader -X face X 238.8 (rev 11b world).
# Rev 12: the right pillow block (to X 229 here) and shaft-2 pedestal 1 (X 227.5..232.5, Y < -97.9) now sit next to the posts,
# so the feet move: front foot toward the front (-Y), rear foot under the heat spreader (+X). Both take an M4 from below the
# base into a heat-set insert; the +-2 mm encoder-gap slot goes in the new base. Tie bar lowered to Z 12..18 (drum hub Z 25.1).
HY, HZ, XF = (-92.48, -32.48), (13.01, 73.01), 238.8
POSTS = ((-98.5, -88.5), (-37.5, -28.5))
FEET = ((XF - 5.5, XF + 3, -106.5, -98.5, 0.5, 5.5), (XF, XF + 12, -37.5, -28.5, 0.5, 5.5))   # front (-Y, 0.8 mm from pedestal 1), rear (+X, under the spreader)
INSERTS = ((XF - 1.25, -102.5), (XF + 8, -33.0))
TIE = (XF - 6, XF - 3, POSTS[0][1], POSTS[1][0], 12.0, 18.0)
BB = [TIE] + [(XF - 6, XF, y0, y1, 0.5, 76.5) for y0, y1 in POSTS] + list(FEET)
b = box(*TIE)
for (y0, y1), f in zip(POSTS, FEET):
    b = b.fuse(box(XF - 6, XF, y0, y1, 0.5, 76.5)).fuse(box(*f))
for (y0, y1), hy, (fx, fy) in zip(POSTS, HY, INSERTS):
    for hz in HZ:
        b = b.cut(cyl(2.15, (XF - 6.1, hy, hz), (XF + .1, hy, hz))).cut(hexpocket(7.2, 3.5, (XF - 6.01, hy, hz), (1, 0, 0)))
    # (round 13: the M3 pilot for the old BMS-tray lip at Z 66 is gone - the tray was retired, the hole was unused)
    b = b.cut(cyl(2.8, (fx, fy, 0.4), (fx, fy, 4.9)))                                          # M4 heat-set insert from below
add('MOUNT ODrive Pro bracket (printed PA-CF, base-mounted)', 'odrive', 'V3_ODrive_heat_spreader_SUPPLIER_CAD', 'frame', b, PRINT,
    'Two posts take the heat spreader on its 60 x 60 corner holes (M4 x 16 from the board side, nuts in hex pockets). '
    'Feet: front foot toward the front, rear foot under the heat spreader; each takes one M4 from under the base into a heat-set insert, '
    'through a +-2 mm base slot that sets the 1 mm encoder gap (1 mm shim, then tighten). Tie bar low (Z 12-18) under the drum hub; '
    'the motor phase leads pass under it and under the heat spreader.', 'PA-CF print', BB, move=(DX12, 0, 0))

# ---------- 2. BMS tray + battery hold-down (host: battery) ----------
T0, T1 = 77.0, 78.5                                           # BMS moved up 0.5: bottom Z 79
tray = box(231.3, 307.3, -127.2, -24.7, T0, T1).cut(box(238.1, 244.7, -98.5, -27.0, T0 - .1, T1 + .1))
for (y0, y1) in POSTS:                                        # lips down the post -X faces, M3 screw at Z 66
    lip = box(231.3, 232.8, y0, y1, 62.0, T0 + .01).cut(cyl(1.7, (231.2, (y0 + y1) / 2, 66), (232.9, (y0 + y1) / 2, 66)))
    tray = tray.fuse(lip)
# V44 fix L3: no hold-down ribs; the tray is the lid of the two battery saddles and rests on their top bars (Z 77).
for x in (250.0, 275.0, 293.0):                                # tie slots for the BMS strap (BMS unchanged)
    for y in (-125.0, -29.0):
        tray = tray.cut(box(x, x + 3, y, y + 2.5, T0 - .1, T1 + .1))
TB = [(231.3, 238.1, -127.2, -24.7, T0, T1), (238.1, 244.7, -127.2, -98.5, T0, T1), (238.1, 244.7, -27.0, -24.7, T0, T1),
      (244.7, 307.3, -127.2, -24.7, T0, T1)] + [(231.3, 232.8, y0, y1, 62.0, T0) for y0, y1 in POSTS]
add('MOUNT BMS tray + battery hold-down (printed PA-CF)', 'battery', 'CATALOG_stock-battery-fit', 'frame', tray, PRINT,
    'Carries the JBD BMS (strapped through the tie slots, 0.5 mm below it). Lid of the two battery saddles: rests on and screws to their top bars (V44 fix L3). '
    'Screwed to the ODrive bracket posts by two lips (M3 at Z 66). Open over the heat-spreader edge so the BMS never touches it.', 'PA-CF print', TB,
    ['MOUNT ODrive Pro bracket (printed PA-CF, base-mounted)', 'MOUNT battery saddle front (printed PA-CF)', 'MOUNT battery saddle rear (printed PA-CF)'], move=(DX12, 0, 0))
# V44 fix L3: two U-saddles the stacked pouches drop into (front Y -124..-114, rear Y -16..-6; rev 11b X here, moved with the battery).
# Side walls 2.5 mm; the +X walls stand 2.5 mm past the pack (the box grows 2.5 mm). The rear saddle's -X wall starts at Z 29, above
# the fuse-lead allowance. Top bars press the stack through 1 mm foam; the BMS tray rests on the bars. Fixing to the bottom plate: S6.
SAD = (('front', -124.0, -114.0, 0.5), ('rear', -16.0, -6.0, 29.0))
BX0, BX1, BZ1 = 268.5, 307.5, 68.5                              # pack (rev 11b X), top of the stack
SCL, LEAD = 0.5, 1.5                                             # round 13: slide clearance per side, 45 deg lead-in at the entry (front) face
def _lead_in(sd, x_in, y0, z0, z1, sgn):
    """Chamfer the inner vertical edge of a side wall at the entry face (the packs slide in from the front, +Y)."""
    tri = cq.Workplane('XY', origin=(0, 0, z0 - 0.1)).polyline([(x_in, y0 - 0.1), (x_in + sgn * (LEAD + 0.1), y0 - 0.1), (x_in, y0 + LEAD + 0.1)]).close()         .extrude(z1 - z0 + 0.2).val()
    return sd.cut(tri)
for tag, y0, y1, zmin in SAD:
    xl, xr = BX0 - SCL, BX1 + SCL                                    # tunnel inner faces
    sb = [(xl - 2.5, xl, y0, y1, zmin, 77.0), (xr, xr + 2.5, y0, y1, 0.5, 77.0), (xl - 2.5, xr + 2.5, y0, y1, BZ1 + 1.0, 77.0)]
    sd = None
    for bx in sb: sd = box(*bx) if sd is None else sd.fuse(box(*bx))
    sd = _lead_in(_lead_in(sd, xl, y0, zmin, BZ1 + 1.0, -1), xr, y0, 0.5, BZ1 + 1.0, 1)
    top_lead = cq.Workplane('YZ', origin=(xl - 2.6, 0, 0)).polyline([(y0 - 0.1, BZ1 + 0.9), (y0 + LEAD + 0.1, BZ1 + 0.9), (y0 - 0.1, BZ1 + 1.0 + LEAD + 0.1)]).close()         .extrude(xr - xl + 5.2).val()
    sd = sd.cut(top_lead)                                            # lead-in on the top bar's entry edge too
    add(f'MOUNT battery saddle {tag} (printed PA-CF)', 'battery', 'CATALOG_stock-battery-fit', 'frame', sd, PRINT,
        'U-saddle the stacked TP2700 pouches slide into from the front (V44 fix L3; round 13: 0.5 mm slide clearance per side, 1.5 mm 45 deg lead-in): side walls hold the stack in X, the top bar presses it down through 1 mm foam, '
        'the BMS tray screws on top. Replaces the tray ribs that cantilevered from the ODrive posts. Fixing to the bottom plate is item S6.', 'PA-CF print', sb,
        ['CATALOG_TP_module_B', 'MOUNT BMS tray + battery hold-down (printed PA-CF)'], move=(DX12, 0, 0))
foam = box(BX0, BX1, SAD[0][1], SAD[0][2], BZ1, BZ1 + 1.0).fuse(box(BX0, BX1, SAD[1][1], SAD[1][2], BZ1, BZ1 + 1.0))
add('MOUNT battery hold-down foam 2 mm (EVA)', 'battery', 'CATALOG_stock-battery-fit', 'frame', foam, FOAM, '1 mm EVA pads under the two saddle top bars; spread the clamp load on the pouch tops.', '1 mm EVA foam',
    [(BX0, BX1, y0, y1, BZ1, BZ1 + 1.0) for _, y0, y1, _ in SAD], ['CATALOG_TP_module_B', 'MOUNT battery saddle front (printed PA-CF)', 'MOUNT battery saddle rear (printed PA-CF)'], move=(DX12, 0, 0))
add('MOUNT battery separator foam 2 mm (EVA)', 'battery', 'CATALOG_stock-battery-fit', 'frame', box(268.5, 307.5, -132.5, -3.5, 33.5, 35.5), FOAM,
    'Fills the 2 mm gap between modules A and B; lets the pouches swell a little.', '2 mm EVA foam', [(268.5, 307.5, -132.5, -3.5, 33.5, 35.5)], ['CATALOG_TP_module_B'], move=(DX12, 0, 0))
add('MOUNT battery rear spacer (printed)', 'battery', 'CATALOG_stock-battery-fit', 'frame',
    box(270.0, 306.0, -3.5, 1.5, 3.0, 66.0).cut(box(276.0, 300.0, -3.6, 1.6, 10.0, 59.0)), PRINT,
    'Frame between the modules and the back wall: holds the stack forward against the front wall (1 mm foam there). Window saves plastic.', 'PA-CF print',
    [(270.0, 276.0, -3.5, 1.5, 3.0, 66.0), (300.0, 306.0, -3.5, 1.5, 3.0, 66.0), (276.0, 300.0, -3.5, 1.5, 3.0, 10.0), (276.0, 300.0, -3.5, 1.5, 59.0, 66.0)], ['CATALOG_TP_module_B'], move=(DX12, 0, 0))

# ---------- 3. Fan duct / mount (host: fan) ----------
FC = (235.0, 58.0)
duct = box(215.0, 255.0, -9.8, 1.5, 38.0, 78.0).cut(cyl(18.5, (FC[0], -9.9, FC[1]), (FC[0], 1.6, FC[1])))
for dx in (-16, 16):
    for dz in (-16, 16):
        duct = duct.cut(cyl(1.7, (FC[0] + dx, -9.9, FC[1] + dz), (FC[0] + dx, 1.6, FC[1] + dz)))
add('MOUNT fan duct / mount frame (printed)', 'fan', 'TRIAL_driver_fan', 'frame', duct, PRINT,
    'Fills the 10 mm fan-face clearance: sealed duct from the back-wall vent to the fan, 4 x M3 x 30 through the fan (32 mm pattern) into back-wall inserts.', 'PETG or PA-CF print',
    [(215.0, 255.0, -9.8, 1.5, 38.0, 78.0)], move=(DX12 + 10.0, 0, 0))      # round 8: +10 with the fan

# ---------- 4. Pi carrier brackets on the motor face plate (host: drivetrain) ----------
pi = None; PB = []
for (y0, y1) in ((-107.5, -100.5), (-28.3, -21.5)):
    p = box(10.0, 13.0, y0, y1, 40.0, 63.0).fuse(box(10.0, 20.0, y0, y1, 61.0, 63.0)); PB += [(10.0, 13.0, y0, y1, 40.0, 63.0), (13.0, 20.0, y0, y1, 61.0, 63.0)]
    for z in (46.0, 56.0): p = p.cut(cyl(1.7, (9.9, (y0 + y1) / 2, z), (13.1, (y0 + y1) / 2, z)))
    p = p.cut(cyl(1.1, (16.5, (y0 + y1) / 2, 60.9), (16.5, (y0 + y1) / 2, 63.1)))
    pi = p if pi is None else pi.fuse(p)
add('MOUNT Pi carrier brackets on the motor face plate (printed PA-CF)', 'drivetrain', 'V43_METAL_motor_face_4mm', 'frame', pi, PRINT,
    'Two L-brackets on the 4 mm motor plate (2 x M3 tapped in the plate each) carry the Pi carrier edge (M2.5 into the flange, 0.5 mm shim). '
    'The carrier also screws to the left pillow-block housing top (2 x M3 heat-set inserts, X 71, 0.5 mm shim).', 'PA-CF print', PB)

# ---------- 5. Screen rear retaining frame (host: screen), screen centred in the front-left panel ----------
# LCD board behind the glass (from supplier CAD, after the centring move): X -27.0..52.4, Z -0.35..78.15, board back at Y -128.0.
BX, BZ, BY = (-27.0, 52.4), (0.5, 78.15), -128.0
fr = box(BX[0], BX[1], BY, BY + 3, BZ[0], BZ[1]).cut(box(BX[0] + 4, BX[1] - 4, BY - .1, BY + 3.1, 3.65, BZ[1] - 4))
ZC = 38.9
SB = [(BX[0], BX[1], BY, BY + 3, BZ[0], 3.65), (BX[0], BX[1], BY, BY + 3, BZ[1] - 4, BZ[1]), (BX[0], BX[0] + 4, BY, BY + 3, BZ[0], BZ[1]), (BX[1] - 4, BX[1], BY, BY + 3, BZ[0], BZ[1])]
for xa, xb, o in ((BX[0] - 10, BX[0], -0.5), (BX[1], BX[1] + 10, 0.5)):   # legs 0.5 mm clear of the LCD module sides
    SB += [(xa + o, xb + o, -133.0, BY, ZC - 8, ZC + 8), (xa, xb, BY, BY + 3, ZC - 8, ZC + 8)]
    xm = -35.0 if xa < 0 else 60.0                                            # R4-8: over wall material beside the screen window (M3 x 20 from the front)
    tab = box(xa + o, xb + o, -133.0, BY, ZC - 8, ZC + 8).fuse(box(xa, xb, BY - .01, BY + 3, ZC - 8, ZC + 8))
    fr = fr.fuse(tab.cut(cyl(1.7, (xm, -133.1, ZC), (xm, BY + 3.1, ZC))))
add('MOUNT screen rear retaining frame (printed)', 'screen', 'TRIAL_Waveshare_DSI_E_portrait', 'frame', fr, PRINT,
    'Presses the LCD board into the front-wall window from behind (4 mm border clears the 40-pin socket). '
    'Two legs to the front wall: M3 x 20 into wall inserts. Bottom edge stops at Z 0.5; the base needs a front notch under the glass (Z -3.35 with the bezel).', 'PETG print', SB)

# ---------- 6. Board standoffs to the back wall (hosts: teensy, TRIAL_CAN_headers, regulator) ----------
def standoffs(name, host, host_piece, x, z, y0, move=(0, 0, 0)):
    # round 6: built at the round 5 pose (far ends on the rear plate face, Y 2.5), then carried with the board to the front plate
    s = None; bx = []
    for xx in x:
        for zz in z:
            p0, p1 = (FB.world(host, np.array(q) + move) for q in ((xx, y0, zz), (xx, 2.5, zz)))
            u = (p1 - p0) / np.linalg.norm(p1 - p0)
            c = cyl(2.5, p0, p1).cut(cyl(1.25, p0 - .1 * u, p1 + .1 * u))
            s = c if s is None else s.fuse(c)
            lo, hi = np.minimum(p0, p1), np.maximum(p0, p1)
            bx.append((lo[0] - 2.5, hi[0] + 2.5, lo[1], hi[1], lo[2] - 2.5, hi[2] + 2.5))
    add(name, host, host_piece, 'frame', s, STOCK, 'M2.5 standoffs from the perfboard corners to inserts in the front board plate (round 6).', 'M2.5 nylon/brass standoffs', bx,
        contacts=('MOUNT front board plate (printed)',))
standoffs('MOUNT Teensy perfboard standoffs', 'teensy', 'TRIAL_Teensy', (94.5, 129.1), (52.5, 69.3), -8.2, move=(-144.0, 0, -2.0))   # R4-5: behind the motor          # rev 11b: behind the drum
standoffs('MOUNT CAN board perfboard standoffs', 'TRIAL_CAN_headers', 'TRIAL_CAN_headers', (94.5, 125.9), (1.5, 10.7), -3.5, move=(-166.0, 0, 5.0))   # round 5: board vertical, Z 4..18.2, 6 mm standoffs
standoffs('MOUNT regulator perfboard standoffs', 'regulator', 'TRIAL_Pololu5571', (136.5, 160.9), (19.5, 43.9), -7.6, move=(-138.0, 0, 11.0))   # rev 12: board +13 mm up

# ---------- 7. Fuse holder cradles (round 11: under the fan and the WAGO; host: drivetrain; rev 12 world) ----------
add('MOUNT fuse holder saddles (printed, base-mounted)', 'drivetrain', 'V43_METAL_motor_face_4mm', 'frame', PP.cradles(), PRINT,
    'Two cradles under the Littelfuse holder body, cable tie through the side slot, each with one M3 into the base. Round 11: under the fan '
    'and the WAGO (the back wall steps in behind the drum).', 'PETG print', [(x, x + 5, PP.FUSE_C[1] - 11.0, PP.FUSE_C[1] + 11.0, 0.5, 14.5) for x in PP.CRADLES_X],
    contacts=('PART Littelfuse MIDI holder + 40 A fuse',))
_h, _fz = PP.fuse_holder()
add('PART Littelfuse MIDI holder + 40 A fuse', 'drivetrain', 'V43_METAL_motor_face_4mm', 'frame', _h.fuse(_fz), (.25, .25, .27),
    'Littelfuse 04980921GXM5 58 V inline MIDI holder (manufacturer STEP) with the BF1 142.5631.5402 40 A fuse on its M5 studs. Round 11: under '
    'the fan and the WAGO; battery + on the line stud (charge branch too), ODrive DC+ and the regulator branch on the load stud.', 'Buy: Littelfuse',
    [(b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax) for b in (_h.BoundingBox(), _fz.BoundingBox())], contacts=('MOUNT fuse holder saddles (printed, base-mounted)',))
FL2 = [(181.5, 193.3, -21.5, -1.5, 0.5, 28.0), (236.7, 244.0, -21.5, -1.5, 0.5, 28.0)]   # round 11: holder under the fan
add('RESERVE fuse holder leads', 'drivetrain', 'V43_METAL_motor_face_4mm', 'reserve', box(*FL2[0]).fuse(box(*FL2[1])), ROUTE,
    'Ring terminals, 10 AWG turns and heat shrink at both ends of the fuse holder (round 11: under the fan).', 'wiring allowance', FL2)
BL = (199.5, 275.5, -24.0, -4.0, 79.0, 92.0)
add('RESERVE BMS leads (back)', 'drivetrain', 'V43_METAL_motor_face_4mm', 'reserve', box(*BL), ROUTE,
    'BMS balance / power leads along the back above the battery (round 9: starts past the zone-B step).', 'wiring allowance', [BL])

# ---------- 8. Motor phase-lead route (host: drivetrain; rev 12 world) ----------
# Rev 12: the ODrive terminal block's wiring space is in front of the block (X 222..241.6, Y < -97.4). The leads run behind the
# pillow blocks, squeeze past the right pillow block (X 205..208.8, stacked 3 high), cross between the bracket posts under the
# tie bar, then run flat under the heat spreader (Z < 8) to the front edge of the board.
# V44 (September 28): the leads now start at the motor's provisional lead-exit endcap (X 3): through a 12 mm grommet hole in the
# 4 mm face plate (X 6..10, the gap between the first two boxes), above motor bolt 3 and the rear gusset, down behind the left pillow block
# (X 41.5..50.5) and into the old channel, which now starts at X 41.5.
RT = [(3.5, 5.5, -36.5, -28.8, 49.0, 60.0), (10.5, 41.0, -36.5, -28.8, 49.0, 60.0), (41.5, 50.5, -35.5, -27.5, 4.0, 60.0),
      (41.5, 206.0, -35.5, -27.5, 4.0, 15.0), (205.3, 208.5, -40.0, -27.0, 1.0, 37.6), (205.3, 222.0, -27.4, -17.0, 28.8, 37.6)]
# Round 6: the ODrive is turned 180 deg about the shaft axis (headers to the front), so its terminal block is at the back
# (X 222..244, Y -38..-28.5, Z 24..62). The leads rise between the right pillow block and the bracket post, then run over the
# fuse holder and under the fan to the terminal wiring space; no more squeeze under the heat spreader.
route = None
for bx in RT: route = box(*bx) if route is None else route.fuse(box(*bx))
add('ROUTE motor phase leads 8 x 11 mm channel', 'drivetrain', 'V43_METAL_motor_face_4mm', 'reserve', route, ROUTE,
    'Three phase wires from the motor end to the ODrive terminal block (at the back since round 6): along the back floor behind the '
    'pillow blocks, up between the right pillow block and the bracket post, then over the fuse holder and under the fan into the '
    'terminal wiring space. At the motor end the leads leave the provisional lead-exit endcap, pass a 12 mm grommet hole in the '
    'face plate (X 8, Y -34, Z 54.5, 12 mm, above motor bolt 3), cross over the rear gusset and drop behind the left pillow block. Confirm the owned motor lead exit.', 'wiring allowance', RT)

# ---------- 8b. Round 6: ODrive terminal wiring at the back (host: odrive; rev 12 world) ----------
# DC leads rise from the fuse holder's output end (X ~243) and the phase leads arrive over the fuse holder; both turn into the
# terminal block's wire entries (its +Y face, Y -28.5). Kept under the fan (Z < 38 next to it) and short of the battery saddle.
TW = [(222.1, 243.8, -28.4, -22.5, 28.8, 62.0)]                 # round 8: DC+ comes from the holder load stud (X 213) under it; beside-fan space dropped
add('RESERVE ODrive terminal wiring (back)', 'odrive', 'V3_ODrive_heat_spreader_SUPPLIER_CAD', 'reserve', box(*TW[0]), ROUTE,
    'DC and phase ferrules, wire turns and screwdriver access at the ODrive terminal block, which faces the back since the ODrive was turned '
    'so its headers face the front (round 6). Insulation OD and bend radius still to confirm.', 'wiring allowance', TW)

# ---------- 8c. Round 6: front board plate + board lead spaces + lane to the Pi, BMS and ODrive (host: drivetrain; rev 12 world) ----------
PL = FB.PLATE
plate = box(*PL['x'], *PL['y'], *PL['z']).fuse(box(*PL['x'], *PL['foot_y'], *PL['foot_z']))
plate = cq.Workplane().add(plate).edges('|Y and >Z').fillet(4.0).val()
holes = []
for host, xs, zs, y0, mv in (('teensy', (94.5, 129.1), (52.5, 69.3), -8.2, (-144.0, 0, -2.0)),
                             ('TRIAL_CAN_headers', (94.5, 125.9), (1.5, 10.7), -3.5, (-166.0, 0, 5.0)),
                             ('regulator', (136.5, 160.9), (19.5, 43.9), -7.6, (-138.0, 0, 11.0))):
    for xx in xs:
        for zz in zs:
            q = FB.world(host, np.array((xx, 2.5, zz)) + mv); holes.append(cyl(1.8, (q[0], PL['y'][0] - .1, q[2]), (q[0], PL['y'][1] + .1, q[2])))
holes += [cyl(2.0, (x, y, PL['foot_z'][0] - .1), (x, y, PL['foot_z'][0] + 4.4)) for x, y in FB.PLATE_SCREWS]
for h in holes: plate = plate.cut(h)
add('MOUNT front board plate (printed)', 'drivetrain', 'V43_METAL_motor_face_4mm', 'frame', plate, PRINT,
    'Round 6: upright plate at the front-left corner, left of the screen and in front of the motor. Teensy (left, USB up), CAN board (right, '
    'terminal up) and regulator (low, across) stand on M2.5 standoffs into its heat-set inserts, components facing the motor. '
    'Foot: 2 x M3 up through the bottom plate into inserts.', 'PETG print', [(*PL['x'], *PL['y'], *PL['z']), (*PL['x'], *PL['foot_y'], *PL['foot_z'])])
FL = [(-77.0, -55.2, -124.0, -108.0, 78.0, 92.0),        # Teensy USB plug + cable, up out of its top end
      (-77.0, -55.2, -109.6, -103.5, 38.0, 77.6),        # Teensy header leads in front of its components
      (-54.7, -38.6, -124.0, -105.5, 75.0, 92.0),        # CAN board terminal + Teensy-CAN leads, above the CAN board
      (-47.3, -38.6, -124.0, -104.0, 6.0, 35.0)]         # regulator in/out leads beside it
fl = None
for bx in FL: fl = box(*bx) if fl is None else fl.fuse(box(*bx))
add('RESERVE front board leads', 'drivetrain', 'V43_METAL_motor_face_4mm', 'reserve', fl, ROUTE,
    'Round 6: Teensy USB (up, to the Pi), Teensy header leads, CAN board terminal and the regulator leads at the front board plate.', 'wiring allowance', FL)
LN = [(-38.4, 3.0, -132.0, -117.3, 84.0, 91.0),          # over the screen, left of the Pi (round 12: the Pi now reaches over the screen top)
      (-35.0, 3.0, -117.3, -27.0, 84.0, 91.0),          # round 12: over the motor, back to behind the Pi (round 13: clear of the 8 mm cover-screw boss)
      (3.0, 80.0, -26.0, -20.6, 78.0, 85.8),            # round 12: behind the Pi's USB plugs (inside the zone-A back wall, no bump), under the cover screw bosses
      (70.0, 200.0, -45.0, -27.0, 81.0, 89.0),          # round 12: over the drum to the WAGO and fuses at the fan
      (70.0, 85.5, -117.3, -27.0, 80.0, 91.0),          # round 8: beside the Pi (round 11: clear of the zone-B cover fillet)
      (64.0, 100.0, -132.0, -117.3, 84.0, 91.0),        # round 12: from beside the Pi to the front lane
      (100.0, 241.0, -132.0, -127.5, 80.0, 91.0),        # over the fairlead and shaft 2, in front of the BMS
      (235.1, 241.0, -132.0, -127.5, 50.0, 80.0),        # down in front of the BMS
      (235.1, 241.0, -127.5, -97.0, 50.0, 78.2),         # back under the BMS, beside the battery connections
      (231.6, 241.0, -97.0, -81.0, 50.0, 72.0)]          # into the ODrive's CAN header plugs (front edge since round 6)
ln = None
for bx in LN: ln = box(*bx) if ln is None else ln.fuse(box(*bx))
add('ROUTE front board leads to the Pi, BMS and ODrive', 'drivetrain', 'V43_METAL_motor_face_4mm', 'reserve', ln, ROUTE,
    'Lanes: over the screen and the motor to behind the Pi (Teensy USB to its ports), over the drum to the WAGO / fuses, and along the top front for the CAN pair '
    'down to the ODrive CAN header (now on its front edge).', 'wiring allowance', LN)

# ---------- 8d. Round 7: real power-path parts (vendor STEPs; host: drivetrain; rev 12 world) ----------
add('PART WAGO 221-615 negative junction', 'drivetrain', 'V43_METAL_motor_face_4mm', 'frame', PP.wago(), (.9, .55, .2),
    'WAGO 221-615 5-port lever nut, 10 AWG: the P- junction (BMS P-, ODrive DC-, regulator -, charge port -). Datasheet size '
    '36.7 x 10.1 x 21.1 mm (WAGO CAD is portal-gated). Clipped on the junction bracket.', 'Buy: WAGO 221-615', [PP.WAGO],
    contacts=('MOUNT power junction bracket (printed)',))
add('MOUNT power junction bracket (printed)', 'drivetrain', 'V43_METAL_motor_face_4mm', 'frame', PP.bracket(), PRINT,
    'Holds the WAGO upright (shelf + cable ties through slots) against the rear plate; round 11: right beside the fan, over the fuse holder. 2 x M3 into rear-plate inserts.', 'PETG print',
    [(PP.BRACKET['x'][0], PP.BRACKET['x'][1], PP.BRACKET['y'][0], PP.BRACKET['y'][1], PP.BRACKET['z'][0], PP.BRACKET['z'][1]),
     (PP.WAGO[0] - 1.0, PP.BRACKET['x'][1], PP.WAGO[2] - 1.0, PP.BRACKET['y'][0], PP.BRACKET['z'][0], 30.4)])   # shelf
_x60 = PP.xt60ef()
add('PART XT60E-F charge port', 'battery', 'CATALOG_stock-battery-fit', 'frame', _x60, (.85, .75, .15),
    'AMASS XT60E-F female panel socket (Marathon OS STEP scaled to the Amass size), flange flush in a pocket of the rear I/O panel, '
    '2 x M2.5 into the panel backing. Female so the live contacts are recessed; the Luna charger plug is XT60 male.', 'Buy: Amass XT60E-F',
    PP.bboxes(_x60), extra=dict(back_step=True))

# ---------- 9. V44 fix L1: battery leads and rear I/O in a back step at the battery end (host: battery; rev 12 world) ----------
# The pouch leads leave the rear end faces (the front faces are 0.5 mm from the wall), pass the rear-spacer window, bend in a 14 mm
# deep step of the back wall and come back in over the spacer to the BMS wiring. The rear I/O panel on the step carries the charge
# port and the power switch (decision D7). The page counts these as a local back step, not as a deeper box.
LB = [(252.0, 262.0, -3.5, 16.0, 10.0, 59.0), (252.0, 262.0, 2.5, 16.0, 59.0, 89.0), (252.0, 262.0, -4.0, 2.5, 66.5, 89.0)]
lb = None
for bx in LB: lb = box(*bx) if lb is None else lb.fuse(box(*bx))
add('ROUTE battery leads to the rear step', 'battery', 'CATALOG_stock-battery-fit', 'reserve', lb, ROUTE,
    'TP2700 main (10 AWG) and balance leads: out of the rear end faces through the rear-spacer window, bend in the back-wall step (14 mm deep), '
    'up and back in over the spacer to the BMS wiring.', 'wiring allowance', LB, ['MOUNT battery rear spacer (printed)', 'CATALOG_TP_module_B'], extra=dict(back_step=True))
IO = [(263.0, 273.0, 2.5, 17.4, 40.5, 55.2), (262.5, 273.5, -2.5, 0.2, 60.0, 85.0)]      # round 7: switch (Z 47) + charge-port leads behind the real XT60E-F
add('RESERVE rear I/O: charge port + power switch', 'battery', 'CATALOG_stock-battery-fit', 'reserve', box(*IO[0]).fuse(box(*IO[1])), ROUTE,
    'Behind the flush rear I/O panel on the back step: the 12 mm latching power switch (Z 47, drives the BMS soft switch) and the '
    'charge-port leads behind the real XT60E-F (round 7). Decision D7.', 'service allowance', IO, extra=dict(back_step=True))

json.dump(dict(parts=rows), open(HERE / 'mounts.json', 'w'))
for r in rows:
    b = r['bounds']; print(f"{r['name'][:62]:62s} {r['host']:<34} X {b[0]:7.1f}..{b[3]:6.1f} Y {b[1]:7.1f}..{b[4]:6.1f} Z {b[2]:6.1f}..{b[5]:5.1f}  {r['volume_mm3']:8.0f} mm3")
