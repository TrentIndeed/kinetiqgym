# Release images from the FreeCAD assembly (run inside the FreeCAD GUI): freecad.exe render_images.py
# env: FCH_ASM = assembly .FCStd, FCH_IMG = output folder. Writes hero.png (closed), inside.png (covers hidden), back.png.
import os
import FreeCAD as App, FreeCADGui as Gui
from PySide import QtCore
ASM, IMG = os.environ['FCH_ASM'], os.environ['FCH_IMG']
os.makedirs(IMG, exist_ok=True)
mw = Gui.getMainWindow(); mw.showMaximized()
COVERS = ('V44_PRINT_cover', 'V44_PRINT_end_cap', 'V44_PRINT_rear_IO')
def shot(v, name, direction):
    v.setViewDirection(App.Vector(*direction)); v.fitAll(); v.zoomIn()
    v.saveImage(os.path.join(IMG, name), 2400, 1350, 'White')
def go():
    try:
        d = App.openDocument(ASM); v = Gui.getDocument(d.Name).activeView()
        Gui.SendMsgToActiveView('ViewFit')
        shot(v, 'hero.png', (-0.55, 1.0, -0.5))                                 # front three-quarter, from above
        covers = [o for o in d.Objects if o.TypeId == 'App::Link' and o.Label.startswith(COVERS)]
        for o in covers: o.ViewObject.Visibility = False
        shot(v, 'inside.png', (-0.55, 1.0, -0.65))
        for o in covers: o.ViewObject.Visibility = True
        shot(v, 'back.png', (0.6, -1.0, -0.45))                                 # rear three-quarter
    except Exception as e:
        open(os.path.join(IMG, 'render_error.txt'), 'w').write(repr(e))
    QtCore.QTimer.singleShot(300, mw.close)
QtCore.QTimer.singleShot(2500, go)
