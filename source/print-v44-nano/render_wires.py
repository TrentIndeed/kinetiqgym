"""Pictures of the harness (round 10): wires in colour over the grey parts. Writes wires-*.png."""
import json, numpy as np, pyvista as pv, cadquery as cq
from pathlib import Path
H = Path(__file__).resolve().parent
r = json.loads((H / 'printed' / 'revision.json').read_text())
def mesh(n):
    vs, fs = cq.Shape.importBrep(str(H / 'printed' / (n + '.brep'))).tessellate(0.3, 0.4)
    v = np.array([[q.x, q.y, q.z] for q in vs]); f = np.hstack([[3, *t] for t in fs])
    return pv.PolyData(v, f)
skip = ('V44_PRINT_cover', 'V44_PRINT_end_cap', 'S17_')
meshes = {n: mesh(n) for n in r['parts'] if not n.startswith(skip)}
for view, cam in (('iso', [(420, 260, 330), (105, -60, 40), (0, 0, 1)]), ('top', [(105, -60, 600), (105, -60, 40), (0, 1, 0)]),
                  ('back', [(105, 420, 120), (105, -60, 40), (0, 0, 1)])):
    p = pv.Plotter(off_screen=True, window_size=(1800, 1100)); p.set_background('white')
    for n, m in meshes.items():
        w = n.startswith(('WIRE_', 'HARNESS_'))
        p.add_mesh(m, color=r['colors'].get(n, (.6, .6, .6)) if w else (.78, .78, .8), opacity=1.0 if w else (0.12 if n.startswith('S01') else 0.35))
    p.camera_position = cam; p.screenshot(str(H / f'wires-{view}.png')); p.close()
print('ok')
