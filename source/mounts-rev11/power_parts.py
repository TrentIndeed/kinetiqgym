"""V44 fix list round 7: real power-path parts, placed once and shared by build_mounts.py (page) and swap_real_cad.py (V44).

- (dropped in round 7b: the packs' EC5 plugs are the service disconnect; plug in with the BMS off) XT90-S anti-spark pair: AMASS XT90S-F (GrabCAD) + XT90H-M (vendor STEPs), mated along X. The female's
  front shell slides about 11.5 mm into the male shroud (both halves measured from their STEPs), so the mated pair is ~41 mm long.
- WAGO 221-615 5-port lever nut (P- junction): WAGO's CAD is portal-gated, so it is a box from its datasheet size
  (36.7 W x 10.1 H x 21.1 D mm) with the five lever tops.
- AMASS XT60E-F charge port: Marathon OS STEP scaled by 2/3 (the file is 1.5x oversize; see supplier-cad/amass-xt60e-f/README.md).
  Flange (34 x 15.8 x 3) sits in a pocket of the rear I/O panel, flush with the back step face (Y 20.5); body behind it.
- Printed junction bracket: holds the WAGO against the rear plate above the fuse holder, 2 x M3 into
  rear-plate inserts.
World frame: X along the shaft (motor at -X), -Y front, Z up, base plate top Z 0."""
from pathlib import Path
import numpy as np
import cadquery as cq

SC = Path(__file__).resolve().parent.parent / 'supplier-cad'

def _load(p):
    return cq.Compound.makeCompound(cq.importers.importStep(str(p)).vals())

def _rot(shape, R, t):
    """Apply a proper 3x3 rotation R (world = R @ local) then translate by t."""
    from OCP.gp import gp_Trsf
    R = np.asarray(R, float); tr = gp_Trsf()
    tr.SetValues(*R[0], float(t[0]), *R[1], float(t[1]), *R[2], float(t[2]))
    return shape.moved(cq.Location(tr))

def box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))

# ---- placement (rev 12 world) ----
XT90_X0, XT90_YC, XT90_ZC = 136.5, -13.0, 36.0   # pair runs X 142.1..183.1 (male solder end at -X)
WAGO = (190.4, 200.5, -24.5, -3.4, 30.5, 67.2)   # round 11: upright right beside the fan again (clear of the rack mount); levers face -X   # X, Y (21.1 deep), Z (10.1 tall)
BRACKET = dict(x=(183.2, 200.4), y=(-1.6, 2.45), z=(28.9, 68.0))
BRACKET_SCREWS = [(186.0, 34.0), (186.0, 63.0)]  # (X, Z) M3 into rear-plate inserts
XT60 = dict(x=268.0, z=72.8, face_y=20.5, pocket=(16.2, 34.4), body=(11.4, 18.9), screw_dz=12.49)

def xt90_pair():
    m = _load(SC / 'amass-xt90h-m/XT90H-M SBORKA PART.STEP')          # axis z, mating end z 31.8, solder end z 5.6
    f = _load(SC / 'amass-xt90s/AMASS_XT90S-F_grabcad.stp')            # axis y, mating end y 0, solder end y 26.3
    Rm = [[0, 0, 1], [0, 1, 0], [-1, 0, 0]]                             # male z -> X, y -> Y, x -> -Z
    Rf = [[0, 1, 0], [1, 0, 0], [0, 0, -1]]                             # female y -> X, x -> Y, z -> -Z
    male = _rot(m, Rm, (XT90_X0, XT90_YC + 0.5, XT90_ZC - 0.32))
    fem = _rot(f, Rf, (XT90_X0 + 31.8 - 11.5, XT90_YC, XT90_ZC))
    return male, fem

def wago():
    """Upright: 36.7 long along Z, 21.1 deep along Y (wire entries on the -Y face), 10.1 thick along X, lever tops on the -X face."""
    x0, x1, y0, y1, z0, z1 = WAGO
    body = box(x0 + 1.5, x1, y0, y1, z0, z1)
    pitch = (z1 - z0) / 5
    for i in range(5):
        body = body.fuse(box(x0, x0 + 1.5, y0 + 1.0, y0 + 13.0, z0 + i * pitch + 0.8, z0 + (i + 1) * pitch - 0.8))
    return body

def bracket():
    """Back plate on the rear plate + a shelf under the upright WAGO; cable ties through two shelf slots and round the WAGO."""
    (x0, x1), (y0, y1), (z0, z1) = BRACKET['x'], BRACKET['y'], BRACKET['z']
    wx0, wx1, wy0, wy1 = WAGO[:4]
    s = box(x0, x1, y0, y1, z0, z1).fuse(box(wx0 - 1.0, x1, wy0 - 1.0, y0 + 0.01, z0, 30.4))   # shelf under the WAGO (bottom Z 30.5)
    for y in (wy0 + 4.0, wy1 - 4.0):                                                          # cable-tie slots through the shelf
        s = s.cut(box(wx0 + 1.0, wx1 - 1.0, y - 1.5, y + 1.5, z0 - 0.1, 30.5))
    for x, z in BRACKET_SCREWS:
        s = s.cut(cq.Solid.makeCylinder(1.7, y1 - y0 + 0.2, cq.Vector(x, y0 - 0.1, z), cq.Vector(0, 1, 0)))
    return s

# Littelfuse holder (manufacturer STEP) + BF1 40 A fuse on two printed cradles; round 11: under the fan and the WAGO
FUSE_C = (215.0, -11.5, 4.5)                     # holder base centre (studs at X 200 / 230, Y -11.5); holder X 193.5..236.5
CRADLES_X = (195.0, 230.0)                       # 5 mm cradles under the holder body ends

def fuse_holder():
    hs = cq.importers.importStep(str(SC / 'littelfuse-04980921gxm5/OL-04980921GXM5.step')).vals()
    holder = max(cq.Compound.makeCompound(hs).Solids(), key=lambda q: q.Volume())
    holder = holder.translate(cq.Vector(FUSE_C[0] - 13.5, FUSE_C[1] - 22.0, FUSE_C[2] - 22.94))   # vendor: studs (-1.5 / 28.5, 22.0), base Z 22.94
    fu = cq.importers.importStep(str(SC / 'littelfuse-142.5631-bf1-58v/3D_model_BF1_142.5631.0000_BF1_58v_M5_0.4mm.stp')).val()
    fb = fu.BoundingBox()
    fu = fu.translate(cq.Vector(FUSE_C[0] - (fb.xmin + fb.xmax) / 2, FUSE_C[1] - (fb.ymin + fb.ymax) / 2, FUSE_C[2] + 6.1 - fb.zmin))
    return holder, fu

def cradles():
    s = None
    for x in CRADLES_X:
        c = box(x, x + 5, FUSE_C[1] - 11.0, FUSE_C[1] + 11.0, 0.5, 14.5).cut(box(x - .1, x + 5.1, FUSE_C[1] - 9.7, FUSE_C[1] + 9.7, 4.3, 14.6)) \
            .cut(box(x - .1, x + 5.1, FUSE_C[1] - 12, FUSE_C[1] + 12, 8, 10))
        s = c if s is None else s.fuse(c)
    return s

def xt60ef():
    c = _load(SC / 'amass-xt60e-f/Amass_XT60E-F.step')                  # flange top z 0, body to z -20.2; x = 34 long axis
    R = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]                               # y -> X, z -> Y, x -> Z
    return _rot(c, R, (XT60['x'], XT60['face_y'], XT60['z']))

def bboxes(shape):
    return [(s.BoundingBox().xmin, s.BoundingBox().xmax, s.BoundingBox().ymin, s.BoundingBox().ymax, s.BoundingBox().zmin, s.BoundingBox().zmax)
            for s in shape.Solids()]
