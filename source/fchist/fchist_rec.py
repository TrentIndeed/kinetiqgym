"""Feature-history recorder for the CadQuery pipeline (FreeCAD export, open-source path step 1).

Activated by FCHIST=1 (boot/sitecustomize.py installs it before any build script runs; the scripts are not changed).
Every CadQuery modelling call is recorded as a node: primitives (box, cylinder, cone, sphere, torus), booleans (cut, fuse,
common), rigid moves, mirror, refine (clean), fillet / chamfer (edges by index + midpoint), compounds. Anything else
(extrusions of wires, text, sweeps, splits, picking one solid of a compound, shapes made straight in OCP) becomes a
"baked" node that keeps its exact shape. When a shape is written (exportBrep / exportStep) its history is written next
to it as <file>.fch.json, baked shapes go to the blob store (.fchist/blobs, by content hash). When a file with a fresh
history is read back (importBrep / importStep, the next pipeline stage), the history continues from there, so the final
part files carry their history back to the first primitive. fchist/to_freecad.py turns it into FreeCAD feature trees.
"""
from pathlib import Path
import hashlib, io, json, math, os, shutil, sys, weakref

ROOT = Path(__file__).resolve().parent.parent                                   # cad/single-cable
STORE = Path(os.environ.get('FCHIST_STORE', ROOT / '.fchist'))
BLOBS = STORE / 'blobs'
_SKIP = ('cadquery', 'OCP', 'fchist', 'site-packages', 'importlib', '<frozen')
NODES = {}                                                                     # id -> node dict
SHAPES = {}                                                                    # id -> shape (strong) for baked nodes in use
WEAK = {}                                                                      # id -> weakref for baked nodes not yet used
_n = [0]
ATTR = '_fch'
_ORIG = {}

def _id():
    _n[0] += 1; return _n[0]

def _site():
    f = sys._getframe(2)
    while f is not None:
        fn = f.f_code.co_filename.replace('\\', '/')
        if not any(s in fn for s in _SKIP):
            return f'{Path(fn).name}:{f.f_lineno} {f.f_code.co_name}'
        f = f.f_back
    return '?'

def _vec(v):
    if v is None: return None
    if hasattr(v, 'x'): return [float(v.x), float(v.y), float(v.z)]
    v = list(v); return [float(a) for a in (v + [0.0] * 3)[:3]]

def _ax2(pnt, d):
    """Rotation of OCC's gp_Ax2(pnt, dir) (its automatic X direction): rows = world coords of local X, Y, Z."""
    from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
    a = gp_Ax2(gp_Pnt(*pnt), gp_Dir(*d)); X, Y, Z = a.XDirection(), a.YDirection(), a.Direction()
    return [[X.X(), Y.X(), Z.X(), pnt[0]], [X.Y(), Y.Y(), Z.Y(), pnt[1]], [X.Z(), Y.Z(), Z.Z(), pnt[2]]]

def _trsf(t):
    return [[t.Value(i, j) for j in range(1, 5)] for i in range(1, 4)]

def _rigid(m):
    import numpy as np
    R = np.array(m)[:, :3]
    return abs(np.linalg.det(R) - 1) < 1e-6 and np.allclose(R @ R.T, np.eye(3), atol=1e-6)

def node(op, inputs=(), site=None, **kw):
    i = _id(); NODES[i] = dict(op=op, inputs=list(inputs), site=site or _site(), **kw); return i

def nid(shape, site=None):
    """Node of a shape; an unrecorded shape becomes a baked node (exact shape kept)."""
    i = getattr(shape, ATTR, None)
    if i is not None and i in NODES:
        if i in WEAK:                                                          # baked node now used: keep it
            s = WEAK.pop(i)(); SHAPES[i] = s if s is not None else shape
        return i
    try:
        j = REG.get(hash(shape.wrapped))
        if j is not None and j in NODES:
            setattr(shape, ATTR, j); return nid(shape)
    except Exception: pass
    i = node('baked', site=site or _site(), what=type(shape).__name__); SHAPES[i] = shape
    try: setattr(shape, ATTR, i)
    except Exception: pass
    return i

REG = {}                                                                       # OCC shape identity -> node (wrappers made by CadQuery itself)

def tag(shape, i):
    try:
        setattr(shape, ATTR, i); REG[hash(shape.wrapped)] = i
        if type(shape).__name__ == 'Compound':                                 # a compound of one solid stands for that solid
            from OCP.TopoDS import TopoDS_Iterator
            it = TopoDS_Iterator(shape.wrapped); kids = []
            while it.More() and len(kids) < 2: kids.append(it.Value()); it.Next()
            if len(kids) == 1: REG[hash(kids[0])] = i
    except Exception: pass
    return shape

def tag_xform(result, source, matrix):
    """For code that moves a shape straight with OCP (a 4x4 or 3x4 matrix): record it as a rigid move."""
    m = [list(map(float, r[:4])) for r in list(matrix)[:3]]
    return tag(result, node('xform', [nid(source)], m=m) if _rigid(m) else _baked(result, 'xform (not rigid)', [nid(source)]))

def _baked(shape, what, inputs=()):
    i = node('baked', inputs, what=what); WEAK[i] = weakref.ref(shape); return i

# ---------------------------------------------------------------- patches
def install():
    import cadquery as cq
    from cadquery.occ_impl import shapes as S
    from OCP.TopTools import TopTools_IndexedMapOfShape
    from OCP.TopExp import TopExp
    from OCP.TopAbs import TopAbs_EDGE
    if getattr(S.Shape, '_fch_installed', False): return
    S.Shape._fch_installed = True

    def prim(cls, name, op, build):
        orig = getattr(cls, name).__func__
        def f(c, *a, **k):
            r = orig(c, *a, **k)
            try: tag(r, node(op, **build(*a, **k)))
            except Exception as e: tag(r, _baked(r, f'{op} ({e})'))
            return r
        setattr(cls, name, classmethod(f))
    V0, Z = [0.0, 0.0, 0.0], [0.0, 0.0, 1.0]
    prim(S.Solid, 'makeBox', 'box', lambda length, width, height, pnt=V0, dir=Z: dict(L=length, W=width, H=height, m=_ax2(_vec(pnt), _vec(dir))))
    prim(S.Solid, 'makeCylinder', 'cylinder', lambda radius, height, pnt=V0, dir=Z, angleDegrees=360: dict(r=radius, h=height, angle=angleDegrees, m=_ax2(_vec(pnt), _vec(dir))))
    prim(S.Solid, 'makeCone', 'cone', lambda radius1, radius2, height, pnt=V0, dir=Z, angleDegrees=360: dict(r1=radius1, r2=radius2, h=height, angle=angleDegrees, m=_ax2(_vec(pnt), _vec(dir))))
    prim(S.Solid, 'makeSphere', 'sphere', lambda radius, pnt=V0, dir=Z, angleDegrees1=0, angleDegrees2=90, angleDegrees3=360: dict(r=radius, a1=angleDegrees1, a2=angleDegrees2, a3=angleDegrees3, m=_ax2(_vec(pnt), _vec(dir))))
    prim(S.Solid, 'makeTorus', 'torus', lambda radius1, radius2, pnt=V0, dir=Z, angleDegrees1=0, angleDegrees2=360: dict(r1=radius1, r2=radius2, a1=angleDegrees1, a2=angleDegrees2, m=_ax2(_vec(pnt), _vec(dir))))

    def opaque(cls, name, what=None):                                         # shapes we cannot replay: kept exact
        raw = cls.__dict__[name]
        orig = raw.__func__ if isinstance(raw, (classmethod, staticmethod)) else raw
        kind = type(raw)
        def f(*a, **k):
            r = orig(*a, **k)
            try:
                if isinstance(r, S.Shape) and getattr(r, ATTR, None) is None:
                    ins = [nid(x) for x in a if isinstance(x, S.Shape) and getattr(x, ATTR, None) is not None][:1] if kind is not staticmethod else []
                    tag(r, _baked(r, what or name, ins))
            except Exception: pass
            return r
        setattr(cls, name, kind(f) if kind in (classmethod, staticmethod) else f)
    for cls, names in ((S.Solid, ('extrudeLinear', 'revolve', 'sweep', 'loft', 'extrudeLinearWithRotation', 'sweep_multi', 'makeWedge')),
                       (S.Compound, ('makeText',)), (S.Shape, ('split', 'scale', 'transformGeometry'))):
        for n in names:
            if n in cls.__dict__: opaque(cls, n)

    def boolean(cls, name, op):
        orig = cls.__dict__[name]
        def f(self, *others, **k):
            r = orig(self, *others, **k)
            try: tag(r, node(op, [nid(self)] + [nid(o) for o in others]))
            except Exception: pass
            return r
        setattr(cls, name, f)
    for cls in (S.Shape, S.Compound):
        for name, op in (('cut', 'cut'), ('fuse', 'fuse'), ('intersect', 'common')):
            if name in cls.__dict__: boolean(cls, name, op)

    def unary(name, build):
        orig = S.Shape.__dict__[name]
        def f(self, *a, **k):
            r = orig(self, *a, **k)
            try:
                if r is not self: tag(r, build(self, r, *a, **k))
            except Exception as e:
                tag(r, _baked(r, f'{name} ({e})', [nid(self)]))
            return r
        setattr(S.Shape, name, f)
    from OCP.gp import gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir, gp_Vec
    def _translate(self, r, v):
        t = gp_Trsf(); t.SetTranslation(gp_Vec(*_vec(v))); return node('xform', [nid(self)], m=_trsf(t))
    def _rotate(self, r, a, b, ang):
        a, b = _vec(a), _vec(b); t = gp_Trsf()
        t.SetRotation(gp_Ax1(gp_Pnt(*a), gp_Dir(*(b[i] - a[i] for i in range(3)))), math.radians(ang)); return node('xform', [nid(self)], m=_trsf(t))
    def _moved(self, r, loc, *a, **k):
        if not hasattr(loc, 'wrapped'): return _baked(r, 'moved (many)', [nid(self)])
        return node('xform', [nid(self)], m=_trsf(loc.wrapped.Transformation()))
    def _tshape(self, r, M):
        m = [[M.wrapped.Value(i, j) for j in range(1, 5)] for i in range(1, 4)]
        return node('xform', [nid(self)], m=m) if _rigid(m) else _baked(r, 'transformShape (not rigid)', [nid(self)])
    def _mirror(self, r, plane='XY', base=(0, 0, 0)):
        nrm = {'XY': (0, 0, 1), 'YX': (0, 0, 1), 'XZ': (0, 1, 0), 'ZX': (0, 1, 0), 'YZ': (1, 0, 0), 'ZY': (1, 0, 0)}.get(plane) if isinstance(plane, str) else _vec(plane)
        return node('mirror', [nid(self)], normal=list(map(float, nrm)), base=_vec(base))
    unary('translate', _translate); unary('rotate', _rotate); unary('moved', _moved); unary('located', _moved)
    unary('transformShape', _tshape); unary('mirror', _mirror)
    unary('clean', lambda self, r: node('refine', [nid(self)]))
    for n in ('copy', 'fix'):                                                  # same geometry: same history
        unary(n, lambda self, r, *a, **k: nid(self))

    def solids_(orig):
        def f(self):
            out = orig(self)
            try:
                if getattr(self, ATTR, None) is not None:
                    if len(out) == 1 and isinstance(self, S.Solid): tag(out[0], nid(self))
                    else:
                        for k, s in enumerate(out): tag(s, _baked(s, f'solid {k} of', [nid(self)]))
            except Exception: pass
            return out
        return f
    S.Shape.Solids = solids_(S.Shape.__dict__['Solids'])

    def edge_refs(shape, edges):
        m = TopTools_IndexedMapOfShape(); TopExp.MapShapes_s(shape.wrapped, TopAbs_EDGE, m)
        out = []
        for e in edges:
            i = m.FindIndex(e.wrapped); c = e.Center()
            out.append(dict(i=int(i), c=[c.x, c.y, c.z], L=float(e.Length())))
        return out
    of, oc = S.Mixin3D.__dict__['fillet'], S.Mixin3D.__dict__['chamfer']
    def fillet(self, radius, edgeList):
        edgeList = list(edgeList); r = of(self, radius, edgeList)
        try: tag(r, node('fillet', [nid(self)], r=float(radius), edges=edge_refs(self, edgeList)))
        except Exception as e: tag(r, _baked(r, f'fillet ({e})', [nid(self)]))
        return r
    def chamfer(self, length, length2, edgeList):
        edgeList = list(edgeList); r = oc(self, length, length2, edgeList)
        try: tag(r, node('chamfer', [nid(self)], d=float(length), d2=float(length2 or length), edges=edge_refs(self, edgeList)))
        except Exception as e: tag(r, _baked(r, f'chamfer ({e})', [nid(self)]))
        return r
    S.Mixin3D.fillet, S.Mixin3D.chamfer = fillet, chamfer

    omc = S.Compound.__dict__['makeCompound'].__func__
    def makeCompound(c, listOfShapes):
        lst = list(listOfShapes); r = omc(c, lst)
        try: tag(r, node('compound', [nid(s) for s in lst]))
        except Exception: pass
        return r
    S.Compound.makeCompound = classmethod(makeCompound)

    # ---- files
    oib = S.Shape.__dict__['importBrep'].__func__
    def importBrep(c, f):
        r = oib(c, f)
        if isinstance(f, (str, Path)): tag(r, _load(Path(f), r))
        return r
    S.Shape.importBrep = classmethod(importBrep)
    import cadquery.occ_impl.importers as IM
    ois = IM.importStep
    def importStep(fileName, *a, **k):
        w = ois(fileName, *a, **k)
        try:
            vals = w.vals()
            if len(vals) == 1: tag(vals[0], _load(Path(fileName), vals[0]))
        except Exception: pass
        return w
    IM.importStep = importStep; cq.importers.importStep = importStep

    oeb, oes = S.Shape.__dict__['exportBrep'], S.Shape.__dict__['exportStep']; _ORIG['exportBrep'] = oeb
    def exportBrep(self, f):
        r = oeb(self, f)
        if isinstance(f, (str, Path)): _save(self, Path(f))
        return r
    def exportStep(self, fileName, **k):
        r = oes(self, fileName, **k)
        _save(self, Path(fileName)); return r
    S.Shape.exportBrep, S.Shape.exportStep = exportBrep, exportStep

    oc_ = shutil.copyfile                                                     # caches copy part files: copy their history too
    def copyfile(src, dst, *a, **k):
        r = oc_(src, dst, *a, **k)
        try:
            s = Path(str(src) + '.fch.json'); d = Path(str(dst) + '.fch.json')
            if s.exists(): oc_(s, d)
            elif d.exists(): d.unlink()
        except Exception: pass
        return r
    shutil.copyfile = copyfile

# ---------------------------------------------------------------- sidecars
def _sha(b): return hashlib.sha1(b).hexdigest()

def _blob(i):
    n = NODES[i]
    if n.get('blob'): return n['blob']
    s = SHAPES.get(i)
    if s is None and i in WEAK: s = WEAK[i]()
    if s is None: return None
    buf = io.BytesIO(); _ORIG['exportBrep'](s, buf)
    b = buf.getvalue(); h = _sha(b); BLOBS.mkdir(parents=True, exist_ok=True)
    p = BLOBS / (h + '.brep')
    if not p.exists(): p.write_bytes(b)
    n['blob'] = h; return h

def _graph(root):
    out, stack = {}, [root]
    while stack:
        i = stack.pop()
        if i in out: continue
        out[i] = NODES[i]; stack.extend(NODES[i]['inputs'])
    return out

def _save(shape, path):
    i = getattr(shape, ATTR, None)
    if i is None or i not in NODES: i = nid(shape, site='(written without history)')
    try:
        g = _graph(i)
        for k, n in g.items():
            if n['op'] == 'baked' and not n.get('blob'): _blob(k)
        data = dict(version=1, file=path.name, file_sha=_sha(path.read_bytes()), root=str(i),
                    nodes={str(k): n for k, n in g.items()})
        Path(str(path) + '.fch.json').write_text(json.dumps(data, separators=(',', ':')))
    except Exception as e:
        sys.stderr.write(f'fchist: no history for {path.name}: {e}\n')

def _load(path, shape):
    """History of a file that is read back; a file without a fresh history becomes a baked start."""
    side = Path(str(path) + '.fch.json')
    try:
        if side.exists():
            d = json.loads(side.read_text())
            if d.get('file_sha') == _sha(path.read_bytes()):
                remap = {k: _id() for k in d['nodes']}
                for k, n in d['nodes'].items():
                    n = dict(n); n['inputs'] = [remap[str(x)] for x in n['inputs']]; NODES[remap[k]] = n
                return remap[d['root']]
    except Exception as e:
        sys.stderr.write(f'fchist: could not read history of {path.name}: {e}\n')
    i = node('baked', site=f'file {path.name}', what='file', source=str(path)); SHAPES[i] = shape
    return i
