# Runs motion.py inside the FreeCAD GUI (so the Simulation and joints get their view providers), then closes FreeCAD.
# usage: freecad.exe motion_gui.py   with env FCH_MODEL, FCH_VARIANT, FCH_OUT
import os, sys, runpy, traceback
import FreeCAD as App, FreeCADGui as Gui
from PySide import QtCore
HERE = os.environ['FCH_HERE']
def go():
    log = open(os.path.join(HERE, 'motion_gui.log'), 'a')
    try:
        for v in os.environ['FCH_VARIANT'].split(','):
            sys.argv = ['motion.py', os.environ['FCH_MODEL'], v, os.environ['FCH_OUT']]
            g = runpy.run_path(os.path.join(HERE, 'motion.py'), run_name='lib')
            doc, asm, s, shafts, path = g['build']()
            for o in asm.Group:
                if o.TypeId == 'Assembly::JointGroup': o.ViewObject.Visibility = False
            for o in doc.Objects:                                          # covers off so the drivetrain is in view
                if o.TypeId == 'App::Link' and o.Label.startswith(('V44_PRINT_cover', 'V44_PRINT_end_cap', 'V44_PRINT_rear_IO')):
                    o.ViewObject.Visibility = False
            doc.save(); log.write(f'{v}: built {path}, {len(doc.Objects)} objects, simulation proxy {type(s.ViewObject.Proxy).__name__}\n')
            for d in list(App.listDocuments().values()): App.closeDocument(d.Name)
    except Exception:
        log.write(traceback.format_exc())
    log.close()
    QtCore.QTimer.singleShot(300, Gui.getMainWindow().close)
QtCore.QTimer.singleShot(1500, go)
