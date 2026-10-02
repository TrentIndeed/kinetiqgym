# Renders the printed drivetrain motion study to PNG frames (FCH_FRAMES_DIR/frames2), then closes FreeCAD.
# freecad.exe render_motion_video.py ; then: ffmpeg -framerate 12.5 -i frames2/f%04d.png -c:v libx264 -pix_fmt yuv420p drivetrain_motion.mp4
# Open the drivetrain motion study, run FreeCAD's simulation, save frames for a video, then loop the animation on screen.
import FreeCAD as App, FreeCADGui as Gui
from PySide import QtCore
import os
F = os.environ.get('FCH_MOTION_FILE', os.path.abspath('freecad/printed/V44_printed_drivetrain_motion.FCStd'))   # run from cad/single-cable
import os; S = os.environ.get('FCH_FRAMES_DIR', os.path.join(os.environ.get('TEMP', '.'), 'fch_motion')) + '/'; os.makedirs(S + 'frames2', exist_ok=True)
mw = Gui.getMainWindow(); mw.showMaximized()
st = dict(k=1)
def log(m): open(S + 'play2.log', 'a').write(m + '\n')
def start():
    d = App.openDocument(F); Gui.activateWorkbench('AssemblyWorkbench')
    st['asm'] = asm = d.getObject('Drivetrain'); sim = [o for o in d.Objects if o.Label.startswith('Simulation:')][0]
    v = st['v'] = Gui.getDocument(d.Name).activeView()
    for o in d.Objects:                                                     # boards over the gears: off for the video
        if o.TypeId == 'App::Link' and o.Label.startswith(('JBD_', 'TRIAL_Pi4', 'MOUNT_Pi', 'MOUNT_BMS', 'WIRE_', 'HARNESS_')): o.ViewObject.Visibility = False
    v.setViewDirection(App.Vector(-0.45, 1.0, -0.55))
    Gui.Selection.clearSelection()
    for o in asm.Group:
        if o.TypeId == 'App::Link' and o.Label.startswith(('FM9_Drum', 'FM10_', 'KHK_', 'goBILDA_2106', 'ServoCity')): Gui.Selection.addSelection(o)
    Gui.SendMsgToActiveView('ViewSelection'); Gui.Selection.clearSelection()
    mw.setWindowTitle('FreeCAD - solving the drivetrain simulation (about 3 min)...'); Gui.updateGui(); log('solving')
    QtCore.QTimer.singleShot(200, lambda: solve(asm, sim))
def solve(asm, sim):
    asm.generateSimulation(sim); st['n'] = asm.numberOfFrames(); log(f"frames {st['n']}")
    mw.setWindowTitle('FreeCAD - rendering video frames...'); QtCore.QTimer.singleShot(100, render)
def render():
    k, n = st['k'], st['n']
    if k < n:
        st['asm'].updateForFrame(k); Gui.updateGui()
        st['v'].saveImage(S + 'frames2/f%04d.png' % (k // 4), 1280, 720, 'White')
        st['k'] = k + 4; QtCore.QTimer.singleShot(1, render); return
    log('rendered'); mw.setWindowTitle('FreeCAD - drivetrain simulation (looping; close the window to stop)')
    log('playing'); QtCore.QTimer.singleShot(300, mw.close)
def play():
    st['asm'].updateForFrame(st['k']); st['k'] = st['k'] + 1 if st['k'] + 1 < st['n'] else 1
QtCore.QTimer.singleShot(2500, start)
