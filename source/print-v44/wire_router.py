"""V44 wire routing: a voxel router for the harness (build_v44_wires.py).

Every placed part and wall (printed variant) is voxelized from its BREP surface (0.8 mm grid, per-part cavities filled).
A wire of radius r may use a voxel when its distance to the nearest obstacle is more than r + CLEAR, and more than
r + MOVING_CLEAR from anything that turns (drum, shafts, coupling, worm, bearings, fairlead sheaves). The cheapest path
(skimage MCP, 26-connected) prefers the wiring lanes and service spaces laid out on the page (ROUTE_* / RESERVE_*),
then it is straightened: each waypoint is joined to the farthest later waypoint it can see without leaving free space.
Wires already routed become obstacles for the next one. The exact CAD check in build_v44_wires.py has the last word.
The occupancy grid is cached in .cache/wire_occ.npz, keyed by the BREP files it was made from.
"""
from pathlib import Path
import json
import numpy as np
import cadquery as cq
from scipy import ndimage
import skimage.graph as skg
import trimesh
import v44cache as VC
import back_wall as BW

HERE = Path(__file__).resolve().parent
P = 0.8                                                # grid pitch (mm)
LO = np.array([-82.0, -139.0, -2.0]); HI = np.array([292.0, 23.0, 98.0])
SHAPE = tuple(np.ceil((HI - LO) / P).astype(int))
CLEAR, MOVING_CLEAR, WIRE_GAP, GROUP_GAP, LANE_COST = 0.5, 2.0, 0.9, 0.3, 0.45
HUG = 0.8
MOVING = ('FM9_Drum', 'REF_drum_shaft', 'NBK_', 'REF_motor_output_shaft', 'KHK_', 'ServoCity_2101', 'goBILDA_2106', 'FM10_', 'SKF_',
          'Bearing_625ZZ', 'goBILDA_1601', 'goBILDA_1611', 'V27_REF_anchor', 'V21_hub', 'H_V21', 'I_V21', 'B_V21', 'V3_REF_encoder_magnet')
KEEP_OUT = ('RESERVE_fan_airspace',)                    # fan air path: no wires
LANES = ('ROUTE_', 'RESERVE_', 'TRIAL_DSI_service')

def idx(p): return tuple(np.clip(np.round((np.asarray(p, float) - LO) / P).astype(int), 0, np.array(SHAPE) - 1))
def pos(i): return LO + np.asarray(i, float) * P

def _voxelize(shape, grid, fill=True):
    """Mark the surface voxels of a shape (tessellated, subdivided below the pitch), then fill its closed cavities."""
    try: vs, fs = shape.tessellate(0.2, 0.3)
    except Exception: return
    if not fs: return
    v = np.array([[q.x, q.y, q.z] for q in vs]); f = np.array(fs)
    v, f = trimesh.remesh.subdivide_to_size(v, f, max_edge=P * 0.7, max_iter=12)
    i = np.round((v - LO) / P).astype(int)
    ok = np.all((i >= 0) & (i < np.array(SHAPE)), axis=1); i = i[ok]
    if not len(i): return
    if not fill:
        grid[i[:, 0], i[:, 1], i[:, 2]] = True; return
    a, b = i.min(0), i.max(0) + 1
    sub = np.zeros(tuple(b - a), bool); sub[tuple((i - a).T)] = True
    sub = ndimage.binary_fill_holes(sub)
    grid[a[0]:b[0], a[1]:b[1], a[2]:b[2]] |= sub

def outside_mask():
    """Everything outside the enclosure's outer skin (so a path can never leave through a grille hole or the fairlead exit)."""
    X, Y, Z = [LO[k] + np.arange(SHAPE[k]) * P for k in range(3)]
    back = np.array([BW.cover_back(x) if x < 248.0 else 20.5 for x in X])
    hood = (X >= BW.PI_HOOD['x'][0]) & (X <= BW.PI_HOOD['x'][1]) if BW.PI_HOOD else np.zeros(len(X), bool)
    m = np.zeros(SHAPE, bool)
    m[(X < -81.0) | (X > 290.0)] = True
    m[:, (Y < -137.0), :] = True
    m[:, :, (Z < 0.0) | (Z > 96.5)] = True
    yy = Y[None, :] > back[:, None]                                   # behind the back wall (per zone)
    for i in np.where(hood)[0]: yy[i] = Y > BW.PI_HOOD['y_in'] + 3.0 if BW.PI_HOOD else yy[i] # the Pi hood reaches further back (top only; walls are voxelized)
    m |= yy[:, :, None]
    return m

def load_occupancy(rev, allow_files):
    """(static obstacles, moving parts, lane voxels), cached against the BREP files."""
    parts = {n: HERE / 'printed' / (n + '.brep') for n in rev['parts'] if not n.startswith(('WIRE_', 'HARNESS_'))}
    key = VC.sha(sorted((n, VC.file_sha(f)) for n, f in parts.items()), sorted((n, VC.file_sha(f)) for n, f in allow_files.items()),
                 [P, LO.tolist(), HI.tolist(), MOVING, KEEP_OUT, LANES, 'surface+fill v1'], VC.file_sha(HERE / 'back_wall.py'))
    cf = VC.CACHE / 'wire_occ.npz'
    if VC.ENABLED and cf.exists():
        d = np.load(cf)
        if str(d['key']) == key: return d['static'], d['moving'], d['lane']
    static = np.zeros(SHAPE, bool); moving = np.zeros(SHAPE, bool); lane = np.zeros(SHAPE, bool)
    for n, f in parts.items():
        s = cq.Shape.importBrep(str(f))
        _voxelize(s, moving if n.startswith(MOVING) else static)
    for n, f in allow_files.items():
        s = cq.Shape.importBrep(str(f))
        if n.startswith(KEEP_OUT): _voxelize(s, static)
        elif n.startswith(LANES): _voxelize(s, lane)
    static |= outside_mask()
    if VC.ENABLED:
        VC.CACHE.mkdir(exist_ok=True); np.savez_compressed(cf, key=key, static=static, moving=moving, lane=lane)
    return static, moving, lane

class Router:
    def __init__(self, static, moving, lane):
        self.d_static = ndimage.distance_transform_edt(~static) * P
        self.d_moving = ndimage.distance_transform_edt(~moving) * P
        self.lane = lane
        self.wl = []                                       # wires: (group, owner, centreline voxel indices, radius); lead-outs are reserved up front

    def _d_wires(self, keep):
        """Distance to the surface of the routed wires selected by keep(group); inf where there are none."""
        sel = [(ix, r) for g, o, ix, r in self.wl if keep(g, o)]
        if not sel: return np.full(SHAPE, np.inf, np.float32)
        occ = np.zeros(SHAPE, bool); rad = np.zeros(SHAPE, np.float32)
        for ix, r in sel: occ[tuple(ix.T)] = True; rad[tuple(ix.T)] = np.maximum(rad[tuple(ix.T)], r)
        d, near = ndimage.distance_transform_edt(~occ, return_indices=True)
        return (d * P - rad[tuple(near)]).astype(np.float32)

    def free(self, r, group=None, owner=None, gap=None):
        fr = (self.d_static > r + CLEAR) & (self.d_moving > r + MOVING_CLEAR)
        fr &= self._d_wires(lambda g, o: g != group and o != owner) > r + (WIRE_GAP if gap is None else gap)
        fr &= self._d_wires(lambda g, o: g == group and o != owner) > r + GROUP_GAP        # same bundle: may lie close
        return fr

    def seg_free(self, fr, a, b, step=0.35):
        n = max(2, int(np.linalg.norm(b - a) / step) + 1)
        for t in np.linspace(0, 1, n):
            if not fr[idx(a + (b - a) * t)]: return False
        return True

    def route(self, a, b, r, group=None, owner=None, gap=None):
        """Cheapest free path a -> b for radius r, straightened. Returns a list of points (a and b exact) or raises."""
        fr = self.free(r, group, owner, gap)
        ia, ib = idx(a), idx(b)
        for p, i in ((a, ia), (b, ib)):
            if not fr[i]:
                # let the end sit in a tight spot: open a small ball around it
                lo = np.maximum(np.array(i) - 3, 0); hi = np.minimum(np.array(i) + 4, SHAPE)
                fr[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]] |= (self.d_static[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]] > r * 0.6)
        hug = 1.0 + HUG * np.clip((self.d_static - r - CLEAR) / 6.0, 0.0, 1.0)      # cheaper within ~6 mm of a surface (tied down)
        cost = np.where(fr, np.where(self.lane, LANE_COST, 1.0) * hug, np.inf)
        m = skg.MCP_Geometric(cost)
        c, _ = m.find_costs([ia], [ib])
        if not np.isfinite(c[ib]): raise RuntimeError(f'no free path for r={r} from {np.round(a,1)} to {np.round(b,1)}')
        path = [pos(q) for q in m.traceback(ib)]
        path[0] = np.asarray(a, float); path[-1] = np.asarray(b, float)
        acc = np.concatenate([[0.0], np.cumsum([np.linalg.norm(q - p) * 0.5 * (cost[idx(p)] + cost[idx(q)]) for p, q in zip(path, path[1:])])])
        out = [path[0]]; i = 0                                          # string pulling: a shortcut must stay free and cost no more
        while i < len(path) - 1:
            j = len(path) - 1
            while j > i + 1 and not (self.seg_free(fr, path[i], path[j]) and self.seg_cost(cost, path[i], path[j]) <= (acc[j] - acc[i]) * 1.02): j -= 1
            out.append(path[j]); i = j
        return out

    def seg_cost(self, cost, a, b, step=0.8):
        n = max(2, int(np.linalg.norm(b - a) / step) + 1)
        return float(np.mean([cost[idx(a + (b - a) * t)] for t in np.linspace(0, 1, n)])) * float(np.linalg.norm(b - a))

    def add(self, pts, r, group=None, owner=None, replace=False):
        """Mark a wire (centreline pts, radius r) as an obstacle for the others; replace drops the owner's reserved lead-outs."""
        if replace: self.wl = [e for e in self.wl if e[1] != owner]
        ix = []
        for a, b in zip(pts, pts[1:]):
            a, b = np.asarray(a), np.asarray(b)
            ix += [idx(a + (b - a) * t) for t in np.linspace(0, 1, max(2, int(np.linalg.norm(b - a) / (P * 0.5)) + 1))]
        self.wl.append((group, owner, np.unique(np.array(ix), axis=0), r))
