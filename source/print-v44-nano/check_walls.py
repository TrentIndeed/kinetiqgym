"""Round 9: every internal part and wiring space against the enclosure walls (printed bottom-plate pieces with the rear plate,
covers, end caps, rear I/O panel). The structure/shell reports check the new walls against parts only; this also checks the
wiring / plug allowances, which live in allowances/. Uses the clash cache. Writes wall-check.json."""
from pathlib import Path
import json
import cadquery as cq
import v44cache as VC

H = Path(__file__).resolve().parent
r = json.loads((H / 'printed' / 'revision.json').read_text())
WALLS = [n for n in r['parts'] if n.startswith(('S01_V44_PRINT_bottom_plate', 'V44_PRINT_cover_', 'V44_PRINT_end_cap_', 'V44_PRINT_rear_IO'))]
SKIP = ('S01_', 'S17_', 'R07_', 'V44_PRINT_', 'MOUNT_Pi_ceiling', 'MOUNT_BMS_ceiling', 'F44_')   # round 13: screws pass through the walls by design (checked in build_v44_fasteners.py)
# parts that sit on / in the walls by design (fused into the printed plate, screwed through it, or seated in a panel pocket)
DESIGNED = ('FM10_Shaft_2_bearing_pedestal', 'MOUNT_fuse_holder_saddles', 'MOUNT_battery_saddle', 'V43_B_', 'V43_W_', 'V43_N_',
            'AMASS_XT60E-F', 'MOUNT_front_board_plate', 'MOUNT_screen_rear_retaining_frame', 'MOUNT_ODrive_Pro_bracket',
            'FM10_Square_back_plate', 'goBILDA_1611', 'TRIAL_Waveshare', 'TRIAL_portrait_bezel',
            'ThunderPower_', 'HARNESS_12mm_latching_power_switch')   # the switch nut clamps the rear I/O panel   # battery modules sit in the saddles fused into the plate (face contact)
import wire_clips as WC
LOOPS = [WC.solid(c) for c in WC.CLIPS]
walls = {n: cq.Shape.importBrep(str(H / 'printed' / (n + '.brep'))) for n in WALLS}
wb = {n: s.BoundingBox() for n, s in walls.items()}
items = {n: H / 'printed' / (n + '.brep') for n in r['parts'] if not n.startswith(SKIP)}
items.update({a['name']: H / 'allowances' / (a['name'] + '.brep') for a in r.get('allowances', [])})   # listed allowances only (no retired files)
hits = []
for n, f in sorted(items.items()):
    s = cq.Shape.importBrep(str(f)); b = s.BoundingBox()
    for w, t in walls.items():
        c = wb[w]
        if b.xmin > c.xmax or b.xmax < c.xmin or b.ymin > c.ymax or b.ymax < c.ymin or b.zmin > c.zmax or b.zmax < c.zmin: continue
        v = VC.clash_volume(s, t)
        if abs(v) > 0.01 and n.startswith(('ROUTE_', 'RESERVE_')) and w.startswith('V44_PRINT_cover_'):
            for c in LOOPS:                                                       # round 13: the wire loops (part of the cover) hang inside the lanes by design
                ct = c.intersect(t)
                if ct.Volume() > 1e-6: v -= s.intersect(ct).Volume()
        if abs(v) > 0.01: hits.append(dict(part=n, wall=w, mm3=round(v, 2), designed=n.startswith(DESIGNED)))
(H / 'wall-check.json').write_text(json.dumps(hits, indent=1))
bad = [h for h in hits if not h['designed']]
print('wall check:', len(items), 'items;', len(bad), 'unexpected intrusions')
for h in bad: print('  ', h['part'][:60], '->', h['wall'], h['mm3'], 'mm3')
