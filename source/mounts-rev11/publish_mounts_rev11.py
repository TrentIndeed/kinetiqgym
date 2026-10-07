"""Put the rev 11 mounts into the packing demo (TP2700 model only; the TP3850 comparison is not updated).

Each mount was authored in world coordinates of design-layout-rev11.json. The page places a new part at its
default pose: world = A_pos + R_a (v_model - A_base), where A_base is the centre of the host group's original
(non-addedIn) parts. So v_model = A_base + R_a^-1 (v_world - A_pos). The BMS wiring allowance is resized from
15.8 to 13 mm, keeping its bottom face (the design layout lowers it 0.6 mm to sit level with the raised BMS). New parts carry addedIn='mounts-11'.
Also writes each mount's pose into design-layout-rev11.json and flags the screen parts for the base notch.
Run after build_mounts.py and make_design_layout.py.
Rev 12: writes the mount poses into design-layout-rev12.json (rev 11 is frozen) and swaps the 200 mm drum shaft for the
user's shaft cut to 176 mm (REF_drum_shaft_12mm_176mm, addedIn='rev-12', CAD in rev12-176-shaft/; the old part is retired).
"""
from pathlib import Path
import gzip, json
import numpy as np
from scipy.spatial.transform import Rotation as Rot

HERE = Path(__file__).resolve().parent
PUB = HERE.parent / 'workbench/public/stock-battery-fit'
TAG = 'mounts-11'
M = json.load(open(HERE / 'mounts.json'))['parts']
LAYOUT_FILE = PUB / 'design-layout-rev12.json'
LAYOUT = json.load(open(LAYOUT_FILE))
LAYOUT['transforms'] = [t for t in LAYOUT['transforms'] if not t['id'].startswith(('piece:MOUNT ', 'piece:ROUTE '))]
LAY = {t['id']: t for t in LAYOUT['transforms']}
NOTCH = ('TRIAL_Waveshare_DSI_E_portrait', 'TRIAL_portrait_bezel_CONCEPT', 'TRIAL_DSI_service')   # the base is notched under the centred screen
path = PUB / 'editor-model-tp2700.json.gz'
d = json.loads(gzip.decompress(path.read_bytes()))
parts = [p for p in d['parts'] if p.get('addedIn') not in (TAG, 'rev-12')]      # idempotent

def a_base(a):
    bs = [p.get('pose_bounds') or p['bounds'] for p in parts if p['assembly'] == a and not p.get('addedIn')]
    return (np.min([b[:3] for b in bs], 0) + np.max([b[3:] for b in bs], 0)) / 2

BYNAME = {p['name']: p for p in parts}
def cen(p): b = np.array(p.get('pose_bounds') or p['bounds'], float); return (b[:3] + b[3:]) / 2
new = []
for r in M:
    # Mated to its host piece: the mount keeps the host's baseline relative pose, so the page treats the pair as a
    # designed fit even where the host piece was placed individually. world w -> model v:
    #   v = c_h + Q_h^-1 (R_a^-1 (w - A_pos) - L_h);  mount layout pose = (L_h + Q_h (c_m - c_h), Q_h)
    a = r['host']; t = LAY['assembly:' + a]
    Ra, Ap, Ab = Rot.from_quat(t['rotation']), np.array(t['position']), a_base(a)
    h = BYNAME[r['host_piece']]; ch = cen(h); th = LAY.get('piece:' + r['host_piece'])
    Lh, Qh = (np.array(th['position']), Rot.from_quat(th['rotation'])) if th else (ch - Ab, Rot.identity())
    to_model = lambda w: ch + Qh.inv().apply(Ra.inv().apply(np.asarray(w, float) - Ap) - Lh)
    v = to_model(np.array(r['vertices']).reshape(-1, 3))
    boxes = []
    for x0, x1, y0, y1, z0, z1 in r['collision_boxes']:
        c = to_model(np.array([[x, y, z] for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]))
        boxes.append([*c.min(0).round(4), *c.max(0).round(4)])
    part = dict(name=r['name'], assembly=a, group=r['group'], color=r['color'], kind='proposal', addedIn=TAG,
                vertices=np.round(v, 4).ravel().tolist(), triangles=r['triangles'], bounds=[*v.min(0).round(4), *v.max(0).round(4)],
                collision_shape=dict(boxes=boxes, source='rev 11 mount solid boxes'), contacts=r['contacts'], mated_to=r['host_piece'],
                description=r['role'] + f" Material: {r['material']}.", model_status='Rev 11 mount — first-pass CAD, not load-qualified', **r.get('extra', {}))
    new.append(part)
    cm = cen(part)
    LAYOUT['transforms'].append(dict(id='piece:' + r['name'], position=(Lh + Qh.apply(cm - ch)).tolist(), rotation=Qh.as_quat().tolist()))
for n in NOTCH:
    BYNAME[n]['base_notch'] = True

# BMS wiring allowance: 15.8 -> 13 mm along the model axis that the layout maps to world Z
w = next(p for p in parts if p['name'] == 'RESERVE_RS50_BMS_leads')
if not w.get('resized_by') == TAG:
    R = Rot.from_quat(LAY['assembly:bms']['rotation']) * Rot.from_quat(LAY['piece:RESERVE_RS50_BMS_leads']['rotation'])
    up = R.inv().apply([0, 0, 1]); ax = int(np.argmax(np.abs(up)))
    bb0 = np.array(w['bounds'], float); h = bb0[3 + ax] - bb0[ax]; s = 13.0 / h
    fix = bb0[ax] if up[ax] > 0 else bb0[3 + ax]                # keep the world-bottom face; pose_bounds (the pivot) untouched
    def squash(vals):
        a = np.array(vals, float).reshape(-1, 3); a[:, ax] = fix + (a[:, ax] - fix) * s; return np.round(a, 4).ravel().tolist()
    for vis in (w.get('visual_parts') or [w]): vis['vertices'] = squash(vis['vertices'])
    for key in ('bounds', 'display_bounds'):
        if key in w:
            bb = np.array(w[key], float); lo, hi = fix + (bb[ax] - fix) * s, fix + (bb[3 + ax] - fix) * s
            bb[ax], bb[3 + ax] = min(lo, hi), max(lo, hi); w[key] = bb.round(4).tolist()
    w['label'] = 'BMS balance / power wiring — 125 × 20 × 13 mm allowance'
    w['description'] = (w.get('description') or '') + ' Rev 11: height cut from 15.8 (old DALY body) to the JBD body height, 13 mm.'
    w['resized_by'] = TAG
    print('BMS wiring allowance resized along model axis', 'XYZ'[ax], f'{h:.1f} -> 13.0')

# ODrive terminal envelope -> the real TB005-762-05BE height (Same Sky drawing: 21.7 mm off the PCB), PCB face kept
t = next(p for p in parts if p['name'] == 'V3_REF_ODrive_TB005_762_05BE_terminal_ENVELOPE')
if not t.get('resized_by') == TAG:
    R = Rot.from_quat(LAY['assembly:odrive']['rotation']) * (Rot.from_quat(LAY['piece:' + t['name']]['rotation']) if 'piece:' + t['name'] in LAY else Rot.identity())
    out = R.inv().apply([1, 0, 0]); ax = int(np.argmax(np.abs(out)))
    bb0 = np.array(t['bounds'], float); h = bb0[3 + ax] - bb0[ax]; s = 21.7 / h
    t.setdefault('pose_bounds', bb0.round(4).tolist()) if not t.get('pose_bounds') else None   # keep the page pivot where it was
    if not t.get('pose_bounds'): t['pose_bounds'] = bb0.round(4).tolist()
    fix = bb0[ax] if out[ax] > 0 else bb0[3 + ax]               # the PCB-side face
    def grow(vals):
        a = np.array(vals, float).reshape(-1, 3); a[:, ax] = fix + (a[:, ax] - fix) * s; return np.round(a, 4).ravel().tolist()
    for vis in (t.get('visual_parts') or [t]): vis['vertices'] = grow(vis['vertices'])
    for key in ('bounds', 'display_bounds'):
        if key in t:
            bb = np.array(t[key], float); lo, hi = fix + (bb[ax] - fix) * s, fix + (bb[3 + ax] - fix) * s
            bb[ax], bb[3 + ax] = min(lo, hi), max(lo, hi); t[key] = bb.round(4).tolist()
    t['description'] = (t.get('description') or '') + ' Rev 11b: height set to the Same Sky TB005-762 drawing, 21.7 mm off the PCB (was 11.9).'
    t['resized_by'] = TAG
    print('TB005 envelope grown along model axis', 'XYZ'[ax], f'{h:.1f} -> 21.7')

# Rev 12: drum shaft cut to 176 mm (right end; the encoder magnet is re-glued on the cut end). Same axis and left end as the
# 200 mm part; pose_bounds = the old bounds, so the old part's layout pose places it (make_design_layout.py copies that pose).
import cadquery as cq
old = BYNAME['REF_drum_shaft_APPROX_12mm']; ob = np.array(old['bounds'], float); ax_c = (ob[1:3] + ob[4:6]) / 2
SH = HERE.parent / 'rev12-176-shaft'; SH.mkdir(exist_ok=True)
shaft = cq.Workplane('YZ', origin=(ob[0], ax_c[0], ax_c[1])).circle(6.0).extrude(176.0).faces('<X or >X').chamfer(0.5).val()
shaft.exportStep(str(SH / 'REF_drum_shaft_12mm_176mm.step')); shaft.exportBrep(str(SH / 'REF_drum_shaft_12mm_176mm.brep'))
sv, st = shaft.tessellate(.02, .15); sv = np.array([q.toTuple() for q in sv])
old['retired'] = True; old['retired_by'] = 'rev-12'
new.append(dict(name='REF_drum_shaft_12mm_176mm', assembly=old['assembly'], group=old['group'], color=old['color'], kind='proposal', addedIn='rev-12',
                vertices=np.round(sv, 4).ravel().tolist(), triangles=np.array(st).ravel().tolist(), bounds=[*sv.min(0).round(4), *sv.max(0).round(4)],
                pose_bounds=ob.round(4).tolist(), contacts=['V3_REF_encoder_magnet_6x5_N45SH_DIAMETRIC'],
                description='User 12 mm round shaft cut to 176 mm at the right (magnet) end: X 37-213. Cut square with a hacksaw, face and chamfer 0.5 mm; '
                            'the encoder magnet is re-glued on the cut end (1 mm to the ODrive encoder). No keyseat.',
                model_status='Rev 12 — user shaft cut to 176 mm'))
print('drum shaft: 200 mm part retired, 176 mm part added', [round(v, 2) for v in new[-1]['bounds']])

# V44 fix list round 2: the Pi hangs from the left cover's ceiling (carrier plate gone); the old disconnect/charge allowance is obsolete
# (charge port and power switch are on the rear I/O panel, D7).
for p in parts:
    if p['name'] in ('CONCEPT_Pi_carrier', 'RESERVE_disconnect_charge') and not p.get('retired'):
        p['retired'] = True; p['retired_by'] = 'fix-round2'
# Round 6: the small boards moved to the front board plate and the ODrive terminal faces the back; their old wiring spaces are
# replaced by 'RESERVE front board leads' and 'RESERVE ODrive terminal wiring (back)'.
for p in parts:
    if p['name'] in ('RESERVE_control_headers', 'RESERVE_Teensy_USB', 'RESERVE_CAN_terminal_leads', 'RESERVE_regulator_leads',
                     'RESERVE_driver_terminal_access') and not p.get('retired'):
        p['retired'] = True; p['retired_by'] = 'fix-round6'
    if p['name'] == 'TRIAL_Pi_port_allowance' and not p.get('retired'):   # round 12: the right-angle USB plug is modelled in the V44 harness
        p['retired'] = True; p['retired_by'] = 'fix-round12'
    if p['name'] in ('RESERVE_branch_distribution', 'RESERVE_battery_connections', 'TRIAL_protection_and_connections', 'RESERVE_RS50_BMS_leads') and not p.get('retired'):   # 7b / round 9   # 7b: XT90S plug space dropped
        p['retired'] = True; p['retired_by'] = 'fix-round7'             # replaced by the fuse-holder studs + WAGO 221-615
# Round 8: the Pi's page envelope becomes its real bodies (44 boxes from the V44 CAD), so the page stops flagging free space
# around it (e.g. the motor-plate bolt head beside its corner) as an overlap.
_pi = BYNAME['TRIAL_Pi4_upright']; _pb = np.array(_pi.get('pose_bounds') or _pi['bounds'], float); _pc = (_pb[:3] + _pb[3:]) / 2
_cb = json.loads((HERE / 'pi_collision_boxes.json').read_text())
_pi['collision_shape'] = dict(boxes=[[*(np.array(b[:3]) + _pc).round(4).tolist(), *(np.array(b[3:]) + _pc).round(4).tolist()] for b in _cb['boxes']], source=_cb['source'])
_fp = BYNAME['V43_METAL_motor_face_4mm']; _fb = np.array(_fp.get('pose_bounds') or _fp['bounds'], float); _fc = (_fb[:3] + _fb[3:]) / 2
_cf = json.loads((HERE / 'face_collision_boxes.json').read_text())
# and its page mesh becomes the trimmed plate (from the V44 CAD, world -> model through its current page pose); pose_bounds keeps the old
# bounds so the layout pose still places it.
import cadquery as _cq
_fb_path = HERE.parent / 'print-v44/printed/V43_METAL_motor_face_4mm.brep'
_dump = json.loads((HERE.parent / 'print-v44/demo-placements-rev12.json').read_text(encoding='utf-8-sig'))
_frow = next((r for r in _dump['rows'] if r['n'] == 'V43_METAL_motor_face_4mm'), None)
if _fb_path.exists() and _frow:
    _plate = _cq.Shape.importBrep(str(_fb_path)).cut(_cq.Solid.makeBox(4.2, 87.2, 8.6, _cq.Vector(5.9, -108.1, 80.5))).cut(_cq.Solid.makeBox(4.2, 21.1, 18.6, _cq.Vector(5.9, -57.0, 70.5)))
    _v, _t = _plate.tessellate(.05, .2); _w = np.array([[q.x, q.y, q.z, 1.0] for q in _v])
    _Mi = np.linalg.inv(np.array(_frow['m']).reshape(4, 4).T)
    _fp.setdefault('pose_bounds', _fp['bounds'])
    _mv = (_w @ _Mi.T)[:, :3] + _fc
    _fp['vertices'] = np.round(_mv, 4).ravel().tolist(); _fp['triangles'] = np.array(_t).ravel().tolist()
    _fp['bounds'] = [*_mv.min(0).round(4).tolist(), *_mv.max(0).round(4).tolist()]
    _fp.pop('visual_parts', None)
_fp['collision_shape'] = dict(boxes=[[*(np.array(b[:3]) + _fc).round(4).tolist(), *(np.array(b[3:]) + _fc).round(4).tolist()] for b in _cf['boxes']], source=_cf['source'])
# Round 12: the screen's page envelope becomes its real bodies too (one box per solid of the V44 CAD), so the Pi can sit over its top
# edge (the envelope included the empty space behind the screen up to its top).
def _detail_from_v44(page_name, brep_name, source):
    row = next((r for r in _dump['rows'] if r['n'] == page_name), None); f = HERE.parent / 'print-v44/printed' / (brep_name + '.brep')
    if not (row and f.exists()): return
    part = BYNAME[page_name]; pb = np.array(part.get('pose_bounds') or part['bounds'], float); pc = (pb[:3] + pb[3:]) / 2
    Mi = np.linalg.inv(np.array(row['m']).reshape(4, 4).T); boxes = []
    for q in _cq.Shape.importBrep(str(f)).Solids():
        b = q.BoundingBox()
        c = np.array([[x, y, z, 1.0] for x in (b.xmin, b.xmax) for y in (b.ymin, b.ymax) for z in (b.zmin, b.zmax)])
        m = (c @ Mi.T)[:, :3] + pc
        boxes.append([*m.min(0).round(4).tolist(), *m.max(0).round(4).tolist()])
    part['collision_shape'] = dict(boxes=boxes, source=source)
_detail_from_v44('TRIAL_Waveshare_DSI_E_portrait', 'TRIAL_Waveshare_DSI_E_portrait', 'one box per body of the Waveshare supplier CAD (V44, round 12)')
parts.extend(new); d['parts'] = parts
if isinstance(d.get('notes'), list):
    d['notes'] = [n for n in d['notes'] if TAG not in str(n) and 'rev-12' not in str(n)] + [f'{TAG}: printed/stock mounts for the ODrive, BMS + battery, fan, Pi carrier, screen, boards and fuse, plus the motor phase-lead route. Design layout rev 11 centres the screen in the front-left panel.',
        'rev-12: drum shaft cut to 176 mm; ODrive, fan, battery and BMS 24 mm toward the motor (design layout rev 12, 5.87 L).']
path.write_bytes(gzip.compress(json.dumps(d, separators=(',', ':')).encode(), mtime=0))
json.dump(LAYOUT, open(LAYOUT_FILE, 'w'), separators=(',', ':'))
print('tp2700', {'added': len(new), 'total': len(parts)})
