"""V44 print package: every printed part of the printed build as STL (and STEP) in print-files/, with an index
(material, size, fits the Bambu P2S 256 mm bed, inserts to press). Run after build_v44_fasteners.py (holes are final then).
Parts are exported in the assembly frame; orient them in the slicer (the index gives the suggested face down)."""
from pathlib import Path
import json, re, collections
import cadquery as cq

H = Path(__file__).resolve().parent
SRC = H / 'printed'; OUT = H / 'print-files'; OUT.mkdir(exist_ok=True)
r = json.loads((SRC / 'revision.json').read_text())
BED = r.get('printer', {}).get('build_volume_mm', [256, 256, 256])

FAIRLEAD_PRINTED = ('FM10_Fixed_bearing_housing', 'FM10_Front_outer_race_retainer_1mm', 'FM10_Rear_inner_race_retainer_2mm',
                    'FM10_Square_back_plate_4-screw_enclosure_mount')
STANDOFFS = ('MOUNT_Teensy_perfboard_standoffs', 'MOUNT_CAN_board_perfboard_standoffs', 'MOUNT_regulator_perfboard_standoffs')
FACE = {'S01_V44_PRINT_bottom_plate': 'underside down', 'V44_PRINT_cover': 'top down (wire loops bridge, no supports)',
        'V44_PRINT_end_cap': 'outer face down', 'V44_PRINT_rear_IO_panel': 'outer face down', 'FM10_Printed_PA-CF_carrier': 'ring face down, supports under the fork',
        'MOUNT_front_board_plate': 'back face down', 'FM10_Square_back_plate': 'back face down (6809 seat up)'}

def material(n, m):
    t = m.get('manufacture', '')
    if 'PRINT' in t.upper() or 'print' in t: return re.sub(r'(?i)print(ed)?', '', t).strip(' /') or 'PA-CF'
    if n.startswith('FM10_'): return 'PA-CF'
    return 'PETG'

def printed(n, m):
    if n.startswith(('F44_', 'WIRE_', 'HARNESS_', 'TRIAL_')): return False
    t = m.get('manufacture', '')
    return 'PRINT' in t.upper() or n in FAIRLEAD_PRINTED or n in STANDOFFS or n.startswith('FM10_Printed')

inserts = collections.Counter()
for h in r['hardware']:
    mm = r['meta'].get(h['part'], {})
    if h['kind'] == 'insert' and mm.get('host'): inserts[(mm['host'], h['size'].split()[0])] += 1

rows = []
for n in r['parts']:
    m = r['meta'][n]
    if not printed(n, m): continue
    s = cq.Shape.importBrep(str(SRC / (n + '.brep')))
    for k, sol in enumerate(s.Solids() if n in STANDOFFS else [s]):
        name = n if n not in STANDOFFS else f'{n}_{k}'
        if n in STANDOFFS and k: continue                                      # identical standoffs: one file, qty = count
        cq.exporters.export(cq.Workplane().add(sol), str(OUT / (name + '.stl')), tolerance=0.03, angularTolerance=0.1)
        # STEP copies: see ../printed/<part>.step (same geometry)
        b = sol.BoundingBox(); dims = sorted([b.xlen, b.ylen, b.zlen], reverse=True)
        fits = all(d <= bd for d, bd in zip(dims, sorted(BED, reverse=True)))
        ins = ', '.join(f'{c} x {sz}' for (hn, sz), c in sorted(inserts.items()) if hn == n)
        face = next((v for k_, v in FACE.items() if n.startswith(k_)), '')
        rows.append(dict(file=name + '.stl', qty=len(s.Solids()) if n in STANDOFFS else 1, material=material(n, m),
                         size=' x '.join(f'{d:.0f}' for d in dims), fits=fits, volume_cm3=round(sol.Volume() / 1000, 1), inserts=ins, face=face))

L = ['# V44 print files (printed build)', '',
     f'{len(rows)} files, exported from `print-v44-nano/printed/` with every hole cut to its final size (inserts, clearance, pilots).',
     'Print `../fit-coupons/` first in the same material and tune the hole sizes if needed. Sizes in mm (longest first);',
     f"bed: {r.get('printer', {}).get('model', '')} {BED[0]} mm. Parts are in the assembly frame: orient them in the slicer.", '',
     '| File | Qty | Material | Size | Fits bed | Volume cm³ | Heat-set inserts | Face down |', '|---|---:|---|---|---|---:|---|---|']
for x in rows:
    L.append(f"| {x['file']} | {x['qty']} | {x['material']} | {x['size']} | {'yes' if x['fits'] else '**no**'} | {x['volume_cm3']} | {x['inserts'] or '-'} | {x['face'] or '-'} |")
L += ['', f"Total volume ≈ {sum(x['volume_cm3'] * x['qty'] for x in rows):.0f} cm³ (solid; real use depends on infill).", '']
(OUT / 'README.md').write_text('\n'.join(L), encoding='utf-8')
print('\n'.join(L))
