# FCHIST=1 with this folder on PYTHONPATH: record CadQuery feature history for FreeCAD (see ../fchist_rec.py).
import os, sys
if os.environ.get('FCHIST') == '1':
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import fchist_rec; fchist_rec.install()
