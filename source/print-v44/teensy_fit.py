"""V44 W7: the Teensy 4.0 supplier CAD on its perfboard. Run after mock_models.py, before build_v44_fasteners.py (both variants).

The demo's Teensy is a drawn block: the KiCad Teensy 4.0 model (rectangular-body-study/vendor/teensy40.brep) never matched the
drawing-based mesh, so phase 1 kept the block. Here the vendor board is placed by rule on the block's perfboard:
  - USB end up (+Z), 2 mm below the perfboard top; components toward +Y; centred on the perfboard in X;
  - on 2 x 14-pin 2.54 mm socket headers (both long edges), the micro-USB receptacle centred on the right-angle plug mock.
Real header rows run the full length of both long edges, right where the 4 corner screws of the perfboard were (their heads sat
0.5 mm inside the Teensy outline). There is no room to grow the perfboard (regulator 2.6 mm below, CAN board 2 mm to the side),
so the perfboard takes 2 screws on the centreline between the header rows (12.7 mm channel, head 2.3 mm under the Teensy):
the standoffs move there and the plate's old corner holes are filled. Idempotent: everything is placed from the perfboard.
"""
from pathlib import Path
import json, sys
import cadquery as cq
from OCP.gp import gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform

H = Path(__file__).resolve().parent
VEND = H.parent / 'rectangular-body-study/vendor/teensy40.brep'
V = cq.Vector
SOCKET = 4.85                      # perfboard face to Teensy underside (2.54 mm socket headers); puts the USB on the plug mock
USB_DROP = 2.0                     # receptacle top below the perfboard top
PITCH, ROWS = 2.54, 15.24          # header pitch, row spacing (0.6 in)
SCREW_IN = 6.0                     # centreline screws: this far in from the PCB ends
PLUG_R = 2.4                       # fill for the old M2.5 insert holes (3.6 + lead-in)
N_T, N_S, N_P = 'TRIAL_Teensy', 'MOUNT_Teensy_perfboard_standoffs', 'MOUNT_front_board_plate_printed'

def box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
def ycyl(r, x, z, y0, y1): return cq.Solid.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))
def thin(s): return [q for q in s.Solids() if q.BoundingBox().ylen < 2.2 and q.Volume() > 300]

vend = cq.Shape.importBrep(str(VEND))
vb = vend.BoundingBox()
pcb_v = max(vend.Solids(), key=lambda q: q.Volume()).BoundingBox()             # vendor PCB: X long, Y thickness (+Y components), Z width

def fit(variant):
    d = H / variant; r = json.loads((d / 'revision.json').read_text())
    if N_T not in r['parts']: return None
    old = cq.Shape.importBrep(str(d / (N_T + '.brep')))
    perf = max(thin(old), key=lambda q: q.Volume())                               # the perfboard (the old PCB block is the smaller one)
    pb = perf.BoundingBox(); cx = (pb.xmin + pb.xmax) / 2
    # world = (zv + tx, yv + ty, -xv + tz): USB (vendor -X end) up
    tx = cx - (pcb_v.zmin + pcb_v.zmax) / 2
    ty = pb.ymax + SOCKET - pcb_v.ymin
    tz = pb.zmax - USB_DROP + vb.xmin
    T = gp_Trsf(); T.SetValues(0, 0, 1, tx, 0, 1, 0, ty, -1, 0, 0, tz)
    board = cq.Shape.cast(BRepBuilderAPI_Transform(vend.wrapped, T, True).Shape())
    fch = sys.modules.get('fchist_rec')                                    # FreeCAD history (FCHIST=1): record the move
    if fch: fch.tag_xform(board, vend, [[0, 0, 1, tx], [0, 1, 0, ty], [-1, 0, 0, tz]])
    z0, z1 = tz - pcb_v.xmax, tz - pcb_v.xmin                                    # PCB ends (world Z)
    n = round((z1 - z0) / PITCH); zs = (z0 + z1) / 2 - n * PITCH / 2
    sockets = [box(cx + s * ROWS / 2 - PITCH / 2, cx + s * ROWS / 2 + PITCH / 2, pb.ymax, pb.ymax + SOCKET, zs, zs + n * PITCH) for s in (-1, 1)]
    teensy = cq.Compound.makeCompound([board, *sockets, perf])
    teensy.exportBrep(str(d / (N_T + '.brep'))); teensy.exportStep(str(d / (N_T + '.step')))

    # standoffs: same piece, now 2 on the centreline
    so = cq.Shape.importBrep(str(d / (N_S + '.brep'))).Solids()
    tpl = so[0]; tb = tpl.BoundingBox(); tc = ((tb.xmin + tb.xmax) / 2, (tb.zmin + tb.zmax) / 2)
    new_axes = [(cx, z0 + SCREW_IN), (cx, z1 - SCREW_IN)]
    old_axes = [((q.BoundingBox().xmin + q.BoundingBox().xmax) / 2, (q.BoundingBox().zmin + q.BoundingBox().zmax) / 2) for q in so]
    stand = cq.Compound.makeCompound([tpl.translate(V(x - tc[0], 0, z - tc[1])) for x, z in new_axes])
    stand.exportBrep(str(d / (N_S + '.brep'))); stand.exportStep(str(d / (N_S + '.step')))

    # plate: fill the old holes that no standoff uses any more
    filled = []
    if N_P in r['parts']:
        plate = cq.Shape.importBrep(str(d / (N_P + '.brep')))
        for x, z in old_axes:
            if min(abs(x - a) + abs(z - b) for a, b in new_axes) < 0.5: continue
            ring = plate.intersect(ycyl(PLUG_R + 1.0, x, z, -400, 400)).BoundingBox()  # plate material around the hole
            plate = plate.fuse(ycyl(PLUG_R, x, z, ring.ymin, ring.ymax)); filled.append((round(x, 2), round(z, 2)))
        plate = plate.clean()
        plate.exportBrep(str(d / (N_P + '.brep'))); plate.exportStep(str(d / (N_P + '.step')))

    m = r['meta'][N_T]
    m['source'] = 'CAD: vendor teensy40.brep (KiCad Teensy library) placed by rule + 2 x 14-pin socket headers + perfboard footprint from the demo'
    m['note'] = ('Teensy 4.0 (supplier CAD) on 2 x 14-pin 2.54 mm socket headers, %.2f mm off a 1.6 mm perfboard; USB up, micro-USB on the '
                 'right-angle plug. Perfboard: 2 x M2.5 on the centreline between the header rows (head under the Teensy - fit the '
                 'perfboard before plugging the Teensy in). Cut the VIN-VUSB pad.' % SOCKET)
    r['meta'][N_S]['note'] = '2 standoffs on the Teensy centreline (W7: corner screws would sit under the header rows).'
    (d / 'revision.json').write_text(json.dumps(r, indent=1))
    bb = board.BoundingBox()
    return dict(board=[round(v, 2) for v in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)], pcb_z=(round(z0, 2), round(z1, 2)),
                screws=[(round(x, 2), round(z, 2)) for x, z in new_axes], filled=filled)

if __name__ == '__main__':
    rep = {v: fit(v) for v in ('printed', 'cnc')}
    for v, x in rep.items(): print(v, x)
    (H / 'teensy-fit.json').write_text(json.dumps(rep, indent=1))
