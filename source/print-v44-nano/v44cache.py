"""Build caches for the V44 pipeline (run_v44.sh). Everything lives in print-v44-nano/.cache/ (not committed); deleting that
folder, or running `./run_v44.sh --clean`, forces a full rebuild.

- part cache (build_v44_phase1.py): a part is rebuilt only when its page placement, its page mesh / source CAD or the phase-1
  script change; otherwise its last BREP/STEP is copied.
- memo (swap_real_cad.py): the vendor-swap results are replayed when the script and every file it read last time are unchanged.
- clash cache (chassis / structure / shell): exact intersection volumes keyed by a geometric fingerprint of both shapes, so
  only pairs involving a changed part are recomputed.
"""
from pathlib import Path
import hashlib, json, os, atexit, shutil

HERE = Path(__file__).resolve().parent
CACHE = HERE / '.cache'
ENABLED = os.environ.get('V44_NO_CACHE') != '1'

def sha(*parts):
    h = hashlib.sha1()
    for p in parts:
        h.update(p if isinstance(p, bytes) else json.dumps(p, sort_keys=True, default=str).encode())
    return h.hexdigest()

def file_sha(path):
    p = Path(path)
    return hashlib.sha1(p.read_bytes()).hexdigest() if p.exists() else 'missing'

# ---------------------------------------------------------------- part cache
PART_DIR = CACHE / 'phase1'

def part_get(name, key):
    """Return the cached record (dict) if the key matches and the files exist, else None."""
    if not ENABLED: return None
    j = PART_DIR / (name + '.json')
    if not j.exists(): return None
    rec = json.loads(j.read_text())
    if rec.get('key') != key or not (PART_DIR / (name + '.brep')).exists() or not (PART_DIR / (name + '.step')).exists(): return None
    return rec

def part_put(name, key, brep_path, step_path, rec):
    PART_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(brep_path, PART_DIR / (name + '.brep')); shutil.copyfile(step_path, PART_DIR / (name + '.step'))
    (PART_DIR / (name + '.json')).write_text(json.dumps(dict(rec, key=key)))

def part_restore(name, dest_dirs):
    for d in dest_dirs:
        shutil.copyfile(PART_DIR / (name + '.brep'), Path(d) / (name + '.brep'))
        shutil.copyfile(PART_DIR / (name + '.step'), Path(d) / (name + '.step'))

# ---------------------------------------------------------------- memo with recorded file dependencies
class Memo:
    """Records every file read (through the patched cadquery importers) while computing; on the next run the result is
    replayed if the script and all recorded files are unchanged."""
    def __init__(self, tag, script_path):
        self.dir = CACHE / tag; self.meta = self.dir / 'meta.json'; self.script = file_sha(script_path); self.deps = set()

    def hit(self):
        if not ENABLED or not self.meta.exists(): return None
        m = json.loads(self.meta.read_text())
        if m.get('script') != self.script: return None
        for path, h in m['deps'].items():
            if file_sha(path) != h: return None
        return m

    def record(self):
        import cadquery as cq
        orig_brep, orig_step = cq.Shape.importBrep, cq.importers.importStep
        deps = self.deps
        def importBrep(path, *a, **k):
            deps.add(str(Path(path).resolve())); return orig_brep(path, *a, **k)
        def importStep(path, *a, **k):
            deps.add(str(Path(path).resolve())); return orig_step(path, *a, **k)
        cq.Shape.importBrep = staticmethod(importBrep)
        cq.importers.importStep = importStep

    def save(self, payload):
        self.dir.mkdir(parents=True, exist_ok=True)
        self.meta.write_text(json.dumps(dict(script=self.script, deps={p: file_sha(p) for p in sorted(self.deps)}, **payload)))

# ---------------------------------------------------------------- clash cache
CLASH_FILE = CACHE / 'clash.json'
_clash = None

def _load():
    global _clash
    if _clash is None:
        _clash = json.loads(CLASH_FILE.read_text()) if (ENABLED and CLASH_FILE.exists()) else {}
        atexit.register(_save)
    return _clash

def _save():
    if _clash is not None and ENABLED:
        CACHE.mkdir(parents=True, exist_ok=True); CLASH_FILE.write_text(json.dumps(_clash))

_fp_memo = {}
def fingerprint(shape):
    """Geometric fingerprint: volume, area, bounding box, face and edge counts (rounded)."""
    k = id(shape)
    if k in _fp_memo and _fp_memo[k][0] is shape: return _fp_memo[k][1]
    b = shape.BoundingBox()
    fp = sha([round(shape.Volume(), 2), round(shape.Area(), 1), [round(v, 2) for v in (b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax)],
              len(shape.Faces()), len(shape.Edges())])
    _fp_memo[k] = (shape, fp)
    return fp

def clash_volume(s, t):
    """Exact intersection volume of two shapes, cached by the fingerprints of both (order-independent)."""
    c = _load(); a, b = fingerprint(s), fingerprint(t); key = a + b if a < b else b + a
    if key in c: return c[key]
    try: v = s.intersect(t).Volume()
    except Exception: v = -1.0
    c[key] = v
    return v
