"""Largest long-edge radius the V44 shell can use without cutting into any part or allowance.

Parts are placed as the page does (demo-placements-rev12.json). The interior is the page's box: exterior (parts + 4 mm)
minus the 3 mm wall, so the 1 mm gap stays everywhere. For each long edge (along X) and each X section, the largest
fillet radius that keeps every vertex inside the rounded interior (with the 1 mm gap) is reported. Screen parts that
sit in the front wall by design and external parts (handle) are skipped.
"""
from pathlib import Path
import gzip, json
import numpy as np

H = Path(__file__).resolve().parent; R = H.parent
ROWS = json.loads((H / 'demo-placements-rev12.json').read_text(encoding='utf-8-sig'))['rows']
MODEL = {p['name']: p for p in json.loads(gzip.decompress((R / 'workbench/public/stock-battery-fit/editor-model-tp2700.json.gz').read_bytes()))['parts']}
SKIP = ('TRIAL_base_placeholder', 'TRIAL_Waveshare_DSI_E_portrait', 'TRIAL_portrait_bezel_CONCEPT', 'TRIAL_DSI_service')

def world(row):
    p = MODEL[row['n']]; el = row['m']; A = np.array([[el[j * 4 + i] for j in range(4)] for i in range(4)])
    v = np.vstack([np.array(vis['vertices'], float).reshape(-1, 3) for vis in (p.get('visual_parts') or [p])]) - row['c']
    return v @ A[:3, :3].T + A[:3, 3]

pts = np.vstack([world(r) for r in ROWS if r['n'] in MODEL and r['n'] not in SKIP and r['g'] != 'external'])
lo = pts.min(0); hi = pts.max(0)
EXT = dict(x=(lo[0] - 4, hi[0] + 4), y=(-137.0, hi[1] + 4), z=(lo[2] - 4, hi[2] + 4))     # front set by the fairlead plate (page rule)
INT = {k: (a + 3, b - 3) for k, (a, b) in EXT.items()}
GAP = 1.0

def max_radius(yz_pts, corner, sy, sz):
    """corner: interior corner (y, z); sy, sz: +1/-1 direction from the corner into the body."""
    best = 80.0
    for Rr in np.arange(80.0, 0, -0.5):
        cy, cz = corner[0] + sy * Rr, corner[1] + sz * Rr
        m = ((yz_pts[:, 0] - cy) * sy < 0) & ((yz_pts[:, 1] - cz) * sz < 0)       # in the corner square
        d = np.hypot(yz_pts[m, 0] - cy, yz_pts[m, 1] - cz)
        if not len(d) or d.max() <= Rr - GAP: return Rr
    return 0.0

SECTIONS = {'motor end / screen (X < 95)': (-1e9, 95), 'fairlead exit (95-175)': (95, 175), 'ODrive / battery (X > 175)': (175, 1e9)}
EDGES = {'top-front': ((INT['y'][0], INT['z'][1]), 1, -1), 'top-back': ((INT['y'][1], INT['z'][1]), -1, -1),
         'bottom-front': ((INT['y'][0], INT['z'][0]), 1, 1), 'bottom-back': ((INT['y'][1], INT['z'][0]), -1, 1)}
out = dict(exterior=EXT, interior=INT, radii={})
for s, (x0, x1) in SECTIONS.items():
    sel = pts[(pts[:, 0] >= x0) & (pts[:, 0] < x1)][:, 1:]
    out['radii'][s] = {e: max_radius(sel, c, sy, sz) for e, (c, sy, sz) in EDGES.items()}
# end faces: rounding of the end-cap perimeter (edges along Y and Z at each end)
print(json.dumps(out, indent=1))
(H / 'shell-clearance.json').write_text(json.dumps(out, indent=1))
