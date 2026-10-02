"""FreeCAD Assembly-workbench motion study of the drivetrain (run with FreeCAD's Python: ./make_freecad.sh <variant> --motion).

Writes freecad/<variant>/V44_<variant>_drivetrain_motion.FCStd: the whole machine as links, with the turning parts inside an
Assembly object that FreeCAD's own solver drives:
  - the motor body is grounded;
  - Revolute joints: drum shaft, shaft 2, worm shaft (X axes) and the carrier ring (Y axis through the 6809 pivot);
  - every part that turns with a shaft (gears, hubs, screws, drum, anchor, magnet, sheave...) is Fixed to that shaft;
  - Gears joints carry the drive: drum 60T -> shaft-2 60T, shaft-2 20T -> worm-shaft 20T (pitch radii 24 / 24, 8 / 8);
  - FreeCAD has no worm joint, so the 53T ring gets its own motion at exactly 1/53 of the drum (KHK SW0.8-R1, right hand:
    the worm turning +a about +X turns the ring +a/53 about +Y);
  - Simulation "Motor": the drum swings +-5.5 turns (sine, 8 s) so the carrier sweeps about +-37 deg inside its +-48.4 deg stops.
Open it, double-click Simulation, press Run, then Play / scrub. Change the motor formula in the Motion object.
"""
import sys, os, json, math
from pathlib import Path
FC = os.environ.get('FREECAD_BIN', r'D:/Programs/FreeCAD_1.1.4-Windows-x86_64-py311/bin')
sys.path.append(FC); sys.path.append(str(Path(FC).parent / 'Mod' / 'Assembly'))
import FreeCAD as App, Part
if not App.GuiUp:                                                           # the simulation module only imports Qt with the GUI
    import builtins
    from PySide import QtCore as _QtCore, QtGui as _QtGui
    builtins.QtCore, builtins.QtGui = _QtCore, _QtGui
import JointObject, UtilsAssembly, CommandCreateSimulation as CS

MODEL, VARIANT, OUT = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
REV = json.loads((MODEL / VARIANT / 'revision.json').read_text())
PARTS = OUT / VARIANT / 'parts'
REPORT = {r['part']: r for r in json.loads((OUT / VARIANT / 'freecad-report.json').read_text()) if r['status'] != 'failed'}

GROUND = 'REF_APS8072S_motor_body_APPROX_80x82'
SETS = {   # name: (axis point, axis direction, part-name prefixes; the first is the shaft the joints use)
    'drum': ((0.0, -62.5, 43.0), (1, 0, 0), ['REF_drum_shaft_12mm_176mm', 'REF_motor_output_shaft', 'V3_REF_encoder_magnet', 'FM9_Drum',
             'FM10_Drum_', 'H_V21_goBILDA_1301', 'B_V21_', 'I_V21_hub', 'V27_', 'I_V30_anchor', 'B_V37_anchor', 'V43_REF_Ruland']),
    'shaft2': ((0.0, -107.938, 27.528), (1, 0, 0), ['goBILDA_2106-4008-0560_REX_shaft', 'FM10_Owned_2302-0014-0060_60T_shaft-2',
               'FM10_Shaft_2_60T_hub', 'FM10_goBILDA_2303-4008-0020_20T_shaft-2']),
    'worm_shaft': ((0.0, -105.0, 11.8), (1, 0, 0), ['ServoCity_2101-0006-0060_D_shaft', 'FM10_goBILDA_2303-1006-0020_20T', 'KHK_SW0.8-R1_worm']),
    'carrier': ((135.2, 0.0, 40.0), (0, 1, 0), ['FM10_Printed_PA-CF_carrier', 'FM10_Top_sheave', 'FM10_sheave_axle', 'FM10_roller_axle', 'Bearing_625ZZ_roller']),
}
GEARS = [('drum', 'shaft2', 24.0, 24.0), ('shaft2', 'worm_shaft', 8.0, 8.0)]          # m0.8: 60T r24, 20T r8
TURNS, PERIOD, T_END, STEP = 5.5, 20.0, 20.0, 0.02                     # <= ~13 deg of drum per frame (the gear joints need small steps)
DRUM_F = f'{TURNS * 2 * math.pi:.6f}*sin({2 * math.pi / PERIOD:.6f}*time)'         # radians
RING_F = f'{TURNS * 2 * math.pi / 53:.6f}*sin({2 * math.pi / PERIOD:.6f}*time)'

def axis_plc(p, d):
    """Joint frame: origin on the axis, Z along it."""
    rot = App.Rotation(App.Vector(0, 0, 1), App.Vector(*d))
    return App.Placement(App.Vector(*p), rot)

def joint(group, asm, kind, a, b, plc_a, plc_b, label):
    j = group.newObject('App::FeaturePython', label)
    JointObject.Joint(j, JointObject.JointTypes.index(kind))
    j.Label = label
    j.Reference1 = [a, ['Vertex1', 'Vertex1']]; j.Reference2 = [b, ['Vertex1', 'Vertex1']]   # the part itself (not an assembly path)
    j.Detach1 = j.Detach2 = True                                           # keep our frames: on the axes, not on picked faces
    j.Placement1 = a.Placement.inverse().multiply(plc_a)                   # frames are local to each part
    j.Placement2 = b.Placement.inverse().multiply(plc_b)
    return j

def build():
    doc = App.newDocument(f'V44_{VARIANT}_motion'); doc.Label = f'V44 {VARIANT} drivetrain motion'
    path = str(OUT / VARIANT / f'V44_{VARIANT}_drivetrain_motion.FCStd'); doc.saveAs(path)
    asm = doc.addObject('Assembly::AssemblyObject', 'Drivetrain'); asm.Label = 'Drivetrain (motion)'
    jg = asm.newObject('Assembly::JointGroup', 'Joints')
    static = doc.addObject('App::DocumentObjectGroup', 'Static'); static.Label = 'Static parts'
    members = {k: [] for k in SETS}
    def setof(n):
        for k, (_, _, pre) in SETS.items():
            if n.startswith(tuple(pre)): return k
    def link(n, into):
        p = App.openDocument(str(PARTS / (n + '.FCStd')), hidden=True)
        ln = (asm.newObject if into is asm else doc.addObject)('App::Link', 'L'); ln.setLink(p.getObject(REPORT[n]['tip']))
        ln.Label = n; ln.LinkTransform = True
        if into is not asm: into.addObject(ln)
        return ln
    ground = None
    for n in REPORT:
        k = setof(n)
        if n == GROUND: ground = link(n, asm)
        elif k: members[k].append(link(n, asm))
        else: link(n, static)
    g = jg.newObject('App::FeaturePython', 'Ground'); JointObject.GroundedJoint(g, ground); g.Label = 'Ground: motor body'
    shafts = {}
    for k, (p, d, pre) in SETS.items():
        lst = sorted(members[k], key=lambda l: 0 if l.Label.startswith(pre[0]) else 1)
        shafts[k] = lst[0]; A = axis_plc(p, d)
        joint(jg, asm, 'Revolute', ground, lst[0], A, A, f'Revolute: {k}')
        for o in lst[1:]: joint(jg, asm, 'Fixed', lst[0], o, A, A, f'Fixed: {o.Label[:40]} on {k}')
    for a, b, ra, rb in GEARS:
        j = joint(jg, asm, 'Gears', shafts[a], shafts[b], axis_plc(*SETS[a][:2]), axis_plc(*SETS[b][:2]), f'Gears: {a} -> {b}')
        j.Distance, j.Distance2 = ra, rb
    s = UtilsAssembly.getSimulationGroup(asm).newObject('App::FeaturePython', 'Simulation'); CS.Simulation(s); s.Label = 'Simulation: motor'
    s.aTimeStart, s.bTimeEnd, s.cTimeStepOutput = 0.0, T_END, STEP
    s.fGlobalErrorTolerance = 1e-6
    if hasattr(s, 'jFramesPerSecond'): s.jFramesPerSecond = 25
    rev = {j.Label.split(': ')[1]: j for j in jg.Group if j.Label.startswith('Revolute')}
    for jn, f, lab in (('drum', DRUM_F, 'Motor: drum shaft'), ('carrier', RING_F, 'Worm drive: carrier ring (1/53 of the drum)')):
        m = asm.newObject('App::FeaturePython', 'Motion'); CS.Motion(m, 'Angular', rev[jn], f); m.Label = lab
        s.Group = s.Group + [m]
    if App.GuiUp:                                                           # view providers: joint markers, simulation panel
        for j in jg.Group:
            (JointObject.ViewProviderGroundedJoint if hasattr(j, 'ObjectToGround') else JointObject.ViewProviderJoint)(j.ViewObject)
        CS.ViewProviderSimulation(s.ViewObject)
        for m in s.Group: CS.ViewProviderMotion(m.ViewObject)
    doc.recompute(); doc.save()
    return doc, asm, s, shafts, path

def check(asm, s, shafts):
    """Run the simulation headless and read each shaft's turn at a few frames."""
    asm.generateSimulation(s); n = asm.numberOfFrames(); out = []
    for k in (0, n // 8, n // 4):
        asm.updateForFrame(k); t = max(k - 1, 0) * STEP                    # frame 0 is the start pose
        row = dict(frame=k, t=round(t, 2), drum_expected=round(math.degrees(TURNS * 2 * math.pi * math.sin(2 * math.pi / PERIOD * t)), 2))
        for name, l in shafts.items():
            r = l.Placement.Rotation; row[name] = round(math.degrees(r.Angle) * (1 if r.Axis.dot(App.Vector(*SETS[name][1])) >= 0 else -1), 2)
        out.append(row)
    return n, out

if __name__ == '__main__':
    doc, asm, s, shafts, path = build()
    print('built', path, 'objects', len(doc.Objects))
    if '--check' in sys.argv:
        n, rows = check(asm, s, shafts); print('frames', n)
        for r in rows: print(r)
