#!/bin/sh
# FreeCAD files with the feature history of every V44 part -> cad/single-cable/freecad/<variant>/.
# Needs a pipeline run with history recording first:  ./record_run.sh   (or FCHIST=1 on any build step).
# usage: ./make_freecad.sh [printed|cnc|both] [part-name-prefix ... | --assembly | --motion]
#   --assembly  relink the assembly only;  --motion  rebuild the drivetrain motion study (opens FreeCAD briefly)
set -e
HERE=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$HERE")
FCPY=${FREECAD_PY:-/d/Programs/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe}
V=${1:-both}; [ $# -gt 0 ] && shift
if [ "$1" = "--motion" ]; then
  VS=$V; [ "$V" = both ] && VS=printed,cnc
  FCH_HERE="$HERE" FCH_MODEL="$R/print-v44-nano" FCH_VARIANT="$VS" FCH_OUT="$R/freecad" "$(dirname "$FCPY")/freecad.exe" "$HERE/motion_gui.py"
  cat "$HERE/motion_gui.log"; exit 0
fi
for v in printed cnc; do
  if [ "$V" = both ] || [ "$V" = "$v" ]; then
    echo "== $v"; "$FCPY" "$HERE/to_freecad.py" "$R/print-v44-nano" "$v" "$R/freecad" "$@" 2>&1 | grep -v "^\s*(\|Recompute"
  fi
done
