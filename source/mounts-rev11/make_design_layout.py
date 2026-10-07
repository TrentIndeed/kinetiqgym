"""Design layout rev 11 = the recovered 6.22 L layout + layout decisions of September 27, 2026.

- Screen centred in the front-left panel (enclosure left edge X -81 to the fairlead front hardware X 101.8) and on
  the front face height (exterior Z -15.2 to 96.5).
- Fuse +1 mm toward the back wall (clears the ODrive heat spreader and the drum clearance).
- ODrive terminal wiring space +1 mm in X (clears the right pillow-block flange).
- Battery plug space +4 mm in X, -1.5 mm in Z (clears the ODrive bracket and the BMS tray).
- BMS group +0.5 mm up (BMS tray under it); BMS wiring allowance cut to the BMS's own 13 mm height
  (the model part is resized by publish_mounts_rev11.py, bottom kept; here it drops 0.6 mm to Z 79-92).
The recovered file itself is not modified.
Rev 12 (September 27, user-approved option A of volume-options-2026-09-27): the user's drum shaft is cut to 176 mm, so the
ODrive, fan, battery and BMS move 24 mm toward the motor. Written to design-layout-rev12.json; design-layout-rev11.json is
frozen (it carries the rev 11b mount poses). Pieces with no pose in the layout take their rev 11b page pose from
print-v44/demo-placements-rev11.json (frozen) before they move.
"""
import json, copy, numpy as np
from pathlib import Path
from scipy.spatial.transform import Rotation as Rot
HERE = Path(__file__).resolve().parent
PUB = HERE.parent / 'workbench/public/stock-battery-fit'
L = json.load(open(PUB / 'user-layout-6.22L.json'))
WB = {r['n']: r for r in json.load(open(HERE / 'world-boxes-6.22L.json', encoding='utf-8-sig'))['rows']}
P = copy.deepcopy(L); PT = {t['id']: t for t in P['transforms']}
PARENT = {'CONCEPT_Pi_carrier': 'assembly:pi'}
def arot(a): return Rot.from_quat(PT[a]['rotation']) if a in PT else Rot.identity()
def shift_asm(a, d): t = PT['assembly:' + a]; t['position'] = (np.array(t['position']) + d).tolist()
def shift_piece(n, dw):
    a = PARENT.get(n, WB[n]['asm']); t = PT['piece:' + n]
    t['position'] = (np.array(t['position']) + (arot(a).inv().apply(dw) if a else np.array(dw))).tolist()

LEFT, FAIRLEAD_FRONT = -77.0 - 4, 101.8                  # enclosure left exterior; fairlead front hardware (rear mount plate)
Z_BOT, Z_TOP = -11.2 - 4, 92.5 + 4                       # bolts kept; top = Pi after the BMS-wiring change
glass = WB['TRIAL_Waveshare_DSI_E_portrait']
cx, cz = (LEFT + FAIRLEAD_FRONT) / 2, (Z_BOT + Z_TOP) / 2
SCREEN_D = np.array([cx - (glass['min'][0] + glass['max'][0]) / 2, 0, cz - (glass['min'][2] + glass['max'][2]) / 2])
shift_asm('screen', SCREEN_D)
shift_piece('TRIAL_protection_and_connections', [0, 1.0, 0])
shift_piece('RESERVE_driver_terminal_access', [1.0, 0, 0])
shift_piece('RESERVE_battery_connections', [4.0, 0, -1.5])
shift_asm('bms', np.array([0, 0, 0.5]))
shift_piece('RESERVE_RS50_BMS_leads', [0, 0, -0.6])     # with the 13 mm resize (bottom kept): world Z 79-92
# --- rev 11b (September 27): battery clear of the real ODrive terminal block; small boards off the motor end ---
def reorient_piece(n, perm_quat, new_center):
    a = PARENT.get(n, WB[n]['asm']); t = PT['piece:' + n]
    Ra = arot(a); Pa = np.array(PT[a]['position'])
    q_new = Rot.from_quat(perm_quat) * (Ra * Rot.from_quat(t['rotation']))
    t['rotation'] = (Ra.inv() * q_new).as_quat().tolist(); t['position'] = Ra.inv().apply(np.array(new_center) - Pa).tolist()
BATTERY_DX = 8.0                                   # TB005-762 terminal block is 21.7 mm tall (Same Sky drawing): battery to X 268.5
shift_asm('battery', np.array([BATTERY_DX, 0, 0]))
# Teensy, CAN board and regulator move to the back wall behind the drum (X 92-170, Y > -20, clear of the drum sweep),
# so the enclosure can curve in around the motor. Reserves follow their boards.
shift_asm('teensy', np.array([123.8, 0, 8.9]))                          # board X 92..131.6, Z 50..71.8
shift_piece('RESERVE_control_headers', [-8.0, 0, 10.1])                 # X 134..169.6, Z 50..60
shift_piece('RESERVE_Teensy_USB', [-14.8, 0, 15.1])                     # X 134..154, Z 61..71
shift_asm('TRIAL_CAN_headers', np.array([161.2, 0, 20.2]))              # board X 92..128.4, Z 22..40.4
s2 = np.sin(np.pi / 4)
reorient_piece('RESERVE_CAN_terminal_leads', [0, 0, s2, s2], [108.2, -12.5, 10.1])     # 32.4 x 15 x 10.2 under the CAN board
shift_asm('regulator', np.array([153.7, 0, 16.7]))                      # board X 134..163.4, Z 17..46.4
reorient_piece('RESERVE_regulator_leads', [0, s2, 0, s2], [146.7, -10.6, 8.5])         # 25.4 x 10.8 x 15 under the regulator
P['designLayout'] = 'rev11b-2026-09-27'

# --- rev 12 (September 27): 176 mm drum shaft ---
ROWS = {r['n']: r for r in json.loads((HERE.parent / 'print-v44/demo-placements-rev11.json').read_text(encoding='utf-8-sig'))['rows']}
def asm_T(a): return (np.zeros(3), Rot.identity()) if a is None else (np.array(PT[a]['position']), Rot.from_quat(PT[a]['rotation']))
def ensure(n):
    """Piece pose in the layout; a piece without one gets its rev 11b page pose (call before its assembly moves)."""
    pid = 'piece:' + n
    if pid not in PT:
        Ap, Ar = asm_T(ROWS[n]['asm']); m = np.array(ROWS[n]['m']).reshape(4, 4).T
        PT[pid] = dict(id=pid, position=Ar.inv().apply(m[:3, 3] - Ap).tolist(), rotation=(Ar.inv() * Rot.from_matrix(m[:3, :3])).as_quat().tolist())
        P['transforms'].append(PT[pid])
    return PT[pid]
def move_piece(n, dw):
    t = ensure(n); _, Ar = asm_T(ROWS[n]['asm']); t['position'] = (np.array(t['position']) + Ar.inv().apply(dw)).tolist()
def place_piece(n, rot_delta, box_centre):
    """Rotate the piece in world by rot_delta about its rev 11b box centre and put that centre at box_centre."""
    t = ensure(n); Ap, Ar = asm_T(ROWS[n]['asm']); m = np.array(ROWS[n]['m']).reshape(4, 4).T
    Wp, Rw = m[:3, 3], Rot.from_matrix(m[:3, :3]); Wc = (np.array(ROWS[n]['min']) + np.array(ROWS[n]['max'])) / 2
    Rd = Rot.from_quat(rot_delta); Wp2 = np.array(box_centre) - Rd.apply(Wc - Wp)
    t['position'] = Ar.inv().apply(Wp2 - Ap).tolist(); t['rotation'] = (Ar.inv() * Rd * Rw).as_quat().tolist()
MOVED12 = ('RESERVE_driver_terminal_access', 'RESERVE_battery_connections', 'TRIAL_protection_and_connections', 'RESERVE_control_headers',
           'RESERVE_Teensy_USB', 'V3_REF_encoder_magnet_6x5_N45SH_DIAMETRIC')
for n in MOVED12: ensure(n)                                            # pin rev 11b poses before any assembly moves
DX12 = np.array([-24.0, 0, 0])
for g in ('odrive', 'fan', 'battery', 'bms'): shift_asm(g, DX12)       # ODrive encoder face 1 mm from the magnet on the cut shaft end
move_piece('V3_REF_encoder_magnet_6x5_N45SH_DIAMETRIC', DX12)           # magnet re-glued on the cut end (shaft X 37..213)
# The 176 mm shaft part (REF_drum_shaft_12mm_176mm) keeps the old shaft's pivot (pose_bounds) and pose; the 200 mm part is retired.
PT['piece:REF_drum_shaft_12mm_176mm'] = dict(PT['piece:REF_drum_shaft_APPROX_12mm'], id='piece:REF_drum_shaft_12mm_176mm')
P['transforms'].append(PT['piece:REF_drum_shaft_12mm_176mm'])
# Shaft 2 (60T hub inboard, outer pedestal 10 mm in, REX 5 mm in) is rebuilt in the module itself: build_fairlead_module10.py rev 12.
s2 = np.sin(np.pi / 4); CYC, Y90 = [.5, .5, .5, .5], [0, s2, 0, s2]
place_piece('RESERVE_driver_terminal_access', CYC, [231.8, -112.4, 25.6])      # 19.5 x 30 x 48 in front of the TB005 wire entries (X 222..243.7)
place_piece('RESERVE_battery_connections', Y90, [205.0, -115.0, 66.0])         # XT90 plug space: 60 x 30 x 20 along X above the gears, under the tray
move_piece('TRIAL_protection_and_connections', [-17.0, 0, 0])                  # fuse X 153..243 (saddles move with it in build_mounts.py)
shift_asm('regulator', np.array([0, 0, 13.0]))                                 # regulator Z 30..59.4
move_piece('RESERVE_regulator_leads', [30.0, 0, 16.0])                         # X 164..189.4, Z 30..45 (net after the board +13)
move_piece('RESERVE_control_headers', [0, 0, 11.0])
move_piece('RESERVE_Teensy_USB', [-62.5, 0, -6.0])                             # to the Teensy's motor-side end: X 71.5..91.5, Z 55..65 (clear of the BMS wiring)
# --- V44 fix list round 2 (L7, September 28): Pi and BMS upside down under the cover ceilings ---
def rotate_asm(a, rot, about, d):
    t = PT['assembly:' + a]; Rd = Rot.from_quat(rot); p = np.array(t['position'])
    t['position'] = (Rd.apply(p - np.array(about)) + np.array(about) + np.array(d)).tolist(); t['rotation'] = (Rd * Rot.from_quat(t['rotation'])).as_quat().tolist()
Y180 = [0, 1, 0, 0]
pi = ROWS['TRIAL_Pi4_upright']; PI_C = (np.array(pi['min']) + np.array(pi['max'])) / 2            # the Pi did not move in rev 12
rotate_asm('pi', Y180, PI_C, [0, 0, -2.0])                  # components hang down, board 3 mm under the ceiling (Z 66.5..90.5)
place_piece('RESERVE_RS50_BMS', Y180, [243.0, -75.95, 85.0])  # JBD BMS upside down, Z 78.5..91.5: 1 mm over the saddle bars, 0.5 over the heat spreader
# --- V44 fix list round 4 (R4-5): Teensy, CAN board and regulator move onto the rear plate behind the motor / coupler ---
BOARD_MOVES = {'teensy': (-144.0, 0.0, -2.0), 'TRIAL_CAN_headers': (-166.0, 0.0, 5.0), 'regulator': (-138.0, 0.0, -2.0)}
for a_, d_ in BOARD_MOVES.items(): shift_asm(a_, np.array(d_))
# --- round 5: the CAN board stands on its standoffs (it was still lying flat): perfboard vertical against the rear plate, low behind the
# motor where the round body leaves the most room (board X -74..-37.6, Y -21.9..-3.5, Z 4..18.2); its lead space goes above it ---
place_piece('TRIAL_CAN_headers', [s2, 0, 0, s2], [-55.8, -12.7, 11.1])      # 6 mm standoffs: board front Y -21.9, clear of the motor box
place_piece('RESERVE_CAN_terminal_leads', [0, 0, 0, 1], [-57.8, -12.5, 24.1])
# --- round 6: Pi and ODrive turned so their ports face the front; the small boards stand on a printed plate left of the screen ---
import front_boards as FB
shift_asm('pi', np.array([-13.0, -15.0, 0]))   # round 12: 15 mm toward the screen too (USB plugs inside the back wall, no bump)                       # round 8: Pi turned back (display connector toward the screen, USB to the back), 13 mm toward the screen centre over the lowered face-plate top (the motor end cap stops it there)
rotate_asm('odrive', [1, 0, 0, 0], [0, -62.5, 43.0], [0, 0, 0])                 # 180 deg about the shaft axis: headers to the front,
                                                                               # terminal block to the back; encoder stays on the magnet
for a_ in FB.ROT:
    rotate_asm(a_, FB.ROT[a_].as_quat().tolist(), FB.NOW[a_], FB.target(a_) - FB.NOW[a_])
shift_asm('fan', np.array([10.0, 0, 0]))                        # round 8: fan 10 mm toward the battery (fan X 201..241)
P['designLayout'] = 'rev12-2026-09-27'
json.dump(P, open(PUB / 'design-layout-rev12.json', 'w'), separators=(',', ':'))
print('screen move', SCREEN_D.round(2).tolist(), 'centre', round(cx, 2), round(cz, 2))
