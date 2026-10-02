"""V44 wiring harness in CAD (round 10): every wire of the power path, motor, charging, 5 V, CAN, USB, balance, NTC, switch
and the display ribbon, as solid wires (insulation OD) routed through the enclosure. Run after build_v44_shell.py.

Each wire runs from a fixed lead-out at one terminal to a fixed lead-in at the other; wire_router.py finds the path between
(free space only, clear of turning parts, preferring the page's wiring lanes) and straightens it. The terminals are the
modelled parts: TB005 wire entries (ODrive), WAGO 221-615 ports, Littelfuse holder ends, XT60E-F solder cups, BMS pads and
headers (mock positions), board pins. Small bought parts that live on the harness are modelled as simple bodies (HARNESS_*):
the two inline MINI fuse holders, the 12 mm power switch, plugs, the NTC probe. Every wire is checked exactly against every
part and every other wire; the result is in wires-report.json. The wires join both variants' revision.json (group 'wiring').

Positions that are still assumptions are listed in each note (motor lead gauge, TB005 pole order, BMS pad / header spots,
pack lead exits). They are easy to move here: change the terminal point and re-run.
"""
from pathlib import Path
import json, time
import numpy as np
import cadquery as cq
import v44cache as VC
import wire_router as WR
import wire_clips as WC                                  # round 13: loops under the cover top for the two main passages

HERE = Path(__file__).resolve().parent
T0 = time.time()
V = cq.Vector
def box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
def cyl(r, a, b):
    a, b = np.asarray(a, float), np.asarray(b, float); d = b - a
    return cq.Solid.makeCylinder(r, float(np.linalg.norm(d)), V(*a), V(*(d / np.linalg.norm(d))))

# ---------------------------------------------------------------- terminals (world mm; X shaft, -Y front, Z up)
TB_X, TB_FACE = 229.3, -27.1                                   # TB005 wire entries (5 poles, 7.62 mm): open toward the back
TB_Z = [28.1, 35.7, 43.3, 50.9, 58.55]                          # pole 1..5 from the bottom; order DC+, DC-, A, B, C to confirm on the board
WG_X, WG_FACE = 195.45, -24.5                                  # WAGO 221-615 upright beside the fan, entries on its front face
WG_Z = [34.17, 41.51, 48.85, 56.19, 63.53]
FH = dict(line=193.6, load=236.4, z=16.8, y=(-15.0, -7.0))      # Littelfuse holder under the fan: wire openings at both ends (Z 13.8..20.6)
BAT = dict(face=-3.4, A=17.0, B=55.0)                          # pack end faces (rear) and lead-exit heights (TP2700: leads + balance lead at one end)
BX = dict(neg=256.0, pos=263.0, bal=271.5)                     # lead exits across the lower window of the rear spacer rib (X 252..276, Z 10..59)
BMS_PAD_Z, BMS_HDR_Z = 87.8, 82.8                              # JBD mock: pads and headers hang under the board (components down)
REG = dict(x=-47.4, y=-118.8)                                  # regulator perfboard screw terminals, +X edge
def reg(z): return [(REG['x'], REG['y'], z), (REG['x'] + 3.0, REG['y'], z)]
def out(p, d, L=3.0): p = np.asarray(p, float); return [tuple(p), tuple(p + np.asarray(d, float) * L)]

# ---------------------------------------------------------------- harness parts (bought, modelled as simple bodies)
HARNESS = {
    'HARNESS_inline_MINI_fuse_holder_7.5A_charge': (box(200.0, 240.0, -17.6, -4.6, 80.0, 89.0), (.15, .15, .15),   # round 13: clear of the 8 mm cover-screw bosses
        'VANTRONIK inline MINI (ATM) fuse holder with cover, 16 AWG, 7.5 A 58 V Littelfuse 997 fuse: charge port + to the main fuse line stud. '
        'Body size approximate (no CAD); lies along the back top channel over the fan, tie-wrapped.'),
    'HARNESS_inline_MINI_fuse_holder_3A_regulator': (box(150.0, 190.0, -37.5, -28.5, 81.0, 90.0), (.15, .15, .15),
        'VANTRONIK inline MINI (ATM) fuse holder with cover, 3 A 58 V Littelfuse 997 fuse: main fuse load stud to the 5 V regulator. '
        'Body size approximate (no CAD); lies along the top over the drum bearing, clear of the drum, tie-wrapped.'),
    'HARNESS_12mm_latching_power_switch': (cyl(6.0, (268, 2.6, 47), (268, 14.35, 47)).fuse(cyl(7.5, (268, 12.35, 47), (268, 14.35, 47)))
        .fuse(box(265.1, 265.9, 0.4, 2.7, 45.5, 48.5)).fuse(box(270.1, 270.9, 0.4, 2.7, 45.5, 48.5)), (.6, .6, .62),
        '12 mm latching push switch (body, nut and solder tags; size typical, no CAD) in the flush rear I/O panel. Drives the BMS soft-switch input.'),
    'HARNESS_NTC_probe_on_pack_B': (cyl(1.4, (257.0, -2.0, 42.0), (263.0, -2.0, 42.0)), (.1, .1, .1),
        'BMS NTC probe (10 k), taped to the rear end face of pack B, in the spacer window.'),
    'HARNESS_micro_USB_right_angle_plug': (box(-71.4, -60.9, -116.6, -109.6, 75.7, 86.5), (.12, .12, .12),
        'Right-angle micro-USB plug in the Teensy (cable leaves sideways: there is 18 mm above the Teensy).'),
    'HARNESS_USB_A_right_angle_plug': (box(44.5, 60.5, -37.5, -25.5, 82.5, 90.5), (.12, .12, .12),
        'Right-angle USB-A plug in the Pi\'s upper USB port (cable leaves sideways); inside the back wall since the Pi moved 15 mm toward the screen (round 12).'),
    'HARNESS_JST_GH_CAN_plug': (box(231.3, 236.5, -94.5, -82.7, 54.6, 59.6), (.9, .9, .88),
        'CAN plug on the ODrive CAN header (JST-GH 4-pin on the ODrive Pro; body size approximate).'),
    'HARNESS_Dupont_1x3_Pi_power': (box(59.3, 61.9, -108.6, -101.0, 67.2, 77.2), (.1, .1, .1),
        '1 x 3 Dupont housing on the Pi GPIO pins 2 (5 V), 4 and 6 (GND), from below; the Pi is powered from the regulator here.'),
}

# ---------------------------------------------------------------- wires: (id, OD, colour, lead-out A, lead-in B, vias, contacts, note)
RED, BLK, WHT = (.78, .1, .08), (.07, .07, .07), (.93, .93, .9)
PH = {'A': (.95, .7, .1), 'B': (.16, .4, .82), 'C': (.2, .62, .28)}
W = []
def wire(i, od, col, a, b, contacts, note, via=(), group=None):
    W.append(dict(id=i, od=od, color=col, group=group, a=[tuple(map(float, p)) for p in a], b=[tuple(map(float, p)) for p in b],
                  via=[tuple(map(float, p)) for p in via], contacts=list(contacts), note=note))

TB, WG = 'SameSky_TB005-762-05BE_ODrive_terminal', 'PART_WAGO_221-615_negative_junction'
HOLD, BMS = 'Littelfuse_04980921GXM5_holder', 'JBD_SP17S005_BMS_mock_from_spec'
PA, PB = 'ThunderPower_TP2700-5SR70_module_A_mock', 'ThunderPower_TP2700-5SR70_module_B_mock'
def tb(k): return out((TB_X, TB_FACE - 0.1, TB_Z[k]), (0, 1, 0), 2.5)
def wg(k): return out((WG_X, WG_FACE - 0.1, WG_Z[k]), (0, -1, 0), 4.0)
def pack(x, m): return out((x, BAT['face'], BAT[m]), (0, 1, 0), 6.5)   # through the 6 mm spacer rib into the step
def pad(y): return out((250.5, y, BMS_PAD_Z), (0, 0, -1), 6.0)
def hdr(x, y, L=4.0): return out((x, y, BMS_HDR_Z), (0, 0, -1), L)

# power path (10 AWG silicone, OD 5.0)
wire('WIRE_pack_plus_B+_to_fuse_line_10AWG', 5.0, RED, pack(BX['pos'], 'B'), out((FH['line'], FH['y'][0], FH['z']), (-1, 0, 0), 5.0), [PB, HOLD],
     'Pack B+ (EC5 on the pack lead) to the main fuse line stud (ring terminal inside the holder).')
wire('WIRE_series_link_A+_to_B-_10AWG', 5.0, RED, pack(BX['pos'], 'A'), pack(BX['neg'], 'B'), [PA, PB],
     'Series link between the two 5S packs (EC5 pair), in the back step.')
wire('WIRE_pack_minus_A-_to_BMS_B-_10AWG', 5.0, BLK, pack(BX['neg'], 'A'), pad(-33.9), [PA, BMS],
     'Pack A- (EC5) to the BMS B- pad (soldered; pad position is the mock\'s).')
wire('WIRE_ODrive_DC+_from_fuse_load_10AWG', 5.0, RED, out((FH['load'], FH['y'][0], FH['z']), (1, 0, 0), 5.0), tb(0), [HOLD, TB],
     'Main fuse load stud to ODrive DC+ (TB005 pole 1; ferrule).')
wire('WIRE_ODrive_DC-_from_WAGO_10AWG', 5.0, BLK, wg(0), tb(1), [WG, TB], 'WAGO port 1 to ODrive DC- (TB005 pole 2; ferrule).')
# round 13: P- after the short WAGO -> terminal links (it is long and can go round; DC- has one narrow corridor)
wire('WIRE_BMS_P-_to_WAGO_10AWG', 5.0, BLK, pad(-117.9), wg(1), [BMS, WG], 'BMS P- pad to the WAGO (port 2).')
# motor phases (motor leads, 12 AWG silicone assumed: OD 3.6; they leave the lead-exit endcap through the 12 mm grommet)
for k, (ph, dy, dz) in reversed(list(enumerate((('A', 0.0, 2.45), ('B', -2.1, -1.2), ('C', 2.1, -1.2))))):   # routed top pole first, so no phase boxes in the one above
    wire(f'WIRE_motor_phase_{ph}_12AWG', 3.6, PH[ph], [(3.05, -34.0 + dy, 54.5 + dz), (14.0, -34.0 + dy, 54.5 + dz)], tb(2 + k),
         ['V3_REF_motor_stationary_endcap_LEAD_EXIT_PROVISIONAL', TB],
         f'Motor phase {ph}: out of the lead-exit endcap, through the 12 mm grommet in the face plate, to TB005 pole {3 + k} (ferrule). '
         'Gauge and exit point to confirm on the motor.', group='phases')
# charging (16 AWG, OD 2.4): XT60E-F solder cups -> 7.5 A inline fuse -> line stud; minus to the WAGO
FC = 'HARNESS_inline_MINI_fuse_holder_7.5A_charge'
wire('WIRE_charge_plus_XT60_to_inline_fuse_16AWG', 2.4, RED, out((268.0, 0.2, 76.35), (0, -1, 0), 1.2), out((240.05, -9.5, 84.5), (1, 0, 0), 3.0),
     ['AMASS_XT60E-F_charge_port', FC], 'Charge port + (upper cup, per the panel marking) to the 7.5 A inline fuse.')
wire('WIRE_charge_plus_inline_fuse_to_line_16AWG', 2.4, RED, out((199.95, -9.5, 84.5), (-1, 0, 0), 3.0), out((FH['line'], FH['y'][1], FH['z']), (-1, 0, 0), 4.0),
     [FC, HOLD], '7.5 A inline fuse to the main fuse line stud (charging bypasses the 40 A fuse, the BMS still switches it).')
wire('WIRE_charge_minus_XT60_to_WAGO_16AWG', 2.4, BLK, out((268.0, 0.2, 69.25), (0, -1, 0), 1.2), wg(2), ['AMASS_XT60E-F_charge_port', WG],
     'Charge port - (lower cup) to the WAGO (port 3).')
# regulator feed (18 AWG, OD 1.8) and 5 V outputs (20 AWG, OD 1.6)
FR = 'HARNESS_inline_MINI_fuse_holder_3A_regulator'
REGP = ['TRIAL_Pololu5571', 'MOUNT_regulator_perfboard_standoffs']
wire('WIRE_regulator_feed_fuse_load_to_inline_fuse_18AWG', 1.8, RED, out((FH['load'], FH['y'][1], FH['z']), (1, 0, 0), 4.0), out((190.05, -33.0, 85.5), (1, 0, 0), 3.0),
     [HOLD, FR], 'Main fuse load stud to the 3 A inline fuse.')
wire('WIRE_regulator_VIN+_from_inline_fuse_18AWG', 1.8, RED, out((149.95, -33.0, 85.5), (-1, 0, 0), 3.0), reg(31.0), [FR] + REGP,
     '3 A inline fuse to the regulator VIN (screw terminal on its perfboard).')
wire('WIRE_regulator_VIN-_to_WAGO_18AWG', 1.8, BLK, wg(3), reg(27.5), [WG] + REGP, 'WAGO port 4 to the regulator GND in.')
PI = 'TRIAL_Pi4_upright'; DP = 'HARNESS_Dupont_1x3_Pi_power'
wire('WIRE_5V_Pi_plus_20AWG', 1.6, RED, reg(24.0), out((60.6, -107.3, 67.15), (0, 0, -1), 2.0), REGP + [DP], 'Regulator 5 V out to Pi GPIO pin 2.', group='pi5v')
wire('WIRE_5V_Pi_minus_20AWG', 1.6, BLK, reg(20.5), out((60.6, -102.3, 67.15), (0, 0, -1), 2.0), REGP + [DP], 'Regulator GND to Pi GPIO pin 6.', group='pi5v')
FAN = 'TRIAL_driver_fan'
wire('WIRE_5V_fan_plus_24AWG', 1.3, RED, reg(17.0), out((200.9, -16.5, 74.5), (-1, 0, 0), 3.0), REGP + [FAN], 'Regulator 5 V out to the ODrive fan (fan lead extended).', group='fan5v')
wire('WIRE_5V_fan_minus_24AWG', 1.3, BLK, reg(13.5), out((200.9, -13.8, 74.5), (-1, 0, 0), 3.0), REGP + [FAN], 'Regulator GND to the ODrive fan.', group='fan5v')
TE = ['TRIAL_Teensy', 'MOUNT_Teensy_perfboard_standoffs']
wire('WIRE_5V_Teensy_VIN_22AWG', 1.4, RED, reg(10.0), out((-58.5, -109.4, 73.3), (0, 1, 0), 2.5), REGP + TE, 'Regulator 5 V out to Teensy VIN (cut the VIN-VUSB pad).', group='teensy5v')
wire('WIRE_5V_Teensy_GND_22AWG', 1.4, BLK, reg(6.8), out((-73.7, -109.4, 73.3), (0, 1, 0), 2.5), REGP + TE, 'Regulator GND to Teensy GND.', group='teensy5v')
# signals
CANB = ['TRIAL_CAN_headers', 'MOUNT_CAN_board_perfboard_standoffs']
wire('WIRE_Teensy_to_CAN_board_4x26AWG', 2.4, (.85, .6, .2), out((-58.5, -109.4, 64.0), (0, 1, 0), 2.5), out((-46.0, -106.6, 48.9), (0, 0, 1), 3.0), TE + CANB,
     'Teensy CAN TX/RX, 3.3 V and GND to the CAN transceiver board (short bundle on the front plate).')
wire('WIRE_CAN_bus_to_ODrive_twisted_pair', 3.0, (.9, .9, .82), out((-46.0, -113.8, 72.5), (0, 0, 1), 4.0), out((236.6, -88.6, 57.1), (1, 0, 0), 3.0),
     CANB + ['HARNESS_JST_GH_CAN_plug'], 'CAN H / CAN L / GND (twisted pair + drain) from the CAN board terminal to the ODrive CAN header, in front of the BMS.')
wire('WIRE_USB_Teensy_to_Pi', 3.8, (.3, .3, .32), out((-60.8, -113.1, 82.5), (1, 0, 0), 3.0), out((44.4, -29.5, 86.5), (-1, 0, 0), 3.0),
     ['HARNESS_micro_USB_right_angle_plug', 'HARNESS_USB_A_right_angle_plug'], 'USB cable, Teensy (micro-USB, right angle) to the Pi upper USB-A port (right angle).')
# pack balance leads (JST-XH 6-way, flat; modelled round OD 3.0), NTC and switch (OD 1.8 pairs)
wire('WIRE_balance_lead_pack_A', 3.0, WHT, pack(BX['bal'], 'A'), hdr(267.3, -81.9), [PA, BMS], 'Pack A balance lead (cells 1-5) to the BMS balance header.')
wire('WIRE_balance_lead_pack_B', 3.0, WHT, pack(BX['bal'], 'B'), hdr(270.7, -81.9), [PB, BMS], 'Pack B balance lead (cells 6-10) to the BMS balance header.')
wire('WIRE_BMS_NTC_lead', 1.8, (.25, .25, .8), out((263.1, -2.0, 42.0), (1, 0, 0), 2.5), hdr(268.5, -60.4), ['HARNESS_NTC_probe_on_pack_B', BMS],
     'BMS NTC lead to the probe on pack B.')
wire('WIRE_power_switch_to_BMS_pair', 2.2, (.5, .5, .55), out((268.0, 0.3, 47.0), (0, -1, 0), 1.5), hdr(268.5, -49.5),
     ['HARNESS_12mm_latching_power_switch', BMS], 'Power switch to the BMS soft-switch input (twisted pair).')

# round 13: the long regulator / fan / USB runs go through the ceiling loops (fixed straight passes), the phase trio stays in the floor channel
PHASE_FLOOR = {'A': (120.0, -32.6, 6.0), 'B': (120.0, -28.0, 6.0), 'C': (120.0, -30.3, 10.3)}
PHASE_SLAB_X = 207.0                                                   # each phase enters the terminal slot at its own height, straight along X
for w in W:
    w['fixed'] = []
    lv = WC.vias(w['id'], w['a'][0])
    if lv:
        w['via'] = [tuple(map(float, p)) for p in lv]
        w['fixed'] = [1 + 2 * k for k in range(len(lv) // 2)]          # stop i -> i+1 with stops = [a end, *via, b end]
    if w['id'].startswith('WIRE_motor_phase_'):
        zb = w['b'][-1][2]
        w['via'] = [PHASE_FLOOR[w['id'].split('_')[3]], (PHASE_SLAB_X, w['b'][-1][1], zb)]
        w['fixed'] = [2]                                                   # slot run: slab start -> terminal lead-out end
# display ribbon (15-way FFC, 16 mm wide): from the screen's connector, back behind the screen stand and up to the Pi DSI port
# round 12: the Pi's display port now sits over the screen's top edge: up behind the screen, under the Pi's front, over the screen top
RIBBON = [(10.45, -129.0, 12.0), (10.45, -129.0, 17.0), (10.45, -116.8, 17.0), (34.8, -116.8, 55.0), (34.8, -116.8, 79.9),
          (34.8, -128.0, 79.9), (34.8, -128.0, 84.0), (34.8, -130.9, 84.0), (34.8, -130.9, 89.6), (34.8, -130.45, 89.6)]
RIBBON_N = [(0, 1, 0), (0, 0, 1), (0, 1, 0), (0, 1, 0), (0, 0, 1), (0, 1, 0), (0, 0, 1), (0, 1, 0), (0, 0, 1)]     # the ribbon's face normal per segment (it folds at the corners)
def ribbon(pts, normals, w=16.0, t=0.5):
    """Flat cable: a thin box along each segment, lying in the plane with the given normal."""
    s = None
    for (a, b), n in zip(zip(pts, pts[1:]), normals):
        a, b = np.asarray(a), np.asarray(b); d = b - a; L = np.linalg.norm(d); u = d / L
        side = np.cross(np.asarray(n, float), u); side /= np.linalg.norm(side)
        pl = cq.Plane(origin=V(*a), xDir=V(*side), normal=V(*u))
        seg = cq.Workplane(pl).rect(w, t).extrude(L).val()
        s = seg if s is None else s.fuse(seg)
    return s.clean()

def simplify(pts, tol=0.6):
    """Drop points closer than tol to the previous kept one and points on a straight line (keeps both ends)."""
    p = [np.asarray(q, float) for q in pts]; out = [p[0]]
    for q in p[1:-1]:
        if np.linalg.norm(q - out[-1]) > tol: out.append(q)
    if np.linalg.norm(p[-1] - out[-1]) < tol and len(out) > 1: out.pop()
    out.append(p[-1]); k = [out[0]]
    for i in range(1, len(out) - 1):
        u, v = out[i] - k[-1], out[i + 1] - out[i]
        if np.linalg.norm(np.cross(u / np.linalg.norm(u), v / np.linalg.norm(v))) > 0.02: k.append(out[i])
    k.append(out[-1])
    return [tuple(map(float, q)) for q in k]

def tube(pts, r):
    pts = simplify(pts)
    pieces = [cyl(r, a, b) for a, b in zip(pts, pts[1:]) if np.linalg.norm(np.subtract(b, a)) > 1e-3]
    pieces += [cq.Solid.makeSphere(r, V(*p), angleDegrees1=-90) for p in pts[1:-1]]
    if len(pieces) == 1: return pieces[0]
    for f in (lambda: pieces[0].fuse(*pieces[1:]).clean(), lambda: pieces[0].fuse(*pieces[1:])):
        try:
            t = f()
            if t.isValid() and len(t.Solids()) == 1: return t
        except Exception: pass
    return cq.Compound.makeCompound(pieces)                        # every piece is a valid primitive

# ---------------------------------------------------------------- route
rev = {m: json.loads((HERE / m / 'revision.json').read_text()) for m in ('printed', 'cnc')}
OURS = ('WIRE_', 'HARNESS_')
for mode, r in rev.items():                                     # re-runs: drop the previous run's wires and harness parts first
    for n in [n for n in r['parts'] if n.startswith(OURS)]:
        r['parts'].remove(n); r['meta'].pop(n, None); r['colors'].pop(n, None)
        for ext in ('.brep', '.step'): (HERE / mode / (n + ext)).unlink(missing_ok=True)
    for v in r['views'].values(): v[:] = [n for n in v if not n.startswith(OURS)]
R = rev['printed']
allow = {a['name']: HERE / 'allowances' / (a['name'] + '.brep') for a in R['allowances']}
static, moving, lane = WR.load_occupancy(R, allow)
print('occupancy', round(time.time() - T0), 's')
extra = {n: s for n, (s, _, _) in HARNESS.items()}
extra['WIRE_DSI_ribbon_15way_FFC'] = ribbon(RIBBON, RIBBON_N)
for s in extra.values(): WR._voxelize(s, static)

key = VC.sha(VC.file_sha(__file__), VC.file_sha(HERE / 'wire_router.py'), np.packbits(static).tobytes(), np.packbits(moving).tobytes(), np.packbits(lane).tobytes())
cf = VC.CACHE / 'wire_routes.json'
cached = json.loads(cf.read_text()) if (VC.ENABLED and cf.exists()) else {}
if cached.get('key') == key:
    routes = cached['routes']; print('routes: cached')
else:
    router = WR.Router(static, moving, lane); routes = {}
    for w in W:                                                 # reserve every lead-out first, so no wire blocks another's terminal
        for lead in (w['a'], w['b']): router.add([np.array(p) for p in lead], w['od'] / 2, w['group'] or w['id'], w['id'])
        st = [w['a'][-1], *w['via'], w['b'][-1]]
        for i in w['fixed']: router.add([np.array(st[i]), np.array(st[i + 1])], w['od'] / 2, w['group'] or w['id'], w['id'])   # through the loops
    for w in W:
        r = w['od'] / 2
        stops = [w['a'][-1], *w['via'], w['b'][-1]]
        mid = []
        try:
            for i, (p, q) in enumerate(zip(stops, stops[1:])):
                if i in w['fixed']: seg = [np.array(p), np.array(q)]
                else:
                    for gap in (None, 0.5, 0.3, 0.1):                              # a tight spot: accept a smaller wire-to-wire gap (the exact check still rules)
                        try: seg = router.route(np.array(p), np.array(q), r, w['group'] or w['id'], w['id'], gap); break
                        except RuntimeError:
                            if gap == 0.1: raise
                mid += [tuple(map(float, x)) for x in (seg if not mid else seg[1:])]
        except RuntimeError as e:
            print('  FAILED', w['id'], e); routes[w['id']] = None; continue
        pts = w['a'][:-1] + mid + w['b'][::-1][1:]
        routes[w['id']] = pts
        router.add([np.array(p) for p in pts], r, w['group'] or w['id'], w['id'], replace=True)
        print(f"  {w['id']}: {len(pts)} points, {sum(np.linalg.norm(np.subtract(b, a)) for a, b in zip(pts, pts[1:])):.0f} mm", flush=True)
    if VC.ENABLED: VC.CACHE.mkdir(exist_ok=True); cf.write_text(json.dumps(dict(key=key, routes=routes)))
print('routing', round(time.time() - T0), 's')

# ---------------------------------------------------------------- solids + exact check
solids = dict(extra)
meta = {}
for n, (s, col, note) in HARNESS.items(): meta[n] = dict(color=list(col), note=note, kind='part')
meta['WIRE_DSI_ribbon_15way_FFC'] = dict(color=[.86, .74, .5], kind='wire', length=round(sum(np.linalg.norm(np.subtract(b, a)) for a, b in zip(RIBBON, RIBBON[1:]))),
                                         note='Display ribbon: 15-way 1 mm FFC from the screen connector, behind the screen stand, up the back of the screen to the Pi DSI port.')
failed = []
for w in W:
    pts = routes.get(w['id'])
    if not pts: failed.append(w['id']); continue
    pts = simplify(pts)
    s = tube(pts, w['od'] / 2)
    if w['id'].startswith(('WIRE_ODrive_DC', 'WIRE_motor_phase')):                  # ferrule into the TB005 entry
        e = np.asarray(pts[-1]); s = cq.Compound.makeCompound([s, cyl(1.3, e, e + [0, -6.0, 0])])
    solids[w['id']] = s
    L = sum(np.linalg.norm(np.subtract(b, a)) for a, b in zip(pts, pts[1:]))
    meta[w['id']] = dict(color=list(w['color']), kind='wire', od=w['od'], length=round(L), note=f"{w['note']} Insulation OD {w['od']} mm, about {L:.0f} mm long.",
                         points=[[round(v, 2) for v in p] for p in pts])
CONTACT = {w['id']: set(w['contacts']) for w in W}
GROUP = {w['id']: w['group'] for w in W}
CONTACT['WIRE_DSI_ribbon_15way_FFC'] = {'TRIAL_Pi4_upright', 'TRIAL_Waveshare_DSI_E_portrait'}
for n in HARNESS: CONTACT.setdefault(n, set())
for w in W:
    for c in w['contacts']:
        if c in HARNESS: CONTACT[c].add(w['id'])

clash = []
shapes = {n: cq.Shape.importBrep(str(HERE / 'printed' / (n + '.brep'))) for n in R['parts']}
bbs = {n: s.BoundingBox() for n, s in shapes.items()}
def near(a, b, g=0.0): return not (a.xmin > b.xmax + g or a.xmax < b.xmin - g or a.ymin > b.ymax + g or a.ymax < b.ymin - g or a.zmin > b.zmax + g or a.zmax < b.zmin - g)
for n, s in solids.items():
    b = s.BoundingBox()
    for m, t in shapes.items():
        if m in CONTACT.get(n, ()) or not near(b, bbs[m]): continue
        v = VC.clash_volume(s, t)
        if abs(v) > 0.001: clash.append((n, m, round(v, 3)))
names = list(solids)
for i, n in enumerate(names):
    for m in names[i + 1:]:
        if m in CONTACT.get(n, ()) or n in CONTACT.get(m, ()) or not near(solids[n].BoundingBox(), solids[m].BoundingBox()): continue
        v = VC.clash_volume(solids[n], solids[m])
        same = GROUP.get(n) is not None and GROUP.get(n) == GROUP.get(m)       # a bundle (phase trio, 5 V pair): insulation may touch
        if abs(v) > (2.0 if same else 0.5 if (n.startswith('WIRE_') and m.startswith('WIRE_')) else 0.001): clash.append((n, m, round(v, 3)))   # insulation touching is normal in a harness (a pair twists together)
cnc_clash = []
cshapes = {n: HERE / 'cnc' / (n + '.brep') for n in rev['cnc']['parts'] if n not in shapes or n.startswith(('S01', 'V44_'))}
for m, f in cshapes.items():
    t = cq.Shape.importBrep(str(f)); tb_ = t.BoundingBox()
    for n, s in solids.items():
        if m in CONTACT.get(n, ()) or not near(s.BoundingBox(), tb_): continue
        v = VC.clash_volume(s, t)
        if abs(v) > 0.001: cnc_clash.append((n, m, round(v, 3)))

# ---------------------------------------------------------------- write into both variants
for mode, r in rev.items():
    d = HERE / mode
    for n, s in solids.items():
        s.exportBrep(str(d / (n + '.brep'))); s.exportStep(str(d / (n + '.step')))
        if n not in r['parts']: r['parts'].append(n)
        m = meta[n]
        r['meta'][n] = dict(group='wiring', kind=m['kind'], note=m['note'], manufacture='Buy' if n.startswith('HARNESS_') else 'Make (harness)',
                            demo_name='', source='build_v44_wires.py', **({'points': m['points']} if 'points' in m else {}))
        r['colors'][n] = m['color']
        for v in ('complete', 'open', 'wiring', 'io_access'):
            if n not in r['views'][v]: r['views'][v].append(n)
    for n in ('Littelfuse_04980921GXM5_holder', 'PART_WAGO_221-615_negative_junction', 'AMASS_XT60E-F_charge_port'):
        if n in r['parts'] and n not in r['views']['wiring']: r['views']['wiring'].append(n)
    (d / 'revision.json').write_text(json.dumps(r, indent=1))

rep = dict(wires=len([n for n in solids if n.startswith('WIRE_')]), harness_parts=len(HARNESS), failed=failed, clashes=clash, cnc_clashes=cnc_clash,
           lengths={n: meta[n].get('length') for n in solids if n.startswith('WIRE_')}, seconds=round(time.time() - T0))
(HERE / 'wires-report.json').write_text(json.dumps(rep, indent=1))
print('wires', rep['wires'], '| failed', failed, '| clashes', len(clash), '| cnc clashes', len(cnc_clash), '|', rep['seconds'], 's')
for c in clash + cnc_clash: print('  ', c)
