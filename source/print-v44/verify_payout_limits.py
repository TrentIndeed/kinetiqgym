"""Payout range vs the carrier's movement limiters (R14-5). Writes payout-limits.json.

1. Rope: the winding law of the module-10 audit (rope tangent from the drum to the sheave, carrier geared 1/53 to the drum):
   carrier angle <-> rope station on the drum, tracked zone between the 3 hand-wound dead wraps and the far flange.
2. Stops in CAD: the carrier, sheave and both axles turn about the 6809 pivot through the whole range and past the stops;
   every part that does not turn with them is checked for overlap (the worm mesh and the 6809 race are skipped).
3. ODrive: drum = motor (direct coupler), so the payout soft limit in motor turns.
"""
from pathlib import Path
import json, math, sys
import numpy as np
import cadquery as cq

H = Path(__file__).resolve().parent; R = H.parent
src = (R / 'stock-drive-study/audit_fairlead_module10.py').read_text(encoding='utf-8')
g = {'__file__': str(R / 'stock-drive-study/audit_fairlead_module10.py')}
exec(src[:src.index('FIXED = [')], g)                                     # winding-law part of the audit only
a_lo, a_hi, wl = g['winding_law'](); station, RATIO, DR, WIDTH, ROPE = g['station'], g['RATIO'], g['DR'], g['WIDTH'], g['ROPE']
DEAD = 3; WRAP_MM = 2 * math.pi * DR
STOP, PIVOT = 48.4, (135.2, 40.0)
turns_full = (a_hi - a_lo) * RATIO / 360
rope = dict(winding=dict((k, (v.tolist() if hasattr(v, 'tolist') else v)) for k, v in wl.items()),
            tracked_zone_x=[round(WIDTH[0], 2), round(WIDTH[1], 2)], dead_wraps=DEAD, dead_wrap_rope_mm=round(DEAD * WRAP_MM),
            carrier_full_wind_deg=round(a_hi, 2), carrier_full_payout_deg=round(a_lo, 2), stop_deg=STOP,
            drum_turns_full_range=round(turns_full, 2), stop_margin_turns=round((STOP - abs(a_lo)) * RATIO / 360, 3),
            stop_margin_rope_mm=round((STOP - abs(a_lo)) * RATIO / 360 * WRAP_MM, 1),
            station_at_stop_x=[round(station(-STOP), 2), round(station(STOP), 2)],
            dead_wraps_left_at_stop=round(DEAD - (WIDTH[0] - station(-STOP)) / 3.3, 2) if station(-STOP) < WIDTH[0] else DEAD)

# ---- 2. CAD sweep of the carrier set
REV = json.loads((H / 'printed/revision.json').read_text())
MOV = ('FM10_Printed_PA-CF_carrier', 'FM10_Top_sheave', 'FM10_sheave_axle', 'FM10_roller_axle', 'Bearing_625ZZ_roller')   # turn with the carrier (module 10 'moving')
SKIP = ('KHK_SW0.8-R1_worm', 'SKF_61809', 'WIRE_', 'HARNESS_', 'RESERVE', 'ROUTE', 'TRIAL_DSI')
load = lambda n: cq.Shape.importBrep(str(H / 'printed' / (n + '.brep')))
mov = {n: load(n) for n in REV['parts'] if n.startswith(MOV)}
mb = [s.BoundingBox() for s in mov.values()]
rmax = max(math.hypot(x - PIVOT[0], z - PIVOT[1]) for b in mb for x in (b.xmin, b.xmax) for z in (b.zmin, b.zmax)) + 1
y0, y1 = min(b.ymin for b in mb) - 1, max(b.ymax for b in mb) + 1
env = cq.Solid.makeCylinder(rmax, y1 - y0, cq.Vector(PIVOT[0], y0, PIVOT[1]), cq.Vector(0, 1, 0))
eb = env.BoundingBox(); stat = {}
for n in REV['parts']:
    if n in mov or n.startswith(SKIP) or n.startswith('F44_') and 'exit' not in n and 'block' not in n: continue
    s = load(n); b = s.BoundingBox()
    if b.xmin > eb.xmax or b.xmax < eb.xmin or b.ymin > eb.ymax or b.ymax < eb.ymin or b.zmin > eb.zmax or b.zmax < eb.zmin: continue
    try:
        if s.intersect(env).Volume() > 1e-3: stat[n] = s
    except Exception: stat[n] = s
def turned(s, a):                                                         # carrier angle a: bottom toward +X
    return s.rotate(cq.Vector(PIVOT[0], 0, PIVOT[1]), cq.Vector(PIVOT[0], 1, PIVOT[1]), -a)
ANG = sorted({0.0, round(a_hi, 2), round(a_lo, 2), 47.0, -47.0, 48.0, -48.0, 48.4, -48.4, 48.8, -48.8, 50.0, -50.0} |
             {float(a) for a in range(-45, 46, 5)})
sweep = []
for a in ANG:
    hits = []
    for mn, ms in mov.items():
        t = turned(ms, a); tb = t.BoundingBox()
        for sn, ss in stat.items():
            sb = ss.BoundingBox()
            if sb.xmin > tb.xmax or sb.xmax < tb.xmin or sb.ymin > tb.ymax or sb.ymax < tb.ymin or sb.zmin > tb.zmax or sb.zmax < tb.zmin: continue
            try: v = t.intersect(ss).Volume()
            except Exception: v = -1
            if abs(v) > 0.01: hits.append(dict(moving=mn[:40], static=sn, mm3=round(v, 3)))
    sweep.append(dict(deg=a, contacts=hits)); print(f'{a:7.2f} deg: ' + ('clear' if not hits else '; '.join(f"{h['moving'][:18]} x {h['static'][:40]} {h['mm3']}" for h in hits)), flush=True)
clear_to = min(abs(s['deg']) for s in sweep if s['contacts']) if any(s['contacts'] for s in sweep) else None

# ---- 3. ODrive soft limits (drum on the motor shaft through the coupler: 1 motor turn = 1 drum turn)
odrive = dict(home='fully wound (carrier +%.2f deg): pull the rope in until the handle stops at the exit, set position 0' % a_hi,
              payout_limit_turns=round(turns_full, 2), stop_contact_turns=round(turns_full + rope['stop_margin_turns'], 2),
              rope_per_turn_mm=round(WRAP_MM, 1),
              recommended=dict(pos_min=0.0, pos_max=round(turns_full - 0.1, 2), note='0.1 turn (16 mm) before the dead wraps; the blocks are '
                               'a further 0.45 turn out and must never be reached under power (the worm locks the drum through the gears).'))
rep = dict(rope=rope, sweep=sweep, static_checked=sorted(stat), first_contact_deg=clear_to, odrive=odrive)
(H / 'payout-limits.json').write_text(json.dumps(rep, indent=1))
print(json.dumps(dict(rope=rope, first_contact_deg=clear_to, odrive=odrive), indent=1))
