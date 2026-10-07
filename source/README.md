# Build scripts (GPL-3.0)

The Python / CadQuery scripts that generate every part, the fasteners, the wiring and the FreeCAD files.
They are the source of truth for the CAD. In this release they still expect the full design workspace (supplier CAD and the
interactive layout data are not published), so treat them as readable source; a self-contained build is planned.

- `print-v44/run_v44.sh`: the V44 pipeline (parts -> structure -> enclosure -> fasteners -> wiring -> checks)
- `mounts-rev11/`: brackets, saddles, board plates; `stock-drive-study/`: the fairlead module
- `fchist/`: records the CadQuery history and writes the FreeCAD files; `release/`: builds this repository
