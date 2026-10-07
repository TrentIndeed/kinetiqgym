"""V44 round 13 (fix-list V3): print-fit coupons. Print these first, in the same material and settings as the real parts, and
tune before printing the big pieces. Writes fit-coupons/*.step + *.stl.

1. inserts   - heat-set pockets (Ruthex RX) M2.5 3.6 / M3 4.0 / M4 5.6 at -0.15 / nominal / +0.15, depth L + 1, 0.5 mm lead-in.
               Press an insert into each; use the size that goes in straight and holds a torqued screw.
2. clearance - printed clearance holes M2.5 2.9 / M3 3.6 / M4 4.7 and the 5.2 pulley-axle hole, at -0.2 / nominal / +0.2.
               The screw (or the 5 mm shoulder) should slide through the nominal hole without forcing.
3. battery   - a 10 mm slice of the battery saddle tunnel (pack 39 + 0.5 per side = 40.0, 1.5 mm 45 deg lead-in, 1 mm foam
               gap on top). Slide a real TP2700 pack through it, both ways.
4. pulleys   - the exit pulley axle spacing: two 5.2 holes 21.13 mm apart in a plate with the carrier walls 11 mm apart.
               Fit the two U625ZZ on M5 shoulder bolts with 2 mm spacers and pull the cable through: it must run in both grooves.
5. seat6809  - the 6809 bearing seat of the square back plate (d58.0, 7 deep, 2 mm lip): the bearing should press in by hand.
Numbers match build_v44_fasteners.py (INSERTS / CLEAR), mounts-rev11/build_mounts.py (saddles) and the fairlead module (exit).
"""
from pathlib import Path
import cadquery as cq

H = Path(__file__).resolve().parent
OUT = H / 'fit-coupons'; OUT.mkdir(exist_ok=True)
V = cq.Vector
def box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
def zcyl(r, x, y, z0, z1): return cq.Solid.makeCylinder(r, z1 - z0, V(x, y, z0), V(0, 0, 1))
def label(text, x, y, z, size=3.0):
    return cq.Workplane('XY', origin=(x, y, z)).text(text, size, -0.6, halign='center', valign='center').val()   # engraved 0.6

def inserts():
    rows = [(2.5, 3.6, 4.0, 4.0), (3, 4.0, 4.0, 4.6), (4, 5.6, 4.0, 6.3)]                # size, pocket, insert L, insert OD
    pitch, T = 13.0, 7.0
    s = box(0, 3 * pitch + 6, 0, len(rows) * pitch + 4, 0, T)
    for j, (d, hole, L, od) in enumerate(rows):
        y = 8 + j * pitch
        s = s.cut(label(f'M{d:g}', 4.5, y, T, 2.6))
        for i, dd in enumerate((-0.15, 0.0, 0.15)):
            x = 13 + i * pitch; h = hole + dd
            s = s.cut(zcyl(h / 2, x, y, T - (L + 1), T + 0.1)).cut(cq.Solid.makeCone(h / 2 + 0.25, h / 2, 0.5, V(x, y, T - 0.5), V(0, 0, 1)))
            s = s.cut(zcyl(h / 2 - 0.4, x, y, -0.1, T))                                   # vent / push-out hole below
    for i, dd in enumerate(('-.15', '0', '+.15')):
        s = s.cut(label(dd, 13 + i * pitch, 2.2, T, 2.2))
    return s

def clearance():
    rows = [('M2.5', 2.9), ('M3', 3.6), ('M4', 4.7), ('axle5', 5.2)]
    pitch, T = 11.0, 4.0
    s = box(0, 3 * pitch + 14, 0, len(rows) * pitch + 4, 0, T)
    for j, (n, hole) in enumerate(rows):
        y = 7 + j * pitch
        s = s.cut(label(n, 6, y, T, 2.2))
        for i, dd in enumerate((-0.2, 0.0, 0.2)):
            s = s.cut(zcyl((hole + dd) / 2, 18 + i * pitch, y, -0.1, T + 0.1))
    return s

def battery():
    """Saddle slice, printed standing (tunnel axis vertical): inner 40.0 x 69.0 (pack 39 x 68 + 1 mm foam), walls 2.5, lead-in."""
    W_IN, H_IN, WALL, LEN, LEAD = 40.0, 69.0, 2.5, 10.0, 1.5
    s = box(-W_IN / 2 - WALL, W_IN / 2 + WALL, -WALL, H_IN + WALL, 0, LEN).cut(box(-W_IN / 2, W_IN / 2, 0, H_IN, -0.1, LEN + 0.1))
    for sx in (-1, 1):                                                                    # 45 deg lead-in on the entry edges
        tri = cq.Workplane('XZ', origin=(0, H_IN + 0.1, 0)).polyline([(sx * W_IN / 2, LEN - LEAD), (sx * W_IN / 2, LEN + 0.1), (sx * (W_IN / 2 + LEAD + 0.1), LEN + 0.1)]).close().extrude(H_IN + 0.2).val()
        s = s.cut(tri)
    top = cq.Workplane('YZ', origin=(-W_IN / 2 - WALL - 0.1, 0, 0)).polyline([(H_IN - 0.1, LEN - LEAD), (H_IN - 0.1, LEN + 0.1), (H_IN + LEAD + 0.1, LEN + 0.1)]).close().extrude(W_IN + 2 * WALL + 0.2).val()
    return s.cut(top).cut(label('BATT 40.0', 0, -WALL / 2 - 0.0, LEN, 1.6).rotate(V(0, -WALL / 2, LEN), V(1, -WALL / 2, LEN), 0))

def pulleys():
    """Two 5.2 axle holes 21.13 apart through two walls 11 apart (as in the exit ring carrier); U-shaped so the cable passes."""
    AX = 21.13; WALL_T = 6.0; GAP = 11.0; R = 14.0
    s = box(-R, R, 0, 2 * WALL_T + GAP, -R - AX / 2, R + AX / 2)
    s = s.cut(box(-R - 1, R + 1, WALL_T, WALL_T + GAP, -R - AX / 2 + 3, R + AX / 2 - 3))      # pulley cavity between the walls
    for z in (-AX / 2, AX / 2):
        s = s.cut(cq.Solid.makeCylinder(2.6, 2 * WALL_T + GAP + 2, V(0, -1, z), V(0, 1, 0)))
    s = s.cut(box(-2.5, 2.5, -1, 2 * WALL_T + GAP + 1, -3, 3))                              # cable window along the axis
    return s

def seat6809():
    """Ring with the 6809 seat: d58.0 x 7 deep, 2 mm lip (d50 opening), 3 mm wall."""
    return zcyl(32.0, 0, 0, 0, 9.0).cut(zcyl(29.0, 0, 0, 2.0, 9.1)).cut(zcyl(25.0, 0, 0, -0.1, 2.1))

for name, fn in (('01_inserts_M2.5_M3_M4', inserts), ('02_clearance_holes', clearance), ('03_battery_slide_slice', battery),
                 ('04_exit_pulley_axles_21.13', pulleys), ('05_6809_bearing_seat', seat6809)):
    s = fn()
    cq.exporters.export(cq.Workplane().add(s), str(OUT / (name + '.step')))
    cq.exporters.export(cq.Workplane().add(s), str(OUT / (name + '.stl')), tolerance=0.02, angularTolerance=0.1)
    b = s.BoundingBox(); print(name, round(b.xlen, 1), round(b.ylen, 1), round(b.zlen, 1), 'valid', s.isValid())
(OUT / 'README.md').write_text('# V44 print-fit coupons\n\n' + __doc__.split('\n', 2)[2])
