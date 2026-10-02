"""Put fairlead module rev 10 (gear train on the free right end of the drum shaft) into the packing demo.

The rev 6-9 drum 60T sat inside the Ruland motor coupler. Rev 10 retires (never deletes) the rev 9
module parts, the FM6 drum 60T and hub, and the old 2GT drum pulley with its set screws, then adds
the rev 10 module parts plus the drum 60T and hub in the old pulley slot. New parts carry
addedIn='fairlead-module-10' (whitelisted in editor.js). Run after publish_fairlead_module9_packing.py.
"""
from pathlib import Path
import gzip, json

R = Path(__file__).resolve().parent.parent
PUB = R / 'workbench/public/stock-battery-fit'
MOD = json.loads(gzip.decompress((R / 'workbench/public/stock-drive-study/voltra-module10-model.json.gz').read_bytes()))
TAG = 'fairlead-module-10'
EXTERNAL = ('Square back plate', 'Square exit frame', 'Square exit bezel', 'Exit frame spacer', '6809-2RS', 'Printed PA-CF carrier', 'Roller 625ZZ', 'roller axle', '6808_sealed_bearing', 'Carrier_M3',
            'Fixed_bearing_housing', 'Front_outer_race', 'Rear_mount_plate', 'Hub_retainer', 'Rear_inner_race', 'Owned_exit_625', 'JY_MARINE',
            'Oval_clamp', 'Printed_oval', 'Stock_M5_spacer', 'ISO7379_5x25_M4_shoulder', 'Axle_M4', 'Exit_pulley', 'Exit_axle')
OLD_PULLEY = ('V14_PRINT_2GT_drum', 'I_V14_pulley_drum_1', 'I_V14_pulley_drum_2')


def patch(path):
    d = json.loads(gzip.decompress(path.read_bytes()))
    parts = [p for p in d['parts'] if p.get('addedIn') != TAG]          # idempotent re-run
    by = {p['name']: p for p in parts}
    retired = 0
    for p in parts:
        n = p['name']
        if ((p.get('addedIn') == 'fairlead-module-9' and n.startswith('FM9 ') and n != 'FM9 Drum V8 widened 6 mm')
                or n.startswith(('FM6 Drum input gear', 'FM6 Drum hub')) or n in OLD_PULLEY):
            if not p.get('retired'):
                p['retired'] = True; p['retired_by'] = TAG; retired += 1
    new = []
    for r in MOD['parts']:
        n = r['name']
        if n.startswith(('Drum input gear', 'Drum hub')):
            old = by['FM6 ' + n] if 'FM6 ' + n in by else None
            new.append(dict(name='FM10 ' + n, assembly='drivetrain', group='drivetrain', color=(old or r)['color'],
                            bounds=[round(b, 4) for b in r['bounds']], vertices=r['vertices'], triangles=r['triangles'],
                            description='Owned drum 60T / hub moved to the right end of the drum shaft (old 2GT pulley slot); it sat inside the motor coupler before.',
                            model_status='Fairlead module rev 10 — mechanism review, not a release', kind='proposal', addedIn=TAG))
            continue
        if r['group'] == 'context' or n.startswith('Drum'):
            continue
        ext = any(k in n for k in EXTERNAL)
        extra = dict(front_wall_offset=0.0) if n.startswith('Square back plate') else {}      # R4-1: the plate front is the enclosure face
        new.append(dict(**extra, name='FM10 ' + n, assembly='drivetrain', group='external' if ext else 'drivetrain', color=r['color'],
                        bounds=[round(b, 4) for b in r['bounds']], vertices=r['vertices'], triangles=r['triangles'],
                        description=r.get('role') or '', model_status='Fairlead module rev 10 — mechanism review, not a release', kind='proposal', addedIn=TAG))
    parts.extend(new)
    d['parts'] = parts
    if isinstance(d.get('notes'), list):
        d['notes'] = [n for n in d['notes'] if TAG not in str(n)] + [f'{TAG}: drum 60T moved out of the Ruland motor coupler to the right shaft end (old 2GT pulley retired); shaft 2 and the 20T pair moved right of the fairlead frame on two printed base pedestals. Rev 9 module parts retired.']
    d['fairlead_update'] = dict(revision=TAG, source='real-fairlead-revision/voltra-module10', front_plate='FM10 Square back plate (4-screw enclosure mount)', plate_standoff_mm=7.5)
    path.write_bytes(gzip.compress(json.dumps(d, separators=(',', ':')).encode(), mtime=0))
    return retired, len(new), len(parts)


for variant in ('tp2700', 'tp3850'):
    print(variant, dict(zip(('retired', 'added', 'total'), patch(PUB / f'editor-model-{variant}.json.gz'))))
