"""V44 fix list E1-E8: compact enclosure on the bottom plate (same for both variants). Run after build_v44_structure.py.

- E1: covers and end caps stand on the bottom plate (no bottom pans). Bosses at the foot of the walls take M3 from below through the
  plate into heat-set inserts; bosses are placed only where they clear every part inside, never over the ladder or the uprights.
- E2: centre cover open below the square exit frame (U opening), so it lifts off without touching the swivel.
- E3: the rear upright is the back wall behind the boards; the back step at the battery end carries a flush rear I/O panel
  (charge port above the power switch, D7).
- E4: no Pi port window. E5: both end caps plain (handle is the aluminium end loop, S5).
- E6: seams at X 98 and 172 are half-lapped (1.5 mm each, 6 mm overlap).
- E7: intake slots on the motor end cap and the screen-side ribs; small front grille over the ODrive only; fan exhausts at the back.
- E8: board standoffs need to be 1 mm longer to reach the rear upright (hardware note).
World frame: X shaft (motor -X), -Y front, Z up, plate top Z 0. Exterior X -81..290, Y -137..5.5 (+ step to 20.5 at X 248..290), top 96.5.
"""
from pathlib import Path
import json, csv
import numpy as np
import cadquery as cq
import v44cache as VC
import back_wall as BW                                   # round 9: stepped back wall                                   # round 8: cached clash checks (.cache/)

H = Path(__file__).resolve().parent
REV = {m: json.loads((H / m / 'revision.json').read_text()) for m in ('cnc', 'printed')}
X0E, X1E, Y0E, Y1E, ZT = -81.0, 290.0, -137.0, 5.5, 96.5
STEP_X, STEP_Y = 248.0, 20.5
W, RT, CAP = 3.0, 9.0, 10.0
X0B, X1B = X0E + CAP, X1E - CAP
SEAMS = (98.0, 172.0)
REAR_UP = (80.0, 188.0, 2.5, 8.5, 90.0)                     # x0, x1, y0, y1, top
EXIT = dict(x=(99.9, 170.5), ztop=74.3)                      # R4-1: U opening; the square back plate front (X 100.2..170.2, top 74) is flush in it
IO = dict(x=(252.0, 276.5), z=(40.0, 90.0))                  # rear I/O panel on the back step
def box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))
def ycyl(r, x, z, y0, y1): return cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))
def zcyl(r, x, y, z0, z1): return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1))
def xcyl(r, y, z, x0, x1): return cq.Solid.makeCylinder(r, x1 - x0, cq.Vector(x0, y, z), cq.Vector(1, 0, 0))
def fuse(solids):
    solids = [s for s in solids]; return solids[0] if len(solids) == 1 else solids[0].fuse(*solids[1:]).clean()
def bb(s): b = s.BoundingBox(); return np.array([b.xmin, b.ymin, b.zmin]), np.array([b.xmax, b.ymax, b.zmax])

def zone_box(x0, x1, yb, off, z0, r):
    return cq.Workplane('XY').box(x1 - x0, (yb - off) - (Y0E + off), ZT - off - z0, centered=False).translate((x0, Y0E + off, z0)) \
        .edges('|X and >Z').fillet(r).val()

def body(x0, x1, off, z0=0.0):
    """Outer body offset inward by `off`: rounded top long edges, the stepped back (round 9 zones), the back step at the battery end,
    flat bottom on the plate. At a zone step the shallower zone gives up `off` of its length so the step wall has thickness."""
    r = max(RT - off, 0.5); parts = []
    zs = BW.ZONES
    for i, (a0, a1, d) in enumerate(zs):
        lo = a0 if i else min(x0, a0); hi = a1 if i < len(zs) - 1 else max(x1, a1)
        # round 11: the step wall between zones sits inside the shallower zone (behind its plate): the deeper zone's box runs `off` into it
        if i and zs[i - 1][2] < d: lo -= off
        if i and zs[i - 1][2] > d: lo += off
        if i < len(zs) - 1 and zs[i + 1][2] < d: hi += off
        if i < len(zs) - 1 and zs[i + 1][2] > d: hi -= off
        lo, hi = max(lo, x0), min(hi, x1)
        if hi > lo: parts.append(zone_box(lo, hi, Y1E + d, off, z0, r))
    main = parts[0].fuse(*parts[1:]).clean() if len(parts) > 1 else parts[0]
    hx0, hx1 = BW.PI_HOOD['x'] if BW.PI_HOOD else (0.0, 0.0)       # hood over the Pi's USB plugs (zone A, top only; none since round 12)
    if BW.PI_HOOD and hx1 > x0 and hx0 < x1:
        hood = cq.Workplane('XY').box((hx1 - off) - (hx0 + off), (BW.PI_HOOD['y_in'] + W - off) - (Y1E + zs[0][2] - RT), ZT - off - (BW.PI_HOOD['z_floor'] + off),
                                      centered=False).translate((hx0 + off, Y1E + zs[0][2] - RT, BW.PI_HOOD['z_floor'] + off)).edges('|X and >Z and >Y').fillet(r).val()
        main = main.fuse(hood).clean()
    if x1 > STEP_X + off:
        xs = max(x0, STEP_X + off)
        st = cq.Workplane('XY').box(x1 - xs, (STEP_Y - off) - (Y1E - RT), ZT - off - z0, centered=False) \
            .translate((xs, Y1E - RT, z0)).edges('|X and >Z and >Y').fillet(r).val()
        main = main.fuse(st).clean()
    return main
outer = body(X0B, X1B, 0.0); inner = body(X0B - 1, X1B + 1, W, z0=-1.0)
shell = outer.cut(inner)
cut, add = [], []
# R4-6: the rear plate is the back wall from the motor end cap to the back step (X -81..248); covers keep their top over it
PLATE_ZONE = fuse([box(max(x0, X0E - 1.0) if i else X0E - 1.0, x1, BW.INNER0 + d - 0.1, 30.0, -1.0, 93.49) for i, (x0, x1, d) in enumerate(BW.ZONES)]
                  + [box(cx0, cx1, cy0 - 0.1, 30.0, -1.0, 93.49) for cx0, cx1, cy0, cy1 in BW.connectors()])        # round 9: stepped plate zone
if BW.PI_HOOD: PLATE_ZONE = PLATE_ZONE.cut(box(*BW.PI_HOOD['x'], -60.0, 40.0, BW.PI_HOOD['z_floor'], 100.0))                   # the cover forms the Pi hood
cut.append(PLATE_ZONE)
# E2: U opening under the exit frame
cut.append(box(*EXIT['x'], Y0E - 1, Y0E + W + 1, -1.0, EXIT['ztop']))
# screen window + vent ribs (E7 intake), no Pi window (E4)
cut.append(box(-32.1, 52.9, Y0E - 1, Y0E + W + 1, -1.9, 83.2))
cut += [box(x, x + 2.5, Y0E - 1, Y0E + W + 1, 12.0, 72.0) for x in list(np.arange(-66.0, -37.0, 5.0)) + list(np.arange(63.0, 92.0, 5.0))]
cut += [ycyl(1.7, x, 38.9, Y0E - 1, Y0E + W + 1) for x in (-35.0, 60.0)]                      # R4-8: screen frame legs, M3 x 20 from the front
# E7: small front grille over the ODrive only; fan exhaust grille + screws on the back (X 211, Z 58)
cut += [box(x, x + 26.0, Y0E - 1, Y0E + W + 1, z, z + 2.5) for x in (208.0,) for z in np.arange(16.0, 70.0, 6.0)]
# (R4-6: fan exhaust grille and screws are in the rear plate now)
# E3: rear I/O panel opening in the step's back wall (panel is a separate part)
cut.append(box(IO['x'][0], IO['x'][1], STEP_Y - W - 1, STEP_Y + 1, IO['z'][0], IO['z'][1]))
# L6: battery rear spacer as a rib hanging from the right cover's ceiling (holds the stack forward), windows for the lead route
rib = box(246.0, 282.0, -3.5, 1.5, 3.0, ZT - W + 0.5).cut(box(252.0, 276.0, -3.6, 1.6, 10.0, 59.0)).cut(box(251.5, 262.5, -3.6, 1.6, 66.0, 90.0))
rib = rib.cut(box(262.0, 274.0, -3.6, 1.6, 60.0, 86.0))                    # round 7: window for the XT60E-F solder cups and charge leads
shell = shell.fuse(rib).cut(fuse(cut))

# ------------------------------------------------ E1: fixing bosses at the foot of the walls, placed only where they clear the parts
OWN = ('V44_PRINT_cover_', 'V44_PRINT_end_cap_', 'V44_PRINT_rear_IO_panel_flush', 'MOUNT_Pi_ceiling', 'MOUNT_BMS_ceiling')     # this script's own pieces (idempotent re-runs)
parts = {n: cq.Shape.importBrep(str(H / 'printed' / (n + '.brep'))) for n in REV['printed']['parts'] if not n.startswith(OWN)}
pbb = {n: bb(s) for n, s in parts.items()}
def free(sol, pad=0.5):
    lo, hi = bb(sol); lo, hi = lo - pad, hi + pad
    for n, s in parts.items():
        l2, h2 = pbb[n]
        if (lo > h2).any() or (l2 > hi).any(): continue
        if n.startswith(('S01_', 'S17_', 'R07_')) and not n.startswith('S17_V44_AL_front_upright') and not n.startswith('S17_V44_AL_rear_upright'): continue
        if sol.intersect(s).Volume() > 1e-3: return False
    return True
cands = []
for x in np.arange(-66.0, 280.0, 18.0):
    if not 240.0 < x < 290.0: cands.append((x, Y0E + W + 2.0))    # round 9: no front bosses at the battery (its face is 0.5 mm from the wall)
    if x >= STEP_X: cands.append((x, STEP_Y - W - 2.0))           # the rear plate is the back wall for X < 248
for y in np.arange(-125.0, 0.0, 20.0): cands += [(X0B + 2.0, y)]          # (end caps carry their own bosses below)
bosses = []
for x, y in cands:
    if 95.0 < x < 175.0 and y < -100: continue                              # front upright slot / ladder Y bar
    if any(abs(x - s) < 7 for s in SEAMS): continue                         # half-lap zone
    if -110.5 < y < -72.5 or -52.0 < y < -14.0: continue                    # over the ladder X bars (PRINT): no screw path
    b = zcyl(4.0, x, y, 0.0, 10.0)
    if b.intersect(outer).Volume() > 50.0 and free(b): bosses.append((x, y))     # round 13: inside the body only (no phantom boss)
shell = shell.fuse(fuse([zcyl(4.0, x, y, 0.0, 10.0).intersect(outer) for x, y in bosses])).cut(fuse([zcyl(2.0, x, y, -0.1, 6.0) for x, y in bosses]))

# ------------------------------------------------ L7: ceiling bosses for the upside-down Pi (its own mounting holes) and BMS (corners)
def pi_holes():
    pi = parts['TRIAL_Pi4_upright']; out = set()
    for f in pi.Faces():
        if f.geomType() == 'CYLINDER':
            c = f._geomAdaptor().Cylinder(); d = c.Axis().Direction(); l = c.Axis().Location()
            if 1.2 < c.Radius() < 1.6 and abs(d.Z()) > 0.99: out.add((round(l.X(), 1), round(l.Y(), 1)))
    out = sorted(out)                                                  # keep the 4 mounting holes: the 49 x 58 mm rectangle
    for a in out:
        for b in out:
            if abs((b[0] - a[0]) - 49.0) < 1.0 and abs(b[1] - a[1]) < 0.5:
                for c in out:
                    if abs(c[0] - a[0]) < 0.5 and abs(abs(c[1] - a[1]) - 58.0) < 1.0 and (b[0], c[1]) in out:
                        return [a, b, c, (b[0], c[1])]
    return out
PI_HOLES = pi_holes()
pl, ph = pbb['TRIAL_Pi4_upright']
ph = ph.copy(); ph[2] = max(parts['TRIAL_Pi4_upright'].Solids(), key=lambda q: q.Volume()).BoundingBox().zmax   # round 13: PCB top (the USB stack stands 1.9 higher)
bl, bh = pbb['JBD_SP17S005_BMS_mock_from_spec']
BMS_HOLES = [(x, y) for x in (bl[0] + 5, bh[0] - 5) for y in (bl[1] + 5, bh[1] - 5)]
ceil = []
for (x, y) in PI_HOLES: ceil.append((x, y, ph[2], 1.8))
for (x, y) in BMS_HOLES: ceil.append((x, y, bh[2], 2.0))
shell = shell.cut(fuse([zcyl(r - 0.35, x, y, ZT - W - 0.1, ZT + 0.1) for x, y, z0, r in ceil]))        # R4-4: screws from above into standoffs
# R4-6: bosses under the cover top at the back; M3 from the back through the rear plate
COVER_SCREWS = [-60.0, -25.0, 72.0, 205.0, 235.0]                     # round 9: clear of the Pi hood
def cover_boss(x): return ycyl(4.0, x, 90.0, BW.inner(x) - 6.5, BW.inner(x) - 0.05)          # round 13: OD 8 (1.7 mm wall round the insert), 6.5 deep
def cover_pocket(x): return ycyl(2.0, x, 90.0, BW.inner(x) - 5.0, BW.inner(x) + 0.1)         # M3 heat-set insert: 4.0 x 5.0 (L4 + 1)
shell = shell.fuse(fuse([cover_boss(x) for x in COVER_SCREWS if x > X0B])).cut(fuse([cover_pocket(x) for x in COVER_SCREWS if x > X0B]))
import wire_clips as WC                                                # round 13: wire loops under the cover top (printed with the covers)
shell = shell.fuse(fuse([WC.solid(c) for c in WC.CLIPS]))
STANDOFF_PARTS = [('MOUNT_Pi_ceiling_standoffs_M2.5', fuse([zcyl(2.5, x, y, z0, ZT - W).cut(zcyl(1.05, x, y, z0 - .1, ZT - W + .1)) for x, y, z0, r in ceil if r < 1.9]), 'Pi 4 hangs upside down: 4 x M2.5 female standoffs (3 mm) from its mounting holes to the cover ceiling, screws from above (R4-4).'),
                  ('MOUNT_BMS_ceiling_standoffs_M3', fuse([zcyl(3.0, x, y, z0, ZT - W).cut(zcyl(1.7, x, y, z0 - .1, ZT - W + .1)) for x, y, z0, r in ceil if r >= 1.9]), 'JBD BMS hangs upside down: 4 x M3 female standoffs (2 mm) at its corners to the cover ceiling, screws from above (R4-4).')]

# ------------------------------------------------ E6: pieces with half-lapped seams
outer_half = outer.cut(body(X0B - 1, X1B + 1, 1.5, z0=-1.0))            # outer 1.5 mm of the wall
def piece(xa, xb, lap_left, lap_right):
    s = shell.intersect(box(xa, xb, -200, 50, -2, 120))
    if lap_left:  s = s.cut(outer_half.intersect(box(xa, xa + 6.0, -200, 50, -2, 120)))                # inner half runs 6 mm left under the neighbour
    if lap_right: s = s.fuse(shell.intersect(outer_half).intersect(box(xb, xb + 6.0, -200, 50, -2, 120)))  # outer half runs 6 mm over
    return s.clean()
shell = shell.cut(fuse([ycyl(1.1, x, z, STEP_Y - W - 0.1, STEP_Y - 0.5) for x, z in [(264.5, 37.0), (272.5, 37.0)]]))   # round 13: I/O panel tab pilots
covers = [('V44_PRINT_cover_left_screen', piece(X0B, SEAMS[0], False, True),
           'Upper cover, motor end (X -71..98): screen window with vent ribs (intake), top vent band removed from the Pi zone (no Pi window, E4); stands on the bottom plate, M3 bosses at its foot.'),
          ('V44_PRINT_cover_centre_exit', piece(SEAMS[0], SEAMS[1], True, True),
           'Centre cover (X 98..172): U opening under the square exit frame, so it lifts off without touching the swivel (E2). No back wall: the rear upright is the back here.'),
          ('V44_PRINT_cover_right_grille', piece(SEAMS[1], X1B, True, False),
           'Right cover (X 172..280): small grille over the ODrive, fan exhaust + 4 screws on the back, back step at the battery end with the rear I/O opening.')]
# end caps (plain, E5): same profile with the end face rounded, intake slots on the motor end (E7)
def cap(x0, x1, end):
    o = body(x0, x1, 0.0)
    face = sorted(o.Faces(), key=lambda f: f.Center().x)[0 if end == 'motor' else -1]
    o = o.fillet(3.0, [e for e in face.Edges() if e.Center().z > 0.5])         # round the end face except its bottom edge
    xi = (x0 + W, x1 + 1) if end == 'motor' else (x0 - 1, x1 - W)
    s = o.cut(body(xi[0], xi[1], W, z0=-1.0))
    if end == 'motor':
        s = s.cut(fuse([box(X0E - 1, X0E + W + 1, y, y + 3.0, 12.0, 78.0) for y in np.arange(-122.0, -14.0, 8.0)]))
    s = s.cut(PLATE_ZONE) if end == 'motor' else s                            # the rear plate passes behind the motor-end cap
    # round 13: the caps get fixings too - the motor cap a boss for the M3 from the back (X -75), the battery cap one from below
    for x, y in CAP_BOSSES:
        if x0 < x < x1: s = s.fuse(zcyl(4.0, x, y, 0.0, 10.0).intersect(o)).cut(zcyl(2.0, x, y, -0.1, 5.0))
    return s.clean()
CAP_BOSSES = [(-76.5, -109.0), (-76.5, -28.0), (284.0, 10.0)]              # round 13: end caps, M3 from below (motor cap: clear of the motor's round body and the boards; battery cap: back step)
caps = [('V44_PRINT_end_cap_motor', cap(X0E, X0B, 'motor'), 'Plain motor-end cap (E5) with intake slots (E7); the aluminium handle loop passes outside it.'),
        ('V44_PRINT_end_cap_battery', cap(X1B, X1E, 'battery'), 'Plain battery-end cap (E5), including the back step.')]
io = box(IO['x'][0] + 0.2, IO['x'][1] - 0.2, STEP_Y - W, STEP_Y, IO['z'][0] + 0.2, IO['z'][1] - 0.2)
# round 7: real AMASS XT60E-F (flange 34 x 15.8 x 3 flush in a pocket; body 18.5 x 11 through a 3 mm backing frame, 2 x M2.5 pilots)
XP = dict(x=268.0, z=72.8)
io = io.cut(box(XP['x'] - 8.1, XP['x'] + 8.1, STEP_Y - W - 0.2, STEP_Y + .1, XP['z'] - 17.2, XP['z'] + 17.2))
backing = box(262.2, IO['x'][1] - 0.2, STEP_Y - W - 3.1, STEP_Y - W - 0.1, 55.4, IO['z'][1] - 0.2)   # flange is 3.1 thick
backing = backing.cut(box(XP['x'] - 5.7, XP['x'] + 5.7, STEP_Y - W - 3.1, STEP_Y - W + .1, XP['z'] - 9.45, XP['z'] + 9.45))
backing = backing.cut(fuse([ycyl(1.1, XP['x'], XP['z'] + dz, STEP_Y - W - 3.1, STEP_Y - W + .1) for dz in (-12.49, 12.49)]))
io = io.fuse(backing).cut(ycyl(6.1, 268.0, 47.0, STEP_Y - W - .1, STEP_Y + .1))   # 12 mm latching power switch
# (round 13: the M5 bond-lug hole at X 257 Z 80 is gone - nothing was bonded to it)
# round 13: the panel is held in its opening by two tabs under it, screwed to the step wall
IO_TABS = [(264.5, 37.0), (272.5, 37.0)]                                     # M2.5 x 5 from inside, self-tapping into the wall (pilot 2.2 x 2.5)
for x, z in IO_TABS:
    io = io.fuse(box(x - 2.0, x + 2.0, STEP_Y - W - 2.55, STEP_Y - W, 34.0, IO['z'][0] + 0.4)).cut(ycyl(1.45, x, z, STEP_Y - W - 2.6, STEP_Y - W + .1))
# (no top lip: the step's top inner corner is rounded (r 6) right over the opening and the battery-lead lane / XT60E-F fill the space below it;
#  the top edge sits in the opening with 0.2 mm per side)
NEW = covers + caps + [(n, shp, t) for n, shp, t in STANDOFF_PARTS] + [('V44_PRINT_rear_IO_panel_flush', io, 'Flush rear I/O panel in the back step (E3/D6/D7): XT60E-F charge port flush in a pocket (X 268 Z 72.8, 2 x M2.5 into the backing frame), 12 mm power switch (X 268 Z 47), round 13: held by two screw tabs under it.')]

# plate holes for the boss screws (both variants)
PLATES = {'printed': ['S01_V44_PRINT_bottom_plate_left', 'S01_V44_PRINT_bottom_plate_right'], 'cnc': ['S01_V44_CNC_bottom_plate_6061_5mm']}
report = dict(ceiling_bosses=dict(pi=PI_HOLES, bms=BMS_HOLES), ceil=[[float(x), float(y), float(z0), float(r)] for x, y, z0, r in ceil], cover_screws=COVER_SCREWS, cap_bosses=CAP_BOSSES, io_tabs=IO_TABS, bosses=len(bosses), boss_xy=[[round(float(x), 1), round(float(y), 1)] for x, y in bosses], clashes={}, p2s_fit={})
for mode in ('cnc', 'printed'):
    r = REV[mode]; d = H / mode
    holes = fuse([zcyl(1.7, x, y, -5.1, 0.1) for x, y in bosses + CAP_BOSSES])
    for n in PLATES[mode]:
        s = cq.Shape.importBrep(str(d / (n + '.brep'))).cut(holes)
        s.exportStep(str(d / (n + '.step'))); s.exportBrep(str(d / (n + '.brep')))
    existing = {n: cq.Shape.importBrep(str(d / (n + '.brep'))) for n in r['parts'] if not n.startswith(OWN)}
    eb = {n: bb(s) for n, s in existing.items()}
    clash = []
    for n, s, _ in NEW:
        lo, hi = bb(s)
        for m, t in existing.items():
            l2, h2 = eb[m]
            if (lo - .01 > h2).any() or (l2 - .01 > hi).any(): continue
            v = VC.clash_volume(s, t)
            if abs(v) > 1e-3: clash.append((n, m, round(v, 3)))
    for i, (n, s, _) in enumerate(NEW):
        for m, t, _ in NEW[i + 1:]:
            l1, h1 = bb(s); l2, h2 = bb(t)
            if (l1 - .01 > h2).any() or (l2 - .01 > h1).any(): continue
            v = VC.clash_volume(s, t)
            if abs(v) > 1e-3: clash.append((n, m, round(v, 3)))
    report['clashes'][mode] = clash
    shell_names = [n for n, _, _ in NEW]
    for n, s, note in NEW:
        if n not in r['parts']: r['parts'].append(n)
        standoff = n.startswith('MOUNT_')
        r['meta'][n] = dict(group='mounts' if standoff else 'covers', kind='spacer' if standoff else 'part', note=note[:400],
                            manufacture='Buy: brass hex standoffs' if standoff else 'PRINT PETG-CF / PA-CF', demo_name='', source='build_v44_shell.py')
        r['colors'][n] = [.78, .66, .3] if standoff else ([.21, .22, .24] if 'IO' not in n else [.27, .28, .3])
        s.exportStep(str(d / (n + '.step'))); s.exportBrep(str(d / (n + '.brep')))
        if n not in r['views']['complete']: r['views']['complete'].append(n)
        lo, hi = bb(s); dims = sorted((hi - lo).tolist())
        report['p2s_fit'][n] = dict(size_mm=[round(float(v), 1) for v in hi - lo], fits_p2s=None if standoff else bool(dims[1] <= 256 and dims[2] <= 256))
    r['views']['open'] = [n for n in r['views']['complete'] if n not in shell_names or n.startswith('MOUNT_')]
    r['views']['io_access'] = [n for n in r['views']['complete'] if n != 'V44_PRINT_rear_IO_panel_flush']
    r['status'] = r['status'].replace('Rack clevis, handle and enclosure still to do.', 'Enclosure (E1-E8) on the bottom plate: same for both variants.')
    (d / 'revision.json').write_text(json.dumps(r, indent=1))
ext = outer.fuse(body(X0E, X0B, 0.0)).fuse(body(X1B, X1E, 0.0))
report['volume'] = dict(shell_outer_L=round(ext.Volume() / 1e6, 3), height_print_mm=round(ZT + 11.0, 1), height_cnc_mm=round(ZT + 5.0, 1),
                        note='Outer volume of the covers + caps above the plate. Add the plate (and the ladder on PRINT) for the full envelope.')
(H / 'shell-report.json').write_text(json.dumps(report, indent=1))
print(json.dumps({k: v for k, v in report.items() if k != 'boss_xy'}, indent=1))
