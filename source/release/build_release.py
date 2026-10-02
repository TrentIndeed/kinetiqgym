"""Build the public Dragon Gym release folder from this private workspace (allowlist only; no history; no supplier CAD).

usage: python build_release.py <out_dir> [--version 0.1.0] [--skip-freecad] [--scan-only]

Steps: docs + licences -> per variant: stage (supplier parts -> same-size placeholders) -> STEP (parts + assembly) -> FreeCAD
(our parts reuse the history files already built; placeholders and the assembly are built) -> drivetrain motion study ->
STL + fit coupons -> DXF profiles of flat parts -> BOM / wire list / fastener tables / vendor fetch list -> source scripts ->
secret and personal-data scan (the build fails if anything is found).
"""
from pathlib import Path
import json, os, re, shutil, subprocess, sys, hashlib, csv
import cadquery as cq

HERE = Path(__file__).resolve().parent; R = HERE.parent; M = R / 'print-v44-nano'
OUT = Path(sys.argv[1]).resolve(); ARGS = sys.argv[2:]
VERSION = ARGS[ARGS.index('--version') + 1] if '--version' in ARGS else '0.1.0'
FC_BIN = os.environ.get('FREECAD_BIN', r'D:/Programs/FreeCAD_1.1.4-Windows-x86_64-py311/bin')
VARIANTS = ('printed', 'cnc')

# ------------------------------------------------------------------ supplier parts: placeholder + where to get the CAD
VENDOR = [  # (name regex, supplier, part, where)
    (r'^V3_ODrive_|^B_V3_ODrive_PCB_supplier', 'ODrive Robotics', 'ODrive Pro + heat spreader', 'docs.odriverobotics.com (ODrive Pro datasheet: CAD)'),
    (r'^H_V21_goBILDA_1301|^FM10_Drum_hub_1301', 'goBILDA', '1301-0016-0012 12 mm round-bore hub', 'gobilda.com, SKU 1301-0016-0012 (STEP on the product page)'),
    (r'2302-0014-0060', 'goBILDA', '2302-0014-0060 60T MOD 0.8 gear', 'gobilda.com, SKU 2302-0014-0060'),
    (r'FM10_goBILDA_2303-4008', 'goBILDA', '2303-4008-0020 20T pinion, 8 mm REX', 'gobilda.com, SKU 2303-4008-0020'),
    (r'FM10_goBILDA_2303-1006', 'goBILDA', '2303-1006-0020 20T pinion, 6 mm D-bore', 'gobilda.com, SKU 2303-1006-0020'),
    (r'^goBILDA_1601', 'goBILDA', '1601-0014-0006 flanged bearing 6 x 14 x 5', 'gobilda.com, SKU 1601-0014-0006'),
    (r'^goBILDA_1611', 'goBILDA', '1611-0514-4008 flanged bearing 8 mm REX', 'gobilda.com, SKU 1611-0514-4008'),
    (r'^goBILDA_2106', 'goBILDA', '2106-4008-0560 REX shaft 56 mm', 'gobilda.com, SKU 2106-4008-0560'),
    (r'^ServoCity_2101', 'ServoCity', '2101-0006-0060 6 mm D-shaft 60 mm', 'servocity.com, SKU 2101-0006-0060'),
    (r'^SKF_6001', 'SKF', '6001-2RSH bearing', 'skf.com (product page, CAD download)'),
    (r'^SKF_61809', 'SKF', '61809-2RS1 (6809) bearing', 'skf.com'),
    (r'^SKF_61808', 'SKF', '61808-2RS1 (6808) bearing', 'skf.com'),
    (r'^Bearing_625ZZ', 'generic', '625ZZ bearing 5 x 16 x 5', 'any bearing supplier CAD (e.g. skf.com 625-2Z)'),
    (r'^KHK_SW0', 'KHK Gears', 'SW0.8-R1 worm', 'khkgears.net / catalog.khkgears.us (CAD download)'),
    (r'^NBK_MSTS', 'NBK', 'MSTS-25-10-12 slit coupling', 'nbk1560.com (CAD download)'),
    (r'^SameSky_TB005', 'Same Sky (CUI)', 'TB005-762-05BE terminal block', 'sameskydevices.com'),
    (r'^Littelfuse_04980921', 'Littelfuse', '04980921GXM5 MIDI fuse holder', 'littelfuse.com'),
    (r'^Littelfuse_BF1', 'Littelfuse', 'BF1 142.5631.5402 40 A fuse', 'littelfuse.com'),
    (r'^AMASS_XT60', 'AMASS', 'XT60E-F panel socket', 'manufacturer CAD (search XT60E-F STEP)'),
    (r'^TRIAL_Pi4', 'Raspberry Pi', 'Raspberry Pi 4 Model B', 'raspberrypi.com (mechanical drawing) or the FreeCAD parts library'),
    (r'^TRIAL_Waveshare', 'Waveshare', '4 inch DPI LCD (C)', 'waveshare.com wiki (3D drawing)'),
    (r'^TRIAL_CAN_headers', 'Waveshare', 'SN65HVD230 CAN board (on its perfboard)', 'waveshare.com wiki'),
    (r'^TRIAL_Pololu5571', 'Pololu', 'D42V55F5 regulator #5571 (on its perfboard)', 'pololu.com/product/5571 (3D model)'),
    (r'^TRIAL_Teensy', 'PJRC', 'Teensy 4.0 (on its perfboard, socket headers)', 'pjrc.com / KiCad Teensy library'),
    (r'^TRIAL_driver_fan', 'Noctua', 'NF-A4x10 5V fan', 'noctua.at (CAD data)'),
]
def vendor_of(n):
    for rx, sup, part, where in VENDOR:
        if re.search(rx, n): return dict(supplier=sup, part=part, where=where)

def placeholder(shape):
    """Same-size envelope: a cylinder when two sides of the box are equal (round parts), else a box."""
    b = shape.BoundingBox(); d = [b.xlen, b.ylen, b.zlen]; c = cq.Vector((b.xmin + b.xmax) / 2, (b.ymin + b.ymax) / 2, (b.zmin + b.zmax) / 2)
    for ax in range(3):
        o = [i for i in range(3) if i != ax]
        if abs(d[o[0]] - d[o[1]]) < 0.3 and d[o[0]] > 3:
            v = [0, 0, 0]; v[ax] = 1; base = [c.x, c.y, c.z]; base[ax] -= d[ax] / 2
            return cq.Solid.makeCylinder(d[o[0]] / 2, max(d[ax], 0.2), cq.Vector(*base), cq.Vector(*v))
    return cq.Solid.makeBox(max(d[0], .2), max(d[1], .2), max(d[2], .2), cq.Vector(b.xmin, b.ymin, b.zmin))

def run(cmd, env=None, **k):
    e = dict(os.environ, **(env or {})); print('$', ' '.join(map(str, cmd))[:160], flush=True)
    return subprocess.run(list(map(str, cmd)), env=e, check=True, **k)

# ------------------------------------------------------------------ docs
def docs(stats):
    (OUT / 'docs').mkdir(parents=True, exist_ok=True)
    src = HERE / 'docs_src'
    for f in ('SAFETY.md', 'LICENSE.md', 'CONTRIBUTING.md'): shutil.copyfile(src / f, OUT / f)
    for f in ('firmware-setup.md', 'modifying.md', 'printing.md'): shutil.copyfile(src / f, OUT / 'docs' / f)
    t = (src / 'README.md').read_text(encoding='utf-8')
    for k, v in dict(VERSION=VERSION, HERO=stats.get('hero', 'images/hero.png'), N_PRINTED=stats['n_printed'], N_HW=stats['n_hw'], N_BUY=stats['n_buy']).items():
        t = t.replace('{{%s}}' % k, str(v))
    (OUT / 'README.md').write_text(t, encoding='utf-8')
    (OUT / 'docs' / 'build.md').write_text((src / 'build.md').read_text(encoding='utf-8').replace('{{FASTENERS}}', fastener_table()), encoding='utf-8')
    (OUT / 'docs' / 'wiring.md').write_text((src / 'wiring.md').read_text(encoding='utf-8').replace('{{WIRE_TABLE}}', wire_table()), encoding='utf-8')
    (OUT / 'bom').mkdir(exist_ok=True)
    hw = (M / 'hardware-summary.md').read_text(encoding='utf-8').split('\n', 2)[2]
    (OUT / 'bom' / 'BOM.md').write_text((src / 'BOM.md').read_text(encoding='utf-8').replace('{{HARDWARE}}', hw), encoding='utf-8')
    for v in VARIANTS: shutil.copyfile(M / v / 'hardware.csv', OUT / 'bom' / f'hardware_{v}.csv')

def wire_table():
    r = json.loads((M / 'printed' / 'revision.json').read_text())
    rows = ['| Wire | Gauge | Route / ends | Length |', '|---|---|---|---|']
    for n in r['parts']:
        if not n.startswith('WIRE_'): continue
        note = r['meta'][n].get('note', ''); g = re.search(r'(\d+x?\d*AWG|twisted_pair|FFC)', n)
        ln = re.search(r'about (\d+) mm long', note); route = re.sub(r'\s*Insulation OD.*', '', note)
        rows.append(f"| {n[5:].replace('_', ' ')} | {g.group(1) if g else '-'} | {route} | {ln.group(1) + ' mm' if ln else '-'} |")
    return '\n'.join(rows)

def fastener_table():
    rep = json.loads((M / 'fasteners-report.json').read_text())['printed']['joints']
    rows = ['| Joint | Screw | Through / into | Note |', '|---|---|---|---|']
    for j in rep:
        rows.append(f"| {j['joint']} | {j['screw'].split('_')[-2] if j['screw'] else '-'} {j['screw'].split('_')[-1] if j['screw'] else ''} | "
                    f"{' -> '.join(h[1] for h in j['hosts'])} | {j.get('note', '')} |")
    return '\n'.join(rows)

# ------------------------------------------------------------------ CAD
def stage(variant):
    """Copy of the variant with supplier parts replaced by placeholders; returns (stage dir, vendor rows)."""
    src = M / variant; st = OUT.parent / f'.release-stage/{variant}'
    if st.exists(): shutil.rmtree(st)
    st.mkdir(parents=True)
    r = json.loads((src / 'revision.json').read_text()); vend = {}
    for n in r['parts']:
        f = src / (n + '.brep')
        if not f.exists(): continue
        v = vendor_of(n)
        if v:
            ph = placeholder(cq.Shape.importBrep(str(f))); ph.exportBrep(str(st / (n + '.brep')))
            r['meta'][n] = dict(r['meta'][n], note=f"PLACEHOLDER (same size). {v['supplier']} {v['part']}: get the CAD from {v['where']}.", source='placeholder')
            vend[n] = v
        else:
            shutil.copyfile(f, st / (n + '.brep'))
            side = Path(str(f) + '.fch.json')
            if side.exists(): shutil.copyfile(side, st / (n + '.brep.fch.json'))
    (st / 'revision.json').write_text(json.dumps(r))
    return st, r, vend

def history_uses_vendor(sidecar, vendor_blobs):
    d = json.loads(Path(sidecar).read_text())
    for nd in d['nodes'].values():
        if nd['op'] == 'baked' and (nd.get('blob') in vendor_blobs or re.search(r'vendor|supplier|SUPPLIER|odrive-official', nd.get('source', '') or '')):
            return True
    return False

def cad(variant, skip_freecad):
    st, r, vend = stage(variant)
    vendor_blobs = set()
    for n in vend:
        side = M / variant / (n + '.brep.fch.json')
        if side.exists():
            for nd in json.loads(side.read_text())['nodes'].values():
                if nd.get('blob'): vendor_blobs.add(nd['blob'])
    stripped = []
    for side in st.glob('*.brep.fch.json'):
        if history_uses_vendor(side, vendor_blobs): side.unlink(); stripped.append(side.name[:-14])
    # STEP: parts + one assembly
    sd = OUT / 'cad' / 'step' / variant; sd.mkdir(parents=True, exist_ok=True)
    shapes = []
    for n in r['parts']:
        f = st / (n + '.brep')
        if not f.exists(): continue
        s = cq.Shape.importBrep(str(f)); shapes.append(s)
        if n in vend or not (M / variant / (n + '.step')).exists(): s.exportStep(str(sd / (n + '.step')))
        else: shutil.copyfile(M / variant / (n + '.step'), sd / (n + '.step'))
    cq.Compound.makeCompound(shapes).exportStep(str(OUT / 'cad' / 'step' / f'V44_{variant}_assembly.step'))
    if not skip_freecad:
        env = dict(FCH_REUSE=str(R / 'freecad' / '.built.json'))
        run([Path(FC_BIN) / 'python.exe', R / 'fchist' / 'to_freecad.py', st.parent, variant, OUT / 'cad' / 'freecad'], env=env)
        bj = OUT / 'cad' / 'freecad' / '.built.json'                                  # local cache (absolute paths): keep it out of the repo
        if bj.exists(): shutil.move(str(bj), str(st.parent / f'built_{variant}.json'))
        run([Path(FC_BIN) / 'freecad.exe', R / 'fchist' / 'motion_gui.py'],
            env=dict(FCH_HERE=str(R / 'fchist'), FCH_MODEL=str(st.parent), FCH_VARIANT=variant, FCH_OUT=str(OUT / 'cad' / 'freecad')))
    return r, vend, stripped

def dxf(variant, r, vend):
    dd = OUT / 'cad' / 'dxf'; dd.mkdir(parents=True, exist_ok=True); out = []
    for n in r['parts']:
        if n in vend or n.startswith(('F44_', 'WIRE_', 'HARNESS_', 'TRIAL_', 'RESERVE', 'ROUTE', 'ThunderPower', 'JBD_')): continue
        m = r['meta'][n]
        if m.get('kind') not in ('part', None) or not (m.get('manufacture') or n.startswith(('S17_', 'V43_METAL', 'MOUNT_', 'FM10_Square', 'FM10_Front_outer', 'FM10_Rear_inner'))): continue
        f = M / variant / (n + '.brep')
        if not f.exists() or (dd / (n + '.dxf')).exists(): continue
        s = cq.Shape.importBrep(str(f)); b = s.BoundingBox(); d = [b.xlen, b.ylen, b.zlen]; ax = d.index(min(d))
        if min(d) > 12 or sorted(d)[1] < 3 * min(d): continue
        rot = {0: ((0, 1, 0), 90), 1: ((1, 0, 0), -90), 2: ((0, 0, 1), 0)}[ax]
        s2 = s.rotate(cq.Vector(0, 0, 0), cq.Vector(*rot[0]), rot[1]) if rot[1] else s
        b2 = s2.BoundingBox(); s2 = s2.translate(cq.Vector(-b2.xmin, -b2.ymin, -(b2.zmin + b2.zmax) / 2))
        try:
            sec = cq.Workplane('XY').add(s2).section(0.0)
            cq.exporters.export(sec, str(dd / (n + '.dxf')), exportType='DXF'); out.append(n)
        except Exception as e:
            print('dxf skipped', n, e)
    return out

def prints():
    pd = OUT / 'print'; pd.mkdir(parents=True, exist_ok=True)
    for f in (M / 'print-files').glob('*'): shutil.copyfile(f, pd / f.name)
    (pd / 'fit-coupons').mkdir(exist_ok=True)
    for f in (M / 'fit-coupons').glob('*'): shutil.copyfile(f, pd / 'fit-coupons' / f.name)
    return len(list(pd.glob('*.stl')))

def vendor_readme(vend):
    rows = ['# Supplier CAD (not included)', '', 'These parts appear in the CAD as same-size placeholders (`PLACEHOLDER` in their notes). Their CAD belongs',
            'to the suppliers and cannot be redistributed here; download it under each supplier\'s terms and, if you like, replace the',
            'placeholder in your local copy (same part name, same position).', '', '| Part(s) in the model | Supplier | Part | Where to get the CAD |', '|---|---|---|---|']
    by = {}
    for n, v in sorted(vend.items()): by.setdefault((v['supplier'], v['part'], v['where']), []).append(n)
    for (s, p, w), ns in sorted(by.items()):
        rows.append(f"| {', '.join('`' + x + '`' for x in ns[:3])}{' + %d more' % (len(ns) - 3) if len(ns) > 3 else ''} | {s} | {p} | {w} |")
    (OUT / 'cad' / 'vendor').mkdir(parents=True, exist_ok=True)
    (OUT / 'cad' / 'vendor' / 'README.md').write_text('\n'.join(rows) + '\n', encoding='utf-8')

def source():
    sd = OUT / 'source'
    if sd.exists(): shutil.rmtree(sd)
    sets = {'print-v44-nano': ['*.py', '*.sh'], 'mounts-rev11': ['*.py'], 'fchist': ['*.py', '*.sh', 'README.md', 'boot/*.py'], 'release': ['*.py']}
    for d, pats in sets.items():
        for p in pats:
            for f in (R / d).glob(p):
                t = sd / d / f.relative_to(R / d); t.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(f, t)
    for f in ('build_voltra_module10.py', 'audit_voltra_module10.py', 'publish_fairlead_module10_packing.py'):
        t = sd / 'stock-drive-study' / f; t.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(R / 'stock-drive-study' / f, t)
    (sd / 'README.md').write_text('# Build scripts (GPL-3.0)\n\nThe Python / CadQuery scripts that generate every part, the fasteners, the wiring and the FreeCAD files.\n'
        'They are the source of truth for the CAD. In this release they still expect the full design workspace (supplier CAD and the\n'
        'interactive layout data are not published), so treat them as readable source; a self-contained build is planned.\n\n'
        '- `print-v44-nano/run_v44.sh`: the V44 pipeline (parts -> structure -> enclosure -> fasteners -> wiring -> checks)\n'
        '- `mounts-rev11/`: brackets, saddles, board plates; `stock-drive-study/`: the fairlead module\n'
        '- `fchist/`: records the CadQuery history and writes the FreeCAD files; `release/`: builds this repository\n', encoding='utf-8')

# ------------------------------------------------------------------ scan
SCAN = [(r'AKIA[0-9A-Z]{16}', 'AWS key'), (r'(?i)(api[_-]?key|secret|token|passw(or)?d)\s*[:=]\s*[\'"][^\'"]{8,}', 'credential'),
        ('gh' + r'[po]_[A-Za-z0-9]{30,}|github' + '_pat_', 'GitHub token'), (r'sk-[A-Za-z0-9]{20,}', 'API key'),
        (r'xox[abp]-[A-Za-z0-9-]{10,}', 'Slack token'), (r'-----BEGIN [A-Z ]*PRIVATE KEY-----', 'private key'),
        (r'[A-Za-z0-9._%+-]+@(gmail|outlook|hotmail|yahoo|icloud)\.com', 'personal email'),
        (r'(?i)C:[\\/]+Users[\\/]+\w+|/c/Users/\w+|\b' + 'Tren' + r'ton\b|' + 'Trent' + 'Indeed', 'personal path / name'),
        (r'(?i)account_id\s*=|' + 'CLOUDFLARE' + '_API|' + 'wran' + 'gler', 'Cloudflare config'), ('unlocked' + 'efficiency', 'private site')]
# (patterns are split so this file does not match itself)
TEXT = ('.md', '.py', '.sh', '.json', '.csv', '.txt', '.FCMacro', '.step', '.dxf', '.ps1')
def scan():
    hits = []
    for f in OUT.rglob('*'):
        if not f.is_file() or '.git' in f.parts or f.name == '.built.json': continue
        if f.suffix in TEXT and f.stat().st_size < 60_000_000:
            t = f.read_text(encoding='utf-8', errors='ignore')
            for rx, what in SCAN:
                m = re.search(rx, t)
                if m and not (what == 'credential' and 'LICENSES' in f.parts): hits.append((str(f.relative_to(OUT)), what, m.group(0)[:60]))
        if f.suffix == '.FCStd':                                                   # zipped: check the XML inside
            import zipfile
            with zipfile.ZipFile(f) as z:
                for nm in ('Document.xml', 'GuiDocument.xml'):
                    if nm in z.namelist():
                        t = z.read(nm).decode('utf-8', 'ignore')
                        for rx, what in SCAN:
                            m = re.search(rx, t)
                            if m: hits.append((f'{f.relative_to(OUT)}:{nm}', what, m.group(0)[:60]))
    return hits

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    if '--scan-only' not in ARGS:
        allvend, stats, notes = {}, {}, {}
        for v in VARIANTS:
            r, vend, stripped = cad(v, '--skip-freecad' in ARGS); allvend.update(vend)
            notes[v] = dict(placeholders=len(vend), history_removed=stripped, dxf=dxf(v, r, vend))
        stats['n_printed'] = prints()
        hwc = list(csv.DictReader(open(M / 'printed' / 'hardware.csv', encoding='utf-8')))
        stats['n_hw'] = sum(1 for h in hwc if h['part'].startswith('F44_'))
        stats['n_buy'] = len({v['part'] for v in allvend.values()}) + 30
        vendor_readme(allvend); docs(stats); source()
        (OUT / '.gitignore').write_text('cad/freecad/.built.json\n*.FCBak\n__pycache__/\n')
        print(json.dumps(notes, indent=1))
    hits = scan()
    for h in hits: print('SCAN', *h)
    print('scan:', 'CLEAN' if not hits else f'{len(hits)} findings')
    sys.exit(1 if hits else 0)
