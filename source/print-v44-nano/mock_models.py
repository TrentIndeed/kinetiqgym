"""V44 phase 1c: realistic mock models for parts with no vendor CAD, and allowances out of the visible model.

Run after swap_real_cad.py.
- Thunder Power TP2700-5SR70 modules: pouch pack mock (rounded shrink-wrapped block, label panel, end caps) inside the
  maker's 129 x 39 x 33 mm envelope. No vendor CAD exists.
- JBD SP17S005 BMS: board mock from the JBD spec outline (102 x 65 x 12): PCB, aluminium heat bar over the MOSFET row,
  balance / NTC headers, B- / P- power pads, capacitors.
- Wiring and service allowances (RESERVE_*, ROUTE_*, DSI ribbon, Pi port space, fuse-lead space) leave the visible
  model; they are kept as STEP in allowances/ and listed in revision.json['allowances'] for clash checks.
"""
from pathlib import Path
import json, csv, shutil
import numpy as np
import cadquery as cq

HERE = Path(__file__).resolve().parent
REV = {m: json.loads((HERE / m / 'revision.json').read_text()) for m in ('cnc', 'printed')}
def cur(n): return cq.Shape.importBrep(str(HERE / 'printed' / (n + '.brep')))
def bb(s): b = s.BoundingBox(); return np.array([b.xmin, b.ymin, b.zmin]), np.array([b.xmax, b.ymax, b.zmax])
def box(lo, hi): return cq.Solid.makeBox(*(np.array(hi) - np.array(lo)), cq.Vector(*lo))

new = []   # (old, name, shape, group, kind, note, colour)

def lipo(old, name):
    lo, hi = bb(cur(old)); L = hi - lo
    body = cq.Workplane('XY').box(*L).edges('|Y').fillet(3.0).edges('#Y').fillet(1.2).translate(tuple((lo + hi) / 2)).val()
    c = (lo + hi) / 2
    label = cq.Workplane('XY').box(L[0] - 8, L[1] - 30, 0.4).translate((c[0], c[1], hi[2] - 0.2)).val()    # printed label, flush
    body = body.cut(label)
    caps = []
    for y0 in (lo[1], hi[1] - 6):                                                                          # shrink-wrap end caps
        caps.append(cq.Workplane('XY').box(L[0] + 0.01, 6, L[2] + 0.01).edges('|Y').fillet(3.0).translate((c[0], y0 + 3, c[2])).val().cut(
            cq.Workplane('XY').box(L[0] - 1.6, 6.2, L[2] - 1.6).translate((c[0], y0 + 3, c[2])).val()))
    shp = cq.Compound.makeCompound([body, *caps])
    new.append((old, name, shp, 'power', 'electronics_reference',
                'Thunder Power TP2700-5SR70 5S LiPo, appearance mock inside the maker envelope 129 x 39 x 33 mm (no vendor CAD published). '
                'Lead exit not modelled: the pack end faces sit 0.5 mm from the front wall and against the rear spacer; lead and balance-lead exit space is still to allocate.',
                [.08, .1, .16]))

lipo('CATALOG_stock-battery-fit', 'ThunderPower_TP2700-5SR70_module_A_mock')
lipo('CATALOG_TP_module_B', 'ThunderPower_TP2700-5SR70_module_B_mock')

# JBD SP17S005 BMS mock inside its envelope (the long side runs along Y)
old = 'RESERVE_RS50_BMS'; lo, hi = bb(cur(old)); c = (lo + hi) / 2
pcb = box(lo + [0.25, 0.25, 0.0], [hi[0] - 0.25, hi[1] - 0.25, lo[2] + 1.6])
heat = box([lo[0] + 4, lo[1] + 8, lo[2] + 1.6], [lo[0] + 22, hi[1] - 8, lo[2] + 8.5])                    # aluminium bar over the MOSFET row
fins = [box([lo[0] + 4 + k * 3.6, lo[1] + 8, lo[2] + 8.5], [lo[0] + 5.6 + k * 3.6, hi[1] - 8, lo[2] + 11.5]) for k in range(5)]
fets = [box([lo[0] + 24, lo[1] + 10 + k * 8.5, lo[2] + 1.6], [lo[0] + 30, lo[1] + 16 + k * 8.5, lo[2] + 3.8]) for k in range(9)]
bal = box([hi[0] - 10, c[1] - 22, lo[2] + 1.6], [hi[0] - 3, c[1] + 10, lo[2] + 8.6])                       # 10S balance header
ntc = [box([hi[0] - 10, c[1] + 14 + k * 8, lo[2] + 1.6], [hi[0] - 4, c[1] + 20 + k * 8, lo[2] + 7.6]) for k in range(2)]
pads = [box([lo[0] + 34, y, lo[2] + 1.6], [lo[0] + 46, y + 12, lo[2] + 3.6]) for y in (lo[1] + 3, hi[1] - 15)]   # B- / P- copper pads
caps = [cq.Solid.makeCylinder(3, 7, cq.Vector(lo[0] + 52 + k * 8, c[1] + 20, lo[2] + 1.6)) for k in range(2)]
uart = box([hi[0] - 12, lo[1] + 4, lo[2] + 1.6], [hi[0] - 3, lo[1] + 14, lo[2] + 6.6])
bms = cq.Compound.makeCompound([pcb, heat, *fins, *fets, bal, *ntc, *pads, *caps, uart])
bms = bms.mirror('XY', cq.Vector(0, 0, c[2]))                                     # R4-3: hangs upside down from the cover ceiling
new.append((old, 'JBD_SP17S005_BMS_mock_from_spec', bms, 'power', 'electronics_reference',
            'JBD / LLT SP17S005 10S Li-ion 60 A BMS, appearance mock from the JBD spec outline (102 x 65 x 12; no vendor CAD). Heat bar, MOSFET row, balance/NTC/UART headers and B-/P- pads are illustrative positions.',
            [.12, .35, .2]))

ALLOW = lambda n, m: (n.startswith(('RESERVE', 'ROUTE', 'TRIAL_DSI_service', 'TRIAL_Pi_port_allowance'))) and n not in ('RESERVE_RS50_BMS',)

for mode in ('cnc', 'printed'):
    r = REV[mode]; d = HERE / mode; (HERE / 'allowances').mkdir(exist_ok=True)
    for old, name, shp, group, kind, note, col in new:
        i = r['parts'].index(old); r['parts'][i] = name; dm = r['meta'].pop(old); r['colors'].pop(old, None)
        for v in r['views'].values():
            if old in v: v[v.index(old)] = name
        for ext in ('.step', '.brep'): (d / (old + ext)).unlink(missing_ok=True)
        r['meta'][name] = dict(group=group, kind=kind, note=note, manufacture='Buy', demo_name=dm.get('demo_name', ''), source='appearance mock (mock_models.py)', replaced=old)
        r['colors'][name] = col
        shp.exportStep(str(d / (name + '.step'))); shp.exportBrep(str(d / (name + '.brep')))
    def copy_retry(src, dst):
        """Windows can hold an allowance file open (viewer server, preview): retry, and skip if the copy is already identical."""
        import time
        for i in range(5):
            try: shutil.copy2(src, dst); return
            except OSError:
                if dst.exists() and dst.read_bytes() == src.read_bytes(): return
                time.sleep(1.0)
        shutil.copy2(src, dst)
    allow = [n for n in r['parts'] if ALLOW(n, r['meta'][n])]
    r['allowances'] = [dict(name=n, note=r['meta'][n]['note'][:200], demo_name=r['meta'][n].get('demo_name', '')) for n in allow]
    for n in allow:
        if mode == 'printed':
            for ext in ('.step', '.brep'): copy_retry(d / (n + ext), HERE / 'allowances' / (n + ext))
        for ext in ('.step', '.brep'): (d / (n + ext)).unlink(missing_ok=True)
        r['parts'].remove(n); r['meta'].pop(n); r['colors'].pop(n, None)
        for v in r['views'].values():
            if n in v: v.remove(n)
    if mode == 'printed':                                     # round 9: drop allowance files of retired page parts
        for f in (HERE / 'allowances').glob('*.*'):
            if f.stem not in allow and f.suffix in ('.step', '.brep'): f.unlink(missing_ok=True)
    r['hardware'] = [h for h in r['hardware'] if h['part'] in r['parts']]
    r['status'] = ('V44 phase 1d engineering preview: live-demo layout (design layout rev 12, 176 mm drum shaft, 5.87 L) as real CAD - vendor STEPs, '
                   'appearance mocks for the battery and BMS, allowances kept separately. New base, enclosure and rack puck not built yet.')
    (d / 'revision.json').write_text(json.dumps(r, indent=1))
    with open(d / 'hardware.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['part', 'group', 'kind', 'size', 'source', 'note']); w.writeheader(); w.writerows(r['hardware'])
print('mocks', [n for _, n, *_ in new], '| allowances moved out:', len(allow), '| parts now', len(REV['printed']['parts']))
