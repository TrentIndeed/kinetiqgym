"""V44 phase 1b: replace stand-in geometry with the vendor CAD now in supplier-cad/ (run after build_v44_phase1.py).

Each stand-in's world axis and centre come from its current V44 solid; the vendor solid is rotated so its own axis
matches, then centred there (flange / bore end chosen explicitly). The KHK worm is phased against the printed
53T ring for zero overlap. The TB005 terminal block is placed on the ODrive board face from the Same Sky
drawing; the Littelfuse holder is modelled from drawing OL-04980921GXM5 with the real BF1 fuse inside.
Rewrites {cnc,printed}/revision.json, hardware.csv and the part files; writes swap-report.json.
"""
from pathlib import Path
import json, glob, csv
import numpy as np
import cadquery as cq
from build_v44_phase1 import apply

HERE = Path(__file__).resolve().parent; R = HERE.parent; SC = R / 'supplier-cad'
REV = {m: json.loads((HERE / m / 'revision.json').read_text()) for m in ('cnc', 'printed')}
def load(p): p = Path(p); return cq.Shape.importBrep(str(p)) if p.suffix == '.brep' else cq.importers.importStep(str(p)).val()
def cur(n): return cq.Shape.importBrep(str(HERE / 'printed' / (n + '.brep')))
def g1(pat): return glob.glob(str(pat))[0]
AX = np.eye(3)

def frame(src_axis, dst_axis, src_up=None, dst_up=None):
    """Rotation matrix taking unit vector src_axis to dst_axis (and src_up to dst_up if given)."""
    a, b = np.array(src_axis, float), np.array(dst_axis, float)
    if src_up is None:
        src_up = np.cross(a, [1, 0, 0]) if abs(a[0]) < .9 else np.cross(a, [0, 1, 0])
        dst_up = np.cross(b, [1, 0, 0]) if abs(b[0]) < .9 else np.cross(b, [0, 1, 0])
    S = np.stack([a, src_up / np.linalg.norm(src_up), np.cross(a, src_up / np.linalg.norm(src_up))], 1)
    D = np.stack([b, dst_up / np.linalg.norm(dst_up), np.cross(b, dst_up / np.linalg.norm(dst_up))], 1)
    return D @ S.T

def place(shape, Rm, anchor_src, anchor_dst):
    A = np.eye(4); A[:3, :3] = Rm; A[:3, 3] = np.array(anchor_dst) - Rm @ np.array(anchor_src); return apply(shape, A)

def bbox(s): b = s.BoundingBox(); return np.array([b.xmin, b.ymin, b.zmin]), np.array([b.xmax, b.ymax, b.zmax])
def centre(s): lo, hi = bbox(s); return (lo + hi) / 2

swaps, report = [], []
def swap(old, new_name, shape, group, kind, note, manufacture):
    swaps.append((old, new_name, shape, group, kind, note, manufacture))

def compute():

    # ---- round parts on an axis: (old v44 name, vendor file, vendor axis, world axis, end rule) ----
    def axial(old, f, src_ax, dst_ax, new, note, kind='bearing_reference', flip=False, anchor='centre', dst_point=None, group=None, shift=0.0):
        s = load(f); lo, hi = bbox(s); c_src = (lo + hi) / 2
        d = np.array(dst_ax, float) * (-1 if flip else 1)
        Rm = frame(src_ax, d)
        tgt = (centre(cur(old)) if dst_point is None else np.array(dst_point)) + np.array(dst_ax, float) * shift
        if anchor == 'min':                              # vendor min end along its axis goes to dst_point
            c_src = c_src.copy(); k = int(np.argmax(np.abs(src_ax))); c_src[k] = lo[k]
        swap(old, new, place(s, Rm, c_src, tgt), group or REV['printed']['meta'][old]['group'], kind, note, 'Buy')

    X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
    skf = lambda n: g1(SC / f'skf-{n}' / '*.stp')
    axial('V43_REF_6001_2RS_left_FM6', skf('6001-2rsh'), X, X, 'SKF_6001-2RSH_left', 'SKF 6001-2RSH (6001-2RS), manufacturer STEP.')
    axial('V43_REF_6001_2RS_right_FM9', skf('6001-2rsh'), X, X, 'SKF_6001-2RSH_right', 'SKF 6001-2RSH (6001-2RS), manufacturer STEP.')
    axial('FM10_6809-2RS_pivot_bearing', skf('61809-2rs1'), X, Y, 'SKF_61809-2RS1_pivot_6809', 'SKF 61809-2RS1 (6809-2RS 45x58x7), manufacturer STEP; carries the printed ring journal.')
    axial('FM10_6808_sealed_bearing_1', skf('61808-2rs1'), X, Y, 'SKF_61808-2RS1_exit_6808_1', 'SKF 61808-2RS1 (6808-2RS 40x52x7), manufacturer STEP; exit swivel.')
    axial('FM10_6808_sealed_bearing_2', skf('61808-2rs1'), X, Y, 'SKF_61808-2RS1_exit_6808_2', 'SKF 61808-2RS1 (6808-2RS 40x52x7), manufacturer STEP; exit swivel.')
    g625 = g1(SC / 'generic-bearings-stepparts' / '*625*.st*p')
    for i in (0, 1):
        axial(f'FM10_Roller_625ZZ_{i}', g625, (0, 0, 1) if bbox(load(g625))[1][2] - bbox(load(g625))[0][2] < 6 else X, X, f'Bearing_625ZZ_roller_{i}',
              '625ZZ 5x16x5, step.parts generic model (SKF 625-2Z download did not arrive); rope roller inside the journal.')
    g1601 = g1(SC / 'gobilda-1601-0014-0006' / '*.STEP'); g1611 = g1(R / 'stock-drive-study/1611-0514-4008/*.STEP')
    # goBILDA flanged bearings: vendor axis +Y, flange at the +Y end. Flange outboard of each shaft.
    axial('FM10_Worm_shaft_1601_bearing_0', g1601, Y, X, 'goBILDA_1601-0014-0006_worm_bearing_0', 'goBILDA 1601-0014-0006 flanged bearing 6x14x5, supplier STEP; flange seated on the outboard cradle face.', flip=True, shift=-1.0)
    axial('FM10_Worm_shaft_1601_bearing_1', g1601, Y, X, 'goBILDA_1601-0014-0006_worm_bearing_1', 'goBILDA 1601-0014-0006 flanged bearing 6x14x5, supplier STEP; flange seated on the outboard cradle face.', shift=1.0)
    axial('FM10_Shaft_2_1611_bearing_0', g1611, Y, X, 'goBILDA_1611-0514-4008_shaft2_bearing_0', 'goBILDA 1611-0514-4008 flanged bearing 8 mm REX, supplier STEP; flange on the pedestal face toward the 20T.', flip=True, shift=-1.0)
    axial('FM10_Shaft_2_1611_bearing_1', g1611, Y, X, 'goBILDA_1611-0514-4008_shaft2_bearing_1', 'goBILDA 1611-0514-4008 flanged bearing 8 mm REX, supplier STEP; flange on the outboard pedestal face (rev 12: the 60T sits 1 mm inboard of the pedestal).', shift=1.0)
    # shafts: same span as the envelopes
    old = 'FM10_Shaft_2_8mm_REX_envelope'; lo, hi = bbox(cur(old))
    s = load(g1(SC / 'gobilda-2106-4008-0560' / '*.STEP')); sl, sh = bbox(s)
    def clock(shp, axis_pt, mates, step, span):
        ms = [cq.Shape.importBrep(g1(HERE / 'printed' / (m + '.brep'))) for m in mates]
        best = min(((a, sum(shp.rotate(cq.Vector(*axis_pt), cq.Vector(*(np.array(axis_pt) + [1, 0, 0])), a).intersect(m).Volume() for m in ms)) for a in np.arange(0, span, step)), key=lambda t: t[1])
        report.append(dict(part='clock', mates=mates, angle=float(best[0]), overlap_mm3=round(best[1], 3)))
        return shp.rotate(cq.Vector(*axis_pt), cq.Vector(*(np.array(axis_pt) + [1, 0, 0])), best[0])
    rex_axis = np.array([lo[0], (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2])
    body = max(s.Solids(), key=lambda so: so.Volume()); bl, bh = bbox(body)            # shaft body, not the e-clip
    rex = place(s, frame(Y, X), np.array([(bl[0] + bh[0]) / 2, bl[1], (bl[2] + bh[2]) / 2]), rex_axis)
    rex = clock(rex, rex_axis, ['FM10_goBILDA_2303-4008-0020_20T_shaft-2_gear'], 2.0, 60.0)
    for k, sw in enumerate(swaps):                                       # clock the 1611 REX bores to the shaft
        if '1611' in sw[1]:
            best = min(((a, sw[2].rotate(cq.Vector(*rex_axis), cq.Vector(*(rex_axis + [1, 0, 0])), a).intersect(rex).Volume()) for a in np.arange(0, 60, 1.0)), key=lambda t: t[1])
            swaps[k] = (sw[0], sw[1], sw[2].rotate(cq.Vector(*rex_axis), cq.Vector(*(rex_axis + [1, 0, 0])), best[0]), *sw[3:])
            report.append(dict(part='clock', mates=[sw[1], 'REX shaft'], angle=float(best[0]), overlap_mm3=round(best[1], 3)))
    swap(old, 'goBILDA_2106-4008-0560_REX_shaft_56', rex,
         'drivetrain', 'part', 'goBILDA 2106-4008-0560 8 mm REX shaft 56 mm with e-clip, supplier STEP (shaft 2).', 'Buy')
    old = 'FM10_Worm_shaft_6mm_D_envelope'; lo, hi = bbox(cur(old))
    s = load(g1(SC / 'servocity-2101-0006-0060' / '*.STEP'))
    d_axis = np.array([lo[0], (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2])
    dsh = clock(place(s, frame(Y, X), np.array([0, 0, 0.0]), d_axis), d_axis, ['FM10_goBILDA_2303-1006-0020_20T_D-bore_worm-shaft_gear'], 5.0, 360.0)
    swap(old, 'ServoCity_2101-0006-0060_D_shaft_60', dsh,
         'fairlead', 'part', 'ServoCity 2101-0006-0060 6 mm stainless D-shaft 60 mm, supplier STEP (worm shaft).', 'Buy')
    # NBK coupling: vendor X 0..31, 10 mm bore at x=0 -> motor side (-X); shaft gap centre X 36.5
    old = 'REF_coupler_APPROX_10_to_12mm'; lo, hi = bbox(cur(old))
    s = load(SC / 'nbk-msts-25-10-12/MSTS-25-10-12.stp')
    swap(old, 'NBK_MSTS-25-10-12_coupling', place(s, np.eye(3), np.array([15.5, 0, 0]), np.array([36.5, -62.5, 43.0])), 'drivetrain', 'part',
         'NBK MSTS-25-10-12 slit coupling OD25 x L31, bores 10 (motor) / 12 (drum), manufacturer STEP. Closest real part to the user-confirmed flexible OD25 x L30 coupler.', 'Buy')

    # ---- KHK worm: fully threaded 30 mm, same span as before, phased for zero overlap with the printed ring ----
    old = 'FM10_KHK_SW0.8-R1_worm_module_0.8_1_start'
    lo, hi = bbox(cur(old)); ax_c = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2])
    worm0 = place(load(SC / 'khk-SW0.8-R1/KHK-US_SW0_8-R1.stp'), frame(Z, X), np.zeros(3), ax_c)
    ring = cq.Shape.importBrep(g1(HERE / 'printed' / 'FM10_Printed_PA-CF_carrier*.brep'))
    zone = cq.Solid.makeBox(40, 24, 24, cq.Vector(ax_c[0] - 20, ax_c[1] - 12, ax_c[2] - 12)); rz = ring.intersect(zone)
    def worm_at(a): return worm0.rotate(cq.Vector(*ax_c), cq.Vector(*(ax_c + [1, 0, 0])), a)
    scan = [(a, worm_at(a).intersect(rz).Volume()) for a in range(0, 360, 10)]
    a0 = min(scan, key=lambda t: t[1])[0]
    fine = [(a, worm_at(a).intersect(rz).Volume()) for a in np.arange(a0 - 9, a0 + 9.1, 1.0)]
    free = [a for a, v in fine if v < 1e-4]
    best = float(np.mean([free[len(free) // 2]]) if free else min(fine, key=lambda t: t[1])[0])
    worm = worm_at(best); ov = worm.intersect(rz).Volume()
    report.append(dict(part='KHK worm', phase_deg=best, overlap_mm3=round(ov, 5), zero_overlap_phases=[float(a) for a in free]))
    swap(old, 'KHK_SW0.8-R1_worm', worm, 'fairlead', 'part',
         f'KHK SW0.8-R1 steel worm, manufacturer STEP (fully threaded 30 mm). Phased {best:.0f} deg about its axis for zero overlap with the printed 53T ring (overlap {ov:.4f} mm3).', 'Buy')

    # ---- TB005-762-05BE on the ODrive board face (component side +X; the envelope starts 0.1 mm off the PCB face) ----
    old = 'V3_REF_ODrive_TB005_762_05BE_terminal_ENVELOPE'; lo, hi = bbox(cur(old)); PCB_FACE = lo[0] - 0.1
    s = load(SC / 'tb005-762-05be/Same_Sky_TB005-762-05BE.step')
    # vendor: Y = PCB normal (pins at -Y, seat plane y=0), Z = along the 5 poles, X = depth (wire-entry face x=0, pin row x=7.9)
    Rm = np.array([[0, 1, 0], [1, 0, 0], [0, 0, -1]], float)            # x->Y, y->X, z->-Z (proper rotation)
    zc = (-12.03 + 26.67) / 2
    tb = place(s, Rm, np.array([0, 0, zc]), np.array([PCB_FACE, -97.9, 43.0]))
    FLIPPED = (lo[1] + hi[1]) / 2 > -62.5                                 # round 6: ODrive turned 180 deg about the shaft axis
    if FLIPPED: tb = tb.rotate(cq.Vector(0, -62.5, 43.0), cq.Vector(1, -62.5, 43.0), 180)   # block on the back edge, entries face +Y
    report.append(dict(part='TB005-762-05BE', world_bbox=[round(v, 2) for v in (*bbox(tb)[0], *bbox(tb)[1])],
                       finding='Real block is 21.7 mm tall off the PCB (the old envelope assumed 11.9). ' + ('Round 6: ODrive turned, so the block is on the back edge and its wire entries face the back (+Y), into the back terminal wiring space.' if FLIPPED else 'Wire entries face the front (-Y), into the rev 12 terminal wiring space.')))
    swap(old, 'SameSky_TB005-762-05BE_ODrive_terminal', tb, 'electronics', 'electronics_reference',
         'Same Sky (CUI) TB005-762-05BE 5-pole 7.62 mm terminal block, manufacturer STEP, placed from the datasheet on the ODrive board face (pin row position on the board to verify). 21.7 mm tall; wire entries face ' + ('the back (round 6).' if FLIPPED else 'the front.'), 'Buy')

    # ---- round 7: exact vendor geometry for the page's power parts (the page carries their meshes) ----
    import sys; sys.path.insert(0, str(R / 'mounts-rev11')); import power_parts as PP
    _parts = REV['printed']['parts']
    def _find(prefix): return next((n for n in _parts if n.startswith(prefix)), None)
    _h, _fz = PP.fuse_holder()
    _old = _find('PART_Littelfuse')
    if _old:
        swap(_old, 'Littelfuse_04980921GXM5_holder', _h, 'power', 'part', 'Littelfuse 04980921GXM5 MIDI 58 V inline holder with cover, M5 studs 30 mm apart, manufacturer STEP. Round 11: under the fan and the WAGO.', 'Buy')
        swaps.append((None, 'Littelfuse_BF1_142.5631.5402_fuse_40A', _fz, 'power', 'part', 'Littelfuse BF1 58 V M5 fuse (series STEP 142.5631.0000; 142.5631.5402 = 40 A), manufacturer STEP, on the holder studs.', 'Buy'))
    for pre, new, shp, note in (('PART_XT60E-F', 'AMASS_XT60E-F_charge_port', PP.xt60ef(), 'AMASS XT60E-F female panel socket, flange flush in the rear I/O panel pocket (STEP scaled to the Amass size).'),):
        old = _find(pre)
        if old: swap(old, new, shp, 'power', 'part', note, 'Buy')


# Round 8: replay the swaps when this script and every file the computation read are unchanged (v44cache.Memo)
import v44cache as VC
MEMO = VC.Memo('swap', __file__); SWAP_DIR = MEMO.dir
MEMO.deps.update({str(HERE / 'printed' / 'revision.json'), str(R / 'mounts-rev11' / 'power_parts.py')})
_m = MEMO.hit()
if _m and all((SWAP_DIR / (n + '.brep')).exists() for _, n, *_ in _m['swaps']):
    for old, new, group, kind, note, manu in _m['swaps']:
        swaps.append((old, new, cq.Shape.importBrep(str(SWAP_DIR / (new + '.brep'))), group, kind, note, manu))
    report.extend(_m['report']); print('swap memo: replayed', len(swaps), 'swaps', flush=True)
else:
    MEMO.record(); compute()
    SWAP_DIR.mkdir(parents=True, exist_ok=True)
    for _, new, shp, *_ in swaps: shp.exportBrep(str(SWAP_DIR / (new + '.brep')))
    MEMO.deps.update({str(HERE / 'printed' / 'revision.json'), str(R / 'mounts-rev11' / 'power_parts.py')})
    MEMO.save(dict(report=report, swaps=[(o, n, g, k, note, manu) for o, n, _, g, k, note, manu in swaps]))

# ---- write ----
for mode in ('cnc', 'printed'):
    r = REV[mode]; d = HERE / mode
    for old, new, shp, group, kind, note, manu in swaps:
        if old and old in r['parts']:
            i = r['parts'].index(old); r['parts'].pop(i); dm = r['meta'].pop(old); r['colors'].pop(old, None)
            for ext in ('.step', '.brep'): (d / (old + ext)).unlink(missing_ok=True)
            for v in r['views'].values():
                if old in v: v[v.index(old)] = new
        else:
            dm = {}
            for k in ('complete', 'open', 'wiring' if group in ('power', 'wiring', 'electronics') else 'drivetrain'):
                r['views'][k].append(new)
        r['parts'].append(new) if new not in r['parts'] else None
        r['meta'][new] = dict(group=group, kind=kind, note=note, manufacture=manu, demo_name=dm.get('demo_name', ''), source='vendor CAD / drawing (swap_real_cad.py)', replaced=old)
        r['colors'][new] = [.78, .8, .82] if kind in ('bearing_reference',) else [.55, .57, .6] if manu == 'Buy' else [.3, .55, .62]
        if not shp.isValid(): shp = shp.fix()
        shp.exportStep(str(d / (new + '.step'))); shp.exportBrep(str(d / (new + '.brep')))
    hw = [h for h in r['hardware'] if h['part'] in r['parts']]
    for old, new, shp, group, kind, note, manu in swaps:
        if manu == 'Buy': hw.append(dict(part=new, group=group, kind=kind, size=new, source='supplier-cad/', note=note[:160]))
    r['hardware'] = hw
    r['status'] = 'V44 phase 1b engineering preview (design layout rev 12): live-demo layout as real CAD with vendor STEPs swapped in (bearings, coupling, shafts, KHK worm, terminal block, fuse). New base, enclosure and rack puck not built yet.'
    (d / 'revision.json').write_text(json.dumps(r, indent=1))
    with open(d / 'hardware.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['part', 'group', 'kind', 'size', 'source', 'note']); w.writeheader(); w.writerows(hw)
for old, new, shp, *_ in swaps:
    lo, hi = bbox(shp); report.append(dict(new=new, replaced=old, world_bbox=[round(float(v), 2) for v in (*lo, *hi)], valid=shp.isValid()))
(HERE / 'swap-report.json').write_text(json.dumps(report, indent=1))
print(json.dumps(report[:3], indent=1)); print('swapped', len(swaps), 'parts; total', len(REV['printed']['parts']))
