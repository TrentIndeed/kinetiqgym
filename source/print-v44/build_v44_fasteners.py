"""V44 round 13: every screw, nut, washer and heat-set insert of the V44-made joints, with the holes checked and cut to size.
Run after build_v44_shell.py (reads structure-report.json / shell-report.json for the joint positions), before the harness.

For each joint the parts along the screw axis are found, then every hole is made to the size its role needs:
  clear   - through hole: printed parts M2.5 2.9 / M3 3.6 / M4 4.7 / M6 6.8 (the repo rule: metal clearance + 0.2), metal 2.9 / 3.4 / 4.5 / 6.6
  insert  - heat-set pocket (Ruthex RX, as build_fastened.py): M2.5 3.6, M3 4.0, M4 5.6, depth L + 1 where the part allows, 0.5 mm lead-in
  tap     - metal tap drill M2.5 2.05, M3 2.5, M4 3.3, M6 5.0; the screw engages it (printed standoffs: M2.5 female thread 2.1)
  pilot   - printed self-tapping pilot M2.5 2.2
  csk / cbore at the head. The screw length is the shortest standard length that engages the insert / thread fully without
  bottoming. Before a hole is cut the part is checked: a hole that was missing or undersized is reported as added, one that is
  more than 0.35 mm too big as oversize. Holes of screw size that no screw passes through are listed as unused.
Hardware is nominal (no helical threads). Knurl / thread overlap with the host is intended and listed in expected_interference.
"""
from pathlib import Path
import json, math, shutil
import numpy as np
import cadquery as cq
import v44cache as VC
import back_wall as BW
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder

H = Path(__file__).resolve().parent
REV = {m: json.loads((H / m / 'revision.json').read_text()) for m in ('printed', 'cnc')}
ST = json.loads((H / 'structure-report.json').read_text())['joints']
SH = json.loads((H / 'shell-report.json').read_text())
V = cq.Vector
UP, DOWN, FWD, BACK = (0, 0, 1), (0, 0, -1), (0, -1, 0), (0, 1, 0)
ZT, W = 96.5, 3.0

# ---------------------------------------------------------------- hardware tables
DIM = {2.5: (4.5, 2.5, 2.0, 5.0, 2.0, 6.0, 0.5), 3: (5.5, 3.0, 2.5, 5.5, 2.4, 7.0, 0.5), 4: (7.0, 4.0, 3.0, 7.0, 3.2, 9.0, 0.8),
       6: (10.0, 6.0, 5.0, 10.0, 5.0, 12.0, 1.6)}                          # head d, head h, key, nut AF, nut t, washer OD, washer t
INSERTS = {2.5: dict(od=4.0, hole=3.6, length=4.0), 3: dict(od=4.6, hole=4.0, length=4.0), 4: dict(od=6.3, hole=5.6, length=4.0)}
CLEAR = {'printed': {2.5: 2.9, 3: 3.6, 4: 4.7, 6: 6.8}, 'metal': {2.5: 2.9, 3: 3.4, 4: 4.5, 6: 6.6}}
TAP = {2.5: 2.05, 3: 2.5, 4: 3.3, 6: 5.0}
PILOT = {2.5: 2.2, 3: 2.6}
STD = [3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 30, 35, 40]
BLACK, STEEL, BRASS = (.17, .19, .21), (.67, .70, .73), (.77, .57, .20)

def printed_part(n):
    return not any(k in n for k in ('CNC', 'METAL', 'AL_flat_bar', 'SUPPLIER', 'AMASS', 'Littelfuse', 'goBILDA', 'SKF', 'KHK', 'ThunderPower', 'JBD', 'TRIAL_Pi4')) \
        or n.startswith(('V44_PRINT', 'MOUNT_', 'FM10_Square', 'FM10_Printed', 'S01_V44_PRINT', 'R07_V44_PRINT'))

def cyl(r, p, v, t0, t1):
    p, v = np.asarray(p, float), np.asarray(v, float)
    if t1 - t0 < 0.05: t1 = t0 + 0.05                                                    # thin layers: never a zero-length solid
    return cq.Solid.makeCylinder(r, t1 - t0, V(*(p + v * t0)), V(*v))

def orient(s, p, v):
    z = V(0, 0, 1); d = V(*v); c = z.cross(d)
    if c.Length > 1e-8: s = s.rotate(V(0, 0, 0), c, math.degrees(z.getAngle(d)))
    elif d.z < 0: s = s.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    return s.translate(V(*p))

def hexsolid(af, h, z=0): return cq.Workplane('XY').polygon(6, af / math.cos(math.pi / 6)).extrude(h).val().translate((0, 0, z))
def bolt(d, L, style):
    hd, hh, key, *_ = DIM[d]
    if style == 'button': hd, hh = 1.75 * d, 0.55 * d
    if style == 'csk':
        hd = 2 * d; hh = (hd - d) / 2
        s = cq.Solid.makeCone(hd / 2, d / 2, hh).fuse(cq.Solid.makeCylinder(d / 2 - .04, L - hh, V(0, 0, hh)))
        return s.cut(hexsolid(max(1.3, key - 0.5), hh * .75, -.01)).clean()
    s = cq.Solid.makeCylinder(d / 2 - .04, L).fuse(cq.Solid.makeCylinder(hd / 2, hh, V(0, 0, -hh)))
    return s.cut(hexsolid(key, hh * .6 + .01, -hh - .01)).clean()
def washer(d): return cq.Solid.makeCylinder(DIM[d][5] / 2, DIM[d][6]).cut(cq.Solid.makeCylinder(d / 2 + .2, DIM[d][6]))
def nut(d): return hexsolid(DIM[d][3], DIM[d][4]).cut(cq.Solid.makeCylinder(d / 2 + .06, DIM[d][4]))
def insert_solid(d): sp = INSERTS[d]; return cq.Solid.makeCylinder(sp['od'] / 2, sp['length']).cut(cq.Solid.makeCylinder(d / 2 + .06, sp['length']))

# ---------------------------------------------------------------- joints
J = []
def joint(label, d, style, p, v, layers, variants=('printed', 'cnc'), note='', cbore=False):
    """layers: [(role, [part names or prefixes])] in order along v from the head side. role: clear | insert | tap | pilot | nut"""
    J.append(dict(label=label, d=d, style=style, p=tuple(map(float, p)), v=tuple(map(float, v)), layers=layers, variants=variants, note=note, cbore=cbore))

PLATE = ['S01_V44_PRINT_bottom_plate', 'S01_V44_CNC_bottom_plate']
RPLATE = ['S01_V44_PRINT_bottom_plate', 'S17_V44_CNC_rear_plate']
BAR = ['S17_V44_AL_flat_bar']
COVERS = ['V44_PRINT_cover_', 'V44_PRINT_end_cap_']
BZ0 = ST['BAR_Z'][0]
for i, (x, y) in enumerate(ST['BAR_SCREWS']):
    joint(f'bar_{i}', 4, 'csk', (x, y, BZ0), UP, [('clear', BAR), ('insert', PLATE)], ('printed',), 'Flat bar to the printed bottom plate: M4 countersunk up through the bar into a heat-set insert.')
for i, (x, y) in enumerate(ST['ODRIVE_FEET']):
    joint(f'odrive_foot_{i}', 4, 'csk', (x, y, BZ0), UP, [('clear', BAR), ('clear', PLATE), ('insert', ['MOUNT_ODrive_Pro_bracket'])], ('printed',), 'ODrive bracket foot: M4 up through bar and plate slot into its insert.')
    joint(f'odrive_foot_{i}', 4, 'csk', (x, y, -5.0), UP, [('clear', PLATE), ('insert', ['MOUNT_ODrive_Pro_bracket'])], ('cnc',), 'ODrive bracket foot: M4 up through the plate slot into its insert.')
for i, (x, y) in enumerate(ST['FRAME_DOWN']):
    joint(f'exit_plate_{i}', 4, 'csk', (x, y, -5.0), UP, [('clear', PLATE), ('insert', ['FM10_Square_back_plate'])], note='Square back plate (fairlead) to the bottom plate: M4 up into its insert.')
for i, (x, y) in enumerate(ST['BOARD_PLATE_SCREWS']):
    joint(f'board_plate_{i}', 3, 'socket', (x, y, -5.0), UP, [('clear', PLATE), ('insert', ['MOUNT_front_board_plate'])], note='Front board plate foot: M3 up through the plate (head in a counterbore) into its insert.', cbore=True)
for i, x in enumerate(SH['cover_screws']):
    joint(f'cover_back_{i}', 3, 'csk', (x, BW.outer(x), 90.0), FWD, [('clear', RPLATE), ('insert', COVERS)], note='Cover to the rear plate: M3 countersunk from the back (flush, D6) into the cover boss insert.')
for i, (x, y) in enumerate(SH['boss_xy'] + [list(b) for b in SH['cap_bosses']]):
    on_bar = any(abs(y - (y0 + y1) / 2) < 12.7 + 3 for y0, y1 in ((-105.0, -79.6), (-46.0, -20.6))) and x > -81.0
    if on_bar:
        joint(f'cover_foot_{i}', 3, 'csk', (x, y, BZ0), UP, [('clear', BAR), ('clear', PLATE), ('insert', COVERS)], ('printed',), 'Cover / cap foot boss: M3 up through the bar and plate into its insert.')
        joint(f'cover_foot_{i}', 3, 'csk', (x, y, -5.0), UP, [('clear', PLATE), ('insert', COVERS)], ('cnc',), 'Cover / cap foot boss: M3 up through the plate into its insert.')
    else:
        joint(f'cover_foot_{i}', 3, 'csk', (x, y, -5.0), UP, [('clear', PLATE), ('insert', COVERS)], note='Cover / cap foot boss: M3 up through the plate into its insert.')
FX, FZ = ST['FAN']
for i, (dx, dz) in enumerate(((-16, -16), (16, -16), (-16, 16), (16, 16))):
    # round 13: from the back (heads behind the rear plate) - nothing stands in front of the fan, where the phase leads reach the ODrive terminal
    joint(f'fan_{i}', 3, 'csk', (FX + dx, BW.outer(FX), FZ + dz), FWD, [('clear', RPLATE), ('clear', ['MOUNT_fan_duct']), ('pilot', ['TRIAL_driver_fan'], {'depth': 8.0})],
          note='ODrive fan: M3 countersunk from the back (flush, D6) through the rear plate and duct, self-tapping into the fan corner holes.')
for i, (x, z) in enumerate(ST['JUNCTION_SCREWS']):
    joint(f'wago_bracket_{i}', 3, 'socket', (x, -1.6, z), BACK, [('clear', ['MOUNT_power_junction_bracket']), ('insert', RPLATE)], ('printed',), 'WAGO bracket: M3 into a rear-plate insert.')
    joint(f'wago_bracket_{i}', 3, 'socket', (x, -1.6, z), BACK, [('clear', ['MOUNT_power_junction_bracket']), ('tap', RPLATE)], ('cnc',), 'WAGO bracket: M3 into the tapped rear plate.')
RC = ST['REAR_CNC_Y']
for i, (x, z) in enumerate(ST['CLEVIS_M6']):
    joint(f'clevis_{i}', 6, 'csk', (x, RC[1] + 10.0, z), FWD, [('clear', ['R07_V44_PRINT_rack_clevis']), ('tap', ['S17_V44_CNC_rear_plate'])], ('cnc',), 'Rack clevis flange to the rear plate: M6 countersunk into the tapped plate.')
for i, (x, y) in enumerate(ST['BLOCK_SCREWS']):
    cradle = y > -30.0                                                                  # the fuse cradles (the rest are shaft-2 pedestals)
    joint(f'block_{i}', 3, 'csk', (x, y, -5.0), UP, [('clear', PLATE), ('pilot' if cradle else 'insert', ['MOUNT_fuse_holder_saddles'] if cradle else ['FM10_Shaft_2_bearing_pedestal'])], ('cnc',),
          'Fuse cradle to the CNC plate: M3 self-tapping into its 3.8 mm base (the holder sits on it).' if cradle else 'Shaft-2 pedestal to the CNC plate: M3 up into its insert (printed variant: fused to the plate).')
for i, x in enumerate((-35.0, 60.0)):
    joint(f'screen_leg_{i}', 3, 'csk', (x, -137.0, 38.9), BACK, [('clear', ['V44_PRINT_cover_left_screen']), ('insert', ['MOUNT_screen_rear_retaining_frame'])], note='Screen frame leg: M3 countersunk from the front (flush under the bezel edge) into the leg insert.')
for i, (x, y, z0, r) in enumerate(SH['ceil']):
    if r < 1.9:
        joint(f'pi_top_{i}', 2.5, 'csk', (x, y, ZT), DOWN, [('clear', ['V44_PRINT_cover_']), ('tap', ['MOUNT_Pi_ceiling_standoffs'])], note='Pi standoff to the cover top: M2.5 countersunk from above.')
        joint(f'pi_board_{i}', 2.5, 'socket', (x, y, z0 - 1.8), UP, [('clear', ['TRIAL_Pi4_upright']), ('tap', ['MOUNT_Pi_ceiling_standoffs'])], note='Pi to its standoff: M2.5 from below through the board.')
    else:
        joint(f'bms_{i}', 3, 'csk', (x, y, ZT), DOWN, [('clear', ['V44_PRINT_cover_']), ('clear', ['MOUNT_BMS_ceiling_standoffs']), ('clear', ['JBD_SP17S005']), ('nut', [])], note='BMS to the cover top: M3 countersunk from above through the spacer and board, nut under the board.')
for i, dz in enumerate((-12.49, 12.49)):
    joint(f'xt60_{i}', 2.5, 'csk', (268.0, 20.5, 72.8 + dz), FWD, [('clear', ['AMASS_XT60E-F'], {'max': 3.1}), ('pilot', ['V44_PRINT_rear_IO_panel'])], note='XT60E-F flange: M2.5 countersunk (countersink the flange holes) self-tapping into the backing frame.')
for i, (x, z) in enumerate(SH['io_tabs']):
    joint(f'io_tab_{i}', 2.5, 'socket', (x, 14.95, z), BACK, [('clear', ['V44_PRINT_rear_IO_panel']), ('pilot', ['V44_PRINT_cover_right'])], note='Rear I/O panel tab: M2.5 self-tapping into the step wall.')

for i, (y, z) in enumerate([(y, z) for y in (-92.48, -32.48) for z in (13.01, 73.01)]):
    joint(f'odrive_spreader_{i}', 4, 'socket', (220.0, y, z), (-1, 0, 0), [('clear', ['V3_ODrive_heat_spreader']), ('clear', ['MOUNT_ODrive_Pro_bracket']), ('nut', dict(recess=3.5))],
          note='ODrive heat spreader to the bracket post: M4 from the board side, nut in the hex pocket on the far face.')

STANDOFF_TRIM = {}                                                                     # standoff part -> perfboard face Y (keep the plate side)
def standoff_joints():
    """Board standoffs on the front plate: M2.5 through the perfboard and the standoff into a plate insert."""
    out = []
    for n in ('MOUNT_Teensy_perfboard_standoffs', 'MOUNT_CAN_board_perfboard_standoffs', 'MOUNT_regulator_perfboard_standoffs'):
        f = H / 'printed' / (n + '.brep')
        if not f.exists(): continue
        board = {'Teensy': 'TRIAL_Teensy', 'CAN': 'TRIAL_CAN_headers', 'regulator': 'TRIAL_Pololu5571'}[n.split('_')[1]]
        pb = max((q for q in cq.Shape.importBrep(str(H / 'printed' / (board + '.brep'))).Solids() if q.BoundingBox().ylen < 2.2 and q.Volume() > 300),
                 key=lambda q: q.Volume()).BoundingBox()                               # the perfboard (bigger than the board on it)
        STANDOFF_TRIM[n] = pb.ymin
        for k, s in enumerate(cq.Shape.importBrep(str(f)).Solids()):
            b = s.BoundingBox(); x, z = (b.xmin + b.xmax) / 2, (b.zmin + b.zmax) / 2
            joint(f"standoff_{n.split('_')[1]}_{k}", 2.5, 'socket', (x, pb.ymax, z), FWD,
                  [('clear', [board], {'max': pb.ylen + 0.05}), ('clear', [n]), ('insert', ['MOUNT_front_board_plate'])],
                  note='Board standoff: M2.5 through the board and the standoff into a front-plate insert.')
standoff_joints()

# ---------------------------------------------------------------- build
def extent(shape, p, v, r_in, r_out, t0=-3.0, t1=80.0):
    """Where along the axis the part has material near the hole (a tube round the axis, so an existing hole does not hide it)."""
    tube = cyl(r_out, p, v, t0, t1).cut(cyl(r_in, p, v, t0 - 1, t1 + 1))
    try: sec = shape.intersect(tube)
    except Exception: return None
    if sec.Volume() < 1e-3: return None
    segs = []
    for q in (sec.Solids() or [sec]):                                     # each separate piece of material along the axis
        vs, _ = q.tessellate(0.2, 0.5)
        if not vs: continue
        t = (np.array([[w.x, w.y, w.z] for w in vs]) - np.asarray(p, float)) @ np.asarray(v, float)
        segs.append((float(t.min()), float(t.max())))
    segs = sorted(sg for sg in segs if sg[1] > t0 + 0.5)
    if not segs: return None
    return segs[0]                                                        # the first piece met

def resolve(names, shapes, p, v, r, lo=-2.5):
    """Every candidate part with material round the axis beyond lo, nearest first."""
    out = []
    for pre in names:
        for n in shapes:
            if n == pre or n.startswith(pre):
                e = extent(shapes[n], p, v, r + 0.3, r + 2.0, t0=lo)
                if e is None: e = extent(shapes[n], p, v, r + 0.3, r + 4.0, t0=lo)
                if e is not None: out.append((n, e))
    return sorted(out, key=lambda t: t[1][0])

report = {}
for mode in ('printed', 'cnc'):
    r = REV[mode]; d_ = H / mode
    for n in [n for n in r['parts'] if n.startswith('F44_')]:                            # idempotent re-runs
        r['parts'].remove(n); r['meta'].pop(n, None); r['colors'].pop(n, None)
        for ext in ('.brep', '.step'): (d_ / (n + ext)).unlink(missing_ok=True)
    for vv in r['views'].values(): vv[:] = [n for n in vv if not n.startswith('F44_')]
    r['expected_interference'] = [e for e in r.get('expected_interference', []) if not str(e[0]).startswith('F44_')]
    # re-runs start from the parts as the shell left them (.prefast/), never from this step's own output (a second
    # countersink cut would sink the seat 0.6 mm deeper each run)
    pre = d_ / '.prefast'; pre.mkdir(exist_ok=True); pst_f = pre / 'state.json'
    pstate = json.loads(pst_f.read_text()) if pst_f.exists() else {}
    from_pre = {n for n in pstate if (pre / (n + '.brep')).exists() and (d_ / (n + '.brep')).exists() and VC.file_sha(d_ / (n + '.brep')) == pstate[n]}
    shapes = {n: cq.Shape.importBrep(str((pre if n in from_pre else d_) / (n + '.brep'))) for n in r['parts'] if not n.startswith(('WIRE_', 'HARNESS_'))}
    written = set()
    cutters = {}; hw = []; extra_hosts = []; log = dict(added=[], oversize=[], joints=[], unresolved=[])
    for n, yf in STANDOFF_TRIM.items():                                                # standoffs end on the perfboard face
        if n in shapes:
            trim = cq.Solid.makeBox(200, 60, 200, V(-150, yf, -50)); shapes[n] = shapes[n].cut(trim); cutters.setdefault(n, []).append(trim)
    def need_cut(n, c_small, c_ring):
        s = shapes[n]
        try:
            v1 = s.intersect(c_small).Volume()
            v2 = s.intersect(c_ring).Volume() if c_ring is not None else 1.0
        except Exception: return False, False
        return v1 > 0.05, v2 < 0.01
    for j in J:
        if mode not in j['variants']: continue
        d, p, v = j['d'], np.array(j['p']), np.array(j['v'])
        hosts = []
        nut_opt = None
        for lay in j['layers']:
            role, names = lay[0], lay[1]; lopt = lay[2] if len(lay) > 2 else {}
            if role == 'nut': nut_opt = names if isinstance(names, dict) else {}; hosts.append((role, None, None)); continue
            prev = [h for h in hosts if h[2]]
            found = resolve(names, shapes, p, v, d / 2, (prev[-1][2][1] - 1.0) if prev else -2.5)
            if not found: log['unresolved'].append(dict(joint=j['label'], role=role, candidates=names)); hosts.append((role, None, None)); continue
            n, e = found[0]
            if lopt.get('max'): e = (e[0], min(e[1], e[0] + lopt['max']))
            hosts.append((role, n, e))
            for n2, e2 in found[1:]:                                            # lap joints: the other piece on the same stretch of axis
                if n2 != n and e2[0] < e[1] - 0.2: hosts.append((role, n2, (max(e2[0], e[0]), e2[1])))
        first = next((h for h in hosts if h[1]), None)
        if first is None: continue
        seat = first[2][0]                                                           # head seat: where the first part starts
        ps = p + v * seat
        clamp_end = seat; engage_from = engage_to = None; min_engage = 0.0
        for role, n, e in hosts:
            if n is None: continue
            metal = not printed_part(n)
            t0, t1 = e[0] - seat, e[1] - seat
            if role == 'clear':
                dia = CLEAR['metal' if metal else 'printed'][d]
                c = cyl(dia / 2, ps, v, t0 - 0.3, t1 + 0.3); clamp_end = max(clamp_end, e[1])
                try: ring = cyl(dia / 2 + 0.35, ps, v, t0 + 0.2, t1 - 0.2).cut(cyl(dia / 2, ps, v, t0, t1))
                except Exception: ring = None
                miss, over = need_cut(n, cyl(dia / 2 - 0.15, ps, v, t0 + 0.2, t1 - 0.2), ring)
            elif role == 'insert':
                sp = INSERTS[d]; depth = min(sp['length'] + 1.0, t1 - t0 - 0.4) if not n.startswith(('S01_', 'S17_')) or t1 - t0 > sp['length'] + 1.4 else min(sp['length'] + 0.5, t1 - t0 - 0.5)
                depth = max(depth, sp['length'] + 0.3) if t1 - t0 >= sp['length'] + 0.3 else t1 - t0
                c = cyl(sp['hole'] / 2, ps, v, t0 - 0.3, t0 + depth).fuse(cq.Solid.makeCone(sp['hole'] / 2 + 0.25, sp['hole'] / 2, 0.5, V(*(ps + v * t0)), V(*v)))
                miss, over = need_cut(n, cyl(sp['hole'] / 2 - 0.15, ps, v, t0 + 0.2, t0 + depth - 0.2), cyl(sp['hole'] / 2 + 0.35, ps, v, t0 + 0.6, t0 + depth - 0.2).cut(cyl(sp['hole'] / 2, ps, v, t0, t0 + depth)))
                iname = f"F44_I_{j['label']}_M{d:g}"
                if not any(h[0] == iname for h in hw):
                    engage_from, engage_to = t0, t0 + sp['length']
                    hw.append((iname, orient(insert_solid(d), ps + v * t0, v), BRASS, 'insert', f'M{d:g} heat-set insert L{sp["length"]:g} (Ruthex RX)', n))
                else:
                    extra_hosts.append((iname, n))
                if t1 - t0 < sp['length'] - 0.05: log.setdefault('shallow', []).append(dict(joint=j['label'], part=n, depth=round(t1 - t0, 2)))
            elif role in ('tap', 'pilot'):
                dia = (TAP if role == 'tap' else PILOT)[d]; blind = role == 'pilot'
                deep = lopt.get('depth') or (min(t1 - t0 - 0.5, 2.5 * d) if blind else t1 - t0 + 0.3)
                c = cyl(dia / 2, ps, v, t0 - 0.3, t0 + deep)
                miss, over = need_cut(n, cyl(dia / 2 - 0.1, ps, v, t0 + 0.2, t0 + deep - 0.2), None)
                if 'standoffs' in n: deep = (t1 - t0) / 2 + 0.3                    # a standoff takes a screw from each end
                engage_from, engage_to = t0, t0 + deep - 0.3
                min_engage = min((0.6 * d) if 'standoffs' in n else (1.5 * d if role == 'tap' else 2.0 * d), deep - 0.5)
            else:
                continue
            cutters.setdefault(n, []).append(c)
            if miss: log['added'].append(dict(joint=j['label'], part=n, role=role))
            if over: log['oversize'].append(dict(joint=j['label'], part=n, role=role))
        # head seat features in the first part
        n0 = first[1]
        if j['style'] == 'csk':
            hd = 2 * d; cutters.setdefault(n0, []).append(cq.Solid.makeCone(hd / 2 + 0.15, d / 2 + 0.1, (hd - d) / 2 + 0.05, V(*ps), V(*v)))
        if j['cbore']:
            cutters.setdefault(n0, []).append(cyl(DIM[d][0] / 2 + 0.45, ps, v, -0.1, DIM[d][1] + 0.2)); ps2 = ps + v * (DIM[d][1] + 0.2)
        else: ps2 = ps
        # screw length: fully through the insert / thread, never bottoming; nut joints: past the nut
        base = float((ps2 - ps) @ v)
        if engage_to is not None:
            last = [h for h in hosts if h[1]][-1][0]
            need = engage_to - base; room = need + (0.9 if last == 'insert' else 0.0)
            hl = [h for h in hosts if h[1]][-1]; t_end = hl[2][1] - seat - base         # far face of the last part (screw-length coords)
            if room > t_end:                                                         # the tip would leave it: only into free space
                probe = cyl(d / 2, ps2, v, t_end + 0.02, room + 0.1); pb_ = probe.BoundingBox()
                own_ = {h[1] for h in hosts if h[1]}
                for m_, t_ in shapes.items():
                    if m_ in own_ or m_.startswith('F44_'): continue
                    c_ = t_.BoundingBox()
                    if c_.xmin > pb_.xmax or c_.xmax < pb_.xmin or c_.ymin > pb_.ymax or c_.ymax < pb_.ymin or c_.zmin > pb_.zmax or c_.zmax < pb_.zmin: continue
                    try: hit = t_.intersect(probe).Volume() > 1e-3
                    except Exception: hit = False
                    if hit: room = t_end; break
            floor_ = engage_from - base + (3.0 if last == 'insert' else min_engage)
            fits = [s_ for s_ in STD if floor_ - 1e-6 <= s_ <= room + 1e-6]
            if not fits:                                                             # short thread: the longest screw that fits, if it still bites 0.6 d
                fits = [s_ for s_ in STD if s_ <= room + 1e-6 and s_ - (engage_from - base) >= 0.6 * d]
            L = max(fits) if fits else min(s_ for s_ in STD if s_ >= floor_)
            if not fits: log.setdefault('length_compromise', []).append(dict(joint=j['label'], need=round(need, 2), used=L))
        else:
            rec = (nut_opt or {}).get('recess'); wt, nt = DIM[d][6], DIM[d][4]
            need = clamp_end - seat - base + (nt - rec + 0.8 if rec else wt + nt + 0.8)
            L = min(s for s in STD if s >= need)
        head_len = 0.0
        bolt_s = orient(bolt(d, L, j['style']), ps2, v)
        name = f"F44_B_{j['label']}_M{d:g}x{L}_{j['style']}"
        hw.append((name, bolt_s, BLACK if j['style'] == 'socket' else STEEL, 'fastener', f"M{d:g}x{L} {dict(socket='socket head (ISO 4762)', csk='countersunk (ISO 10642)', button='button head (ISO 7380)')[j['style']]}", None))
        if nut_opt is not None:
            pe = ps + v * (clamp_end - seat)
            if nut_opt.get('recess'):                                        # nut sits in a hex pocket in the last part
                hw.append((f"F44_N_{j['label']}_M{d:g}", orient(nut(d), pe - v * nut_opt['recess'], v), STEEL, 'fastener', f'M{d:g} hex nut (ISO 4032), in its pocket', None))
            else:
                hw.append((f"F44_W_{j['label']}_M{d:g}", orient(washer(d), pe, v), STEEL, 'fastener', f'M{d:g} washer (ISO 7089)', None))
                hw.append((f"F44_N_{j['label']}_M{d:g}", orient(nut(d), pe + v * DIM[d][6], v), STEEL, 'fastener', f'M{d:g} nyloc nut (ISO 10511)', None))
        log['joints'].append(dict(joint=j['label'], screw=name, hosts=[[role, n] for role, n, _ in hosts if n], note=j['note']))
    # cut every part once
    VENDOR = ('TRIAL_', 'JBD_', 'AMASS_', 'V3_', 'SameSky_', 'goBILDA', 'SKF_', 'KHK_', 'ThunderPower', 'Littelfuse', 'NBK_', 'REF_', 'ServoCity')
    for n, cs in cutters.items():
        s0 = shapes[n]
        if n.startswith(VENDOR) or len(s0.Solids()) > 1 and not n.startswith(('MOUNT_', 'S01_', 'S17_', 'V44_', 'R07_', 'FM10_')):
            log.setdefault('not_cut', []).append(n); continue                          # vendor / mock models: their holes are taken as they are
        s = s0
        for c in cs:
            try: s = s.cut(c)
            except Exception: log['unresolved'].append(dict(part=n, cut_failed=True))
        s = s.clean() if s.isValid() else s
        if not s.isValid() or s.Volume() > s0.Volume() + 0.01 or s0.Volume() - s.Volume() > sum(c.Volume() for c in cs) + 1.0:
            log.setdefault('cut_reverted', []).append(n); continue                    # a bad boolean: keep the part as it was
        shapes[n] = s
        if n not in from_pre: shutil.copyfile(d_ / (n + '.brep'), pre / (n + '.brep'))   # keep the shell's version for re-runs
        shapes[n].exportBrep(str(d_ / (n + '.brep'))); shapes[n].exportStep(str(d_ / (n + '.step')))
        pstate[n] = VC.file_sha(d_ / (n + '.brep')); written.add(n)
    for n in from_pre - written:                                                      # cut last run, not now: back to the shell's version
        if n in shapes: shapes[n].exportBrep(str(d_ / (n + '.brep'))); shapes[n].exportStep(str(d_ / (n + '.step')))
        pstate.pop(n, None)
    pst_f.write_text(json.dumps(pstate))
    # clash check of the new hardware (their joint hosts excluded; knurl / thread overlap is intended)
    hosts_of = {}
    for jj in log['joints']:
        for role, n in jj['hosts']: hosts_of.setdefault(jj['joint'], set()).add(n)
    bbs = {n: s.BoundingBox() for n, s in shapes.items()}
    clash = []
    for name, s, col, kind, size, host in hw:
        lab = name.split('_', 2)[2].rsplit('_M', 1)[0]
        own = hosts_of.get(lab, set()) | ({host} if host else set()) | {h for nn, h in extra_hosts if nn == name}
        b = s.BoundingBox()
        for m, t in shapes.items():
            if m in own or m.startswith('F44_'): continue
            c = bbs[m]
            if c.xmin > b.xmax or c.xmax < b.xmin or c.ymin > b.ymax or c.ymax < b.ymin or c.zmin > b.zmax or c.zmax < b.zmin: continue
            vv = VC.clash_volume(s, t)
            if abs(vv) > 0.01: clash.append((name, m, round(vv, 3)))
    log['clashes'] = clash
    # write the hardware
    for name, s, col, kind, size, host in hw:
        s.exportBrep(str(d_ / (name + '.brep'))); s.exportStep(str(d_ / (name + '.step')))
        r['parts'].append(name); r['colors'][name] = list(col)
        r['meta'][name] = dict(group='fasteners', kind=kind, size=size, note=size + (f' in {host}' if host else ''), manufacture='Buy', demo_name='', source='build_v44_fasteners.py', **({'host': host} if host else {}))
        for vw in ('complete', 'open', 'io_access'): r['views'][vw].append(name)
        if host: r['expected_interference'].append([name, host])
    for name, host in extra_hosts: r['expected_interference'].append([name, host])
    r['hardware'] = [h for h in r.get('hardware', []) if h.get('part') in r['parts'] and not str(h.get('part')).startswith('F44_')] + \
        [dict(part=n, group='fasteners', kind=k, size=sz, source='build_v44_fasteners.py', note=sz) for n, _, _, k, sz, _ in hw]
    r['insert_reference'] = {f'M{k:g}': v for k, v in INSERTS.items()}
    (d_ / 'revision.json').write_text(json.dumps(r, indent=1))
    import csv
    with open(d_ / 'hardware.csv', 'w', newline='', encoding='utf-8') as fh:
        wtr = csv.DictWriter(fh, fieldnames=['part', 'group', 'kind', 'size', 'source', 'note'], extrasaction='ignore'); wtr.writeheader(); wtr.writerows(r['hardware'])
    # unused holes: screw-size cylindrical holes in made parts that no screw axis passes through
    axes = []
    for n in r['parts']:
        if n.startswith(('F44_B_', 'V43_B_', 'B_V21', 'B_V37', 'FM10_Carrier_M3', 'FM10_Hub_retainer_M3x', 'FM10_Oval_clamp_M3x', 'FM10_ISO7379')):
            b = cq.Shape.importBrep(str(d_ / (n + '.brep'))).BoundingBox(); ext = np.array([b.xlen, b.ylen, b.zlen])
            axes.append((np.array([(b.xmin + b.xmax) / 2, (b.ymin + b.ymax) / 2, (b.zmin + b.zmax) / 2]), np.eye(3)[int(np.argmax(ext))]))
    for j in J:
        if mode in j['variants']: axes.append((np.array(j['p']), np.array(j['v'], float)))
    unused = []
    SCAN = ('S01_', 'S17_V44_CNC', 'V44_PRINT_', 'MOUNT_', 'R07_', 'FM10_Square_back_plate', 'V43_PRINT_', 'V43_METAL_')
    for n in r['parts']:
        if not n.startswith(SCAN): continue
        seen = set(); arcs = {}
        faces = cq.Shape.importBrep(str(d_ / (n + '.brep'))).Faces()
        def akey(ax, rad):
            o = np.array([ax.Location().X(), ax.Location().Y(), ax.Location().Z()]); dv = np.array([ax.Direction().X(), ax.Direction().Y(), ax.Direction().Z()])
            dv = dv * (1 if dv[np.argmax(np.abs(dv))] > 0 else -1); o = o - dv * (o @ dv)
            return (tuple(np.round(o, 1)), tuple(np.round(dv, 2)), round(rad, 2))
        for f in faces:                                                        # a hole is a full circle, maybe split in pieces
            ad = BRepAdaptor_Surface(f.wrapped)
            if ad.GetType() != GeomAbs_Cylinder: continue
            k_ = akey(ad.Cylinder().Axis(), ad.Cylinder().Radius()); arcs[k_] = arcs.get(k_, 0.0) + (ad.LastUParameter() - ad.FirstUParameter())
        full = {k_ for k_, a_ in arcs.items() if a_ > 2 * math.pi - 0.05}
        for f in faces:
            ad = BRepAdaptor_Surface(f.wrapped)
            if ad.GetType() != GeomAbs_Cylinder: continue
            cy_ = ad.Cylinder(); rad = cy_.Radius()
            if not 0.95 < rad < 3.5: continue
            ax = cy_.Axis(); o = np.array([ax.Location().X(), ax.Location().Y(), ax.Location().Z()]); dv = np.array([ax.Direction().X(), ax.Direction().Y(), ax.Direction().Z()])
            c = f.Center(); cc = np.array([c.x, c.y, c.z]); foot = o + dv * ((cc - o) @ dv)
            if np.linalg.norm(cc - foot) > rad + 0.05: continue                     # convex (a boss / pin), not a hole
            key = (n, tuple(np.round(foot - dv * (foot @ dv), 0)), round(rad, 2))
            if key in seen: continue
            seen.add(key)
            if akey(ax, rad) not in full: continue                              # an arc: a fillet or a slot end
            used = any(abs(abs(dv @ a[1]) - 1) < 0.01 and np.linalg.norm(np.cross(foot - a[0], a[1])) < 0.8 for a in axes)
            vent = n.startswith(('S01_', 'S17_')) and abs(foot[0] - ST['FAN'][0]) < 17 and abs(foot[2] - ST['FAN'][1]) < 17 and abs(dv[1]) > 0.99 and rad > 1.9
            if not used and not vent: unused.append(dict(part=n, at=[round(float(q), 1) for q in foot], dia=round(2 * rad, 2), axis=[round(float(q), 2) for q in dv]))
    log['unused_holes'] = unused
    report[mode] = log
    print(mode, 'hardware', len(hw), '| holes added', len(log['added']), '| oversize', len(log['oversize']), '| clashes', len(clash),
          '| unresolved', len(log['unresolved']), '| unused holes', len(unused), '| shallow', len(log.get('shallow', [])))
(H / 'fasteners-report.json').write_text(json.dumps(report, indent=1))
