"""Write FreeCAD files with the full feature history of every V44 part (run with FreeCAD's Python: fchist/make_freecad.ps1).

For each part file <model>/<variant>/<part>.brep with a history (<part>.brep.fch.json, written by fchist_rec.py during
the pipeline run) a parametric part document is built: Part primitives (Box, Cylinder, Cone, Sphere, Torus) with their
placements, booleans (Cut, MultiFuse, MultiCommon), Refine, Fillet / Chamfer (edges found again by position), Mirroring,
Compound. Moves of a feature become its Placement. Steps that cannot be replayed (wire extrusions, text, sweeps, vendor
CAD, picked solids) are exact "Base" shapes. Every feature is labelled with the build script line that made it.
Each part is checked against the pipeline's own shape (volume and bounding box); a part that does not match keeps its
history but shows the exact shape on top (listed in the report). An assembly document links every part, grouped.

usage: python to_freecad.py <model_dir> <variant> <out_dir> [part-name-prefix ...]
"""
import sys, os, json, math, time, traceback, hashlib, shutil
from pathlib import Path
sys.path.append(os.environ.get('FREECAD_BIN', r'D:/Programs/FreeCAD_1.1.4-Windows-x86_64-py311/bin'))
import FreeCAD as App, Part
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guidoc
for k, v in (('CreateBackupFiles', False),): App.ParamGet('User parameter:BaseApp/Preferences/Document').SetBool(k, v)
App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles', 0)

MODEL, VARIANT, OUT = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
ONLY = sys.argv[4:]
SRC = MODEL / VARIANT
STORE = Path(os.environ.get('FCHIST_STORE', Path(__file__).resolve().parent.parent / '.fchist'))
REV = json.loads((SRC / 'revision.json').read_text())
PARTS_DIR = OUT / VARIANT / 'parts'; PARTS_DIR.mkdir(parents=True, exist_ok=True)
NAMES = {'box': 'Box', 'cylinder': 'Cylinder', 'cone': 'Cone', 'sphere': 'Sphere', 'torus': 'Torus', 'cut': 'Cut', 'fuse': 'Fuse',
         'common': 'Common', 'refine': 'Refine', 'fillet': 'Fillet', 'chamfer': 'Chamfer', 'mirror': 'Mirror', 'compound': 'Compound', 'baked': 'Base'}
I4 = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))

def mat(m):
    m = [list(r) for r in m]
    if len(m) == 3: m.append([0, 0, 0, 1])
    return tuple(tuple(float(v) for v in r) for r in m)

def mul(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)) for i in range(4))

def placement(m):
    M = App.Matrix(*[m[i][j] for i in range(4) for j in range(4)])
    return App.Placement(M)

def key(m): return tuple(round(v, 7) for r in m for v in r)

_blobs = {}
def blob(h):
    if h not in _blobs:
        s = Part.Shape(); s.read(str(STORE / 'blobs' / (h + '.brep'))); _blobs[h] = s
    return _blobs[h]

class Builder:
    def __init__(self, doc, nodes, fold=True):
        self.doc, self.nodes, self.memo, self.objs, self.notes, self.fold = doc, nodes, {}, [], [], fold
        self.users = {}
        for k, n in nodes.items():
            for x in n['inputs']: self.users[str(x)] = self.users.get(str(x), 0) + 1

    def add(self, typ, n, label):
        o = self.doc.addObject(typ, NAMES.get(n['op'], 'Feature'))
        o.Label = label
        site = n.get('site', '')
        if site: o.Label2 = site
        self.objs.append(o); return o

    def label(self, n, extra=''):
        site = n.get('site', '')
        where = site.split(' ')[0] if site else ''
        func = site.split(' ', 1)[1] if ' ' in site else ''
        return f"{NAMES.get(n['op'], n['op'])}{extra} · {where}{(' ' + func) if func and func != '<module>' else ''}"

    def build(self, i, M=I4, refine=False):
        i = str(i); k = (i, key(M), refine)
        if k in self.memo: return self.memo[k]
        n = self.nodes[i]; op = n['op']; ins = n['inputs']
        if op == 'refine' and self.nodes[str(ins[0])]['op'] in ('cut', 'fuse', 'common') and len(self.nodes[str(ins[0])]['inputs']) > 1:
            o = self.build(ins[0], M, refine=True)                          # the boolean's own Refine: keeps the tree nested
        elif op == 'xform':
            o = self.build(ins[0], mul(M, mat(n['m'])), refine)
        elif op in ('fuse', 'compound') and len(ins) == 1:
            o = self.build(ins[0], M)
        elif op == 'cut' and len(ins) == 1:
            o = self.build(ins[0], M)
        elif op in ('box', 'cylinder', 'cone', 'sphere', 'torus'):
            o = self.prim(n, M)
        elif op == 'cut':
            base = self.build(ins[0])
            tools = [self.build(x) for x in ins[1:]]
            if len(tools) > 1:
                tool = self.add('Part::MultiFuse', dict(op='fuse', site=n.get('site')), self.label(dict(op='fuse', site=n.get('site')), f' of {len(tools)} tools'))
                tool.Shapes = tools; tool.Visibility = False
            else: tool = tools[0]
            o = self.add('Part::Cut', n, self.label(n)); o.Base, o.Tool = base, tool; o.Placement = placement(M)
            if refine: o.Refine = True
        elif op in ('fuse', 'common'):
            o = self.add('Part::MultiFuse' if op == 'fuse' else 'Part::MultiCommon', n, self.label(n))
            o.Shapes = [self.build(x) for x in ins]; o.Placement = placement(M)
            if refine: o.Refine = True
        elif op == 'compound':
            o = self.add('Part::Compound', n, self.label(n)); o.Links = [self.build(x) for x in ins]; o.Placement = placement(M)
        elif op == 'refine' and self.fold:
            o = self.build(ins[0], M)                                       # Part::Refine breaks the tree; geometry is the same
        elif op == 'refine':
            o = self.add('Part::Refine', n, self.label(n)); o.Source = self.build(ins[0]); o.Placement = placement(M)
        elif op in ('fillet', 'chamfer'):
            o = self.edge_op(n, M)
        elif op == 'mirror':
            o = self.add('Part::Mirroring', n, self.label(n)); o.Source = self.build(ins[0])
            o.Normal = App.Vector(*n['normal']); o.Base = App.Vector(*n['base']); o.Placement = placement(M)
        else:                                                                 # baked
            o = self.baked(n, M)
        self.memo[k] = o
        return o

    def prim(self, n, M):
        op = n['op']; P = placement(mul(M, mat(n['m'])))
        if op == 'box':
            o = self.add('Part::Box', n, self.label(n, f" {n['L']:g} x {n['W']:g} x {n['H']:g}")); o.Length, o.Width, o.Height = n['L'], n['W'], n['H']
        elif op == 'cylinder':
            o = self.add('Part::Cylinder', n, self.label(n, f" r{n['r']:g} x {n['h']:g}")); o.Radius, o.Height, o.Angle = n['r'], n['h'], n['angle']
        elif op == 'cone':
            o = self.add('Part::Cone', n, self.label(n, f" r{n['r1']:g}/{n['r2']:g} x {n['h']:g}"))
            o.Radius1, o.Radius2, o.Height, o.Angle = n['r1'], n['r2'], n['h'], n['angle']
        elif op == 'sphere':
            o = self.add('Part::Sphere', n, self.label(n, f" r{n['r']:g}")); o.Radius = n['r']; o.Angle1, o.Angle2, o.Angle3 = n['a1'], n['a2'], n['a3']
        else:
            o = self.add('Part::Torus', n, self.label(n, f" R{n['r1']:g} r{n['r2']:g}")); o.Radius1, o.Radius2 = n['r1'], n['r2']
            a1, a2 = (-180.0, 180.0) if n['a2'] - n['a1'] >= 360 - 1e-9 else (n['a1'], n['a2'])     # FreeCAD: minor angles in -180..180
            o.Angle1, o.Angle2, o.Angle3 = a1, a2, 360.0
        o.Placement = P
        return o

    def edge_op(self, n, M):
        base = self.build(n['inputs'][0])
        self.doc.recompute()
        edges = base.Shape.Edges; idx = []
        for e in n['edges']:
            c, L, i = App.Vector(*e['c']), e['L'], e['i']
            def ok(k): return 0 < k <= len(edges) and (edges[k - 1].CenterOfMass - c).Length < 1e-3 and abs(edges[k - 1].Length - L) < 1e-3
            if not ok(i):
                best = min(range(1, len(edges) + 1), key=lambda k: (edges[k - 1].CenterOfMass - c).Length + abs(edges[k - 1].Length - L), default=None)
                i = best if best and (edges[best - 1].CenterOfMass - c).Length < 0.05 else None
                if i is None: self.notes.append(f"{n.get('site')}: an edge of the {n['op']} was not found"); continue
            idx.append(i)
        if n['op'] == 'fillet':
            o = self.add('Part::Fillet', n, self.label(n, f" r{n['r']:g}")); o.Base = base; o.Edges = [(i, n['r'], n['r']) for i in idx]
        else:
            o = self.add('Part::Chamfer', n, self.label(n, f" {n['d']:g}")); o.Base = base; o.Edges = [(i, n['d'], n['d2']) for i in idx]
        o.Placement = placement(M)
        return o

    def baked(self, n, M):
        what = n.get('what', '')
        src = Path(n['source']).name if n.get('source') else ''
        lab = f"Base: {src or what} · {n.get('site', '').split(' ')[0]}" if (src or what) else 'Base'
        o = self.add('Part::Feature', n, lab)
        if not n.get('blob'):
            self.notes.append(f"{n.get('site')}: a base shape was not stored"); return o
        s = blob(n['blob']).copy()
        s.Placement = placement(M).multiply(s.Placement)
        o.Shape = s
        return o

def check(shape, ref):
    """Relative volume and area difference, and centre-of-mass distance (bounding boxes of trimmed curved faces are loose)."""
    try:
        dv = abs(shape.Volume - ref.Volume) / max(abs(ref.Volume), 1e-6)
        da = abs(shape.Area - ref.Area) / max(abs(ref.Area), 1e-6)
        dc = (shape.CenterOfGravity - ref.CenterOfGravity).Length if hasattr(shape, 'CenterOfGravity') else              (Part.Compound(shape.Solids).CenterOfMass - Part.Compound(ref.Solids).CenterOfMass).Length
        return max(dv, da), dc
    except Exception:
        return 1.0, 1e9

def part_doc(name):
    f = SRC / (name + '.brep'); side = Path(str(f) + '.fch.json')
    ref = Part.Shape(); ref.read(str(f))
    doc = App.newDocument(name.replace('-', '_').replace('.', '_')[:60])
    doc.Label = name
    meta = REV['meta'].get(name, {})
    rep = dict(part=name, group=meta.get('group'), features=0, parametric=0, baked=0, status='', notes=[])
    t0 = time.time()
    if side.exists():
        d = json.loads(side.read_text())
        for fold in (True, False):                                          # retry with Refine features if folding changed it
            b = Builder(doc, d['nodes'], fold)
            try:
                root = b.build(d['root'])
                doc.recompute()
                ok = root.isValid() and not root.Shape.isNull()
                dv, db = check(root.Shape, ref) if ok else (1.0, 1e9)
            except Exception as e:
                ok, dv, db = False, 1.0, 1e9; b.notes.append('build: ' + str(e)[:200]); root = None
            if (ok and dv < 1e-4 and db < 1e-3) or not fold: break
            for o in list(doc.Objects): doc.removeObject(o.Name)
        rep['features'] = len(b.objs); rep['baked'] = sum(1 for o in b.objs if o.TypeId == 'Part::Feature')
        rep['parametric'] = rep['features'] - rep['baked']; rep['notes'] = b.notes
        for o in b.objs: o.Visibility = False
        if ok and dv < 1e-4 and db < 1e-3:                                 # volume + area within 1e-4, centre of mass within 1 um
            rep['status'] = 'history' if rep['parametric'] else 'exact shape (made outside the recorded scripts)'
            root.Label = name; root.Visibility = True; top = root
        else:
            rep['status'] = 'history (differs: exact shape on top)'; rep['dv'], rep['db'] = round(dv, 6), round(db, 4)
            top = doc.addObject('Part::Feature', 'Exact'); top.Shape = ref; top.Label = name
            if root is not None: root.Label = name + ' (rebuilt history)'
    else:
        top = doc.addObject('Part::Feature', 'Exact'); top.Shape = ref; top.Label = name; rep['status'] = 'no history (exact shape)'
    top.addProperty('App::PropertyString', 'Manufacture', 'V44').Manufacture = meta.get('manufacture', '') or ''
    top.addProperty('App::PropertyString', 'Note', 'V44').Note = (meta.get('note', '') or '')[:2000]
    path = str(PARTS_DIR / (name + '.FCStd')); doc.saveAs(path)
    rep['seconds'] = round(time.time() - t0, 1); rep['tip'] = top.Name
    App.closeDocument(doc.Name)
    guidoc.write(path, {rep['tip']: (True, tuple(REV.get('colors', {}).get(name, (0.7, 0.7, 0.72))[:3]))})
    return rep

def assembly(reports):
    """Links grouped by subsystem; a part that takes heat-set inserts is an App::Part holding the part and its inserts."""
    asm = App.newDocument('V44_' + VARIANT); asm.Label = f'V44 {VARIANT} assembly'
    path = str(OUT / VARIANT / f'V44_{VARIANT}_assembly.FCStd'); asm.saveAs(path)            # links need a saved owner
    names = {r['part'] for r in reports}
    host = {n: m['host'] for n, m in REV['meta'].items() if m.get('kind') == 'insert' and m.get('host') in names and n in names}
    groups, holders, links = {}, {}, {}
    def group(g):
        if g not in groups: groups[g] = asm.addObject('App::DocumentObjectGroup', g); groups[g].Label = g
        return groups[g]
    for r in reports:
        p = App.openDocument(str(PARTS_DIR / (r['part'] + '.FCStd')), hidden=True)
        ln = asm.addObject('App::Link', 'L'); ln.setLink(p.getObject(r['tip'])); ln.Label = r['part']
        ln.LinkTransform = True                                             # use the part's own Placement (off by default)
        links[r['part']] = (ln, r.get('group') or 'other')
    for n in sorted(set(host.values())):                                    # host part + its inserts move together
        ln, g = links[n]
        h = asm.addObject('App::Part', 'WithInserts'); h.Label = n + ' + inserts'
        group(g).addObject(h); h.addObject(ln); holders[n] = h
    for n, (ln, g) in links.items():
        if n in holders: continue
        if n in host: holders[host[n]].addObject(ln)
        else: group(g).addObject(ln)
    asm.recompute(); asm.save()
    shown = set(REV.get('views', {}).get('complete', REV['parts']))
    style = {o.Name: (True, None) for o in list(groups.values()) + list(holders.values())}
    for o in asm.Objects:
        if o.TypeId == 'App::Link': style[o.Name] = (o.Label in shown, None)
    App.closeDocument(asm.Name)
    guidoc.write(path, style)

def fsha(p): return hashlib.sha1(Path(p).read_bytes()).hexdigest()

if __name__ == '__main__' and ONLY == ['--assembly']:                       # relink only, from the last report
    assembly([r for r in json.loads((OUT / VARIANT / 'freecad-report.json').read_text()) if r['status'] != 'failed'])
    sys.exit(0)

if __name__ == '__main__':
    parts = [n for n in REV['parts'] if (SRC / (n + '.brep')).exists() and (not ONLY or n.startswith(tuple(ONLY)))]
    built_f = OUT / '.built.json'                                           # brep+history hash -> built file (both variants)
    built = json.loads(built_f.read_text()) if built_f.exists() else {}
    _ru = os.environ.get('FCH_REUSE')                                          # read-only cache of another build (the release reuses ours)
    reuse = json.loads(Path(_ru).read_text()) if _ru and Path(_ru).exists() else {}
    reports = []
    for n in parts:
        f = SRC / (n + '.brep'); side = Path(str(f) + '.fch.json')
        h = fsha(f) + (fsha(side) if side.exists() else '')
        dst = PARTS_DIR / (n + '.FCStd'); prev = built.get(h) or reuse.get(h)
        if prev and Path(prev['file']).exists() and 'differs' not in prev['report'].get('status', ''):                           # unchanged, or the same part in the other variant
            if Path(prev['file']) != dst: shutil.copyfile(prev['file'], dst)
            r = dict(prev['report'], seconds=0.0, reused=True)
        else:
            try: r = part_doc(n)
            except Exception as e:
                r = dict(part=n, status='failed', notes=[traceback.format_exc()[-400:]])
            if r['status'] != 'failed':
                built[h] = dict(file=str(dst), report=r); built_f.write_text(json.dumps(built))
        r = dict(r, part=n, group=REV['meta'].get(n, {}).get('group'))
        reports.append(r)
        print(f"{n}: {r['status']} | {r.get('parametric', 0)} parametric + {r.get('baked', 0)} base features | {r.get('seconds', '')} s", flush=True)
    if not ONLY: assembly([r for r in reports if r['status'] != 'failed'])
    (OUT / VARIANT / 'freecad-report.json').write_text(json.dumps(reports, indent=1))
