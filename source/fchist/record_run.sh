#!/bin/sh
# Rebuild the parts with feature-history recording (fchist_rec.py): fairlead module, rev-11 mounts, then the V44 pipeline.
# Same geometry as a normal run; each part file gets <file>.fch.json and the base shapes go to cad/single-cable/.fchist/.
set -e
HERE=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$HERE")
export FCHIST=1 PYTHONPATH="$HERE/boot" PYTHONIOENCODING=utf-8
(cd "$R/stock-drive-study" && python build_voltra_module10.py > "$HERE/rec_fairlead.log" 2>&1)
(cd "$R/mounts-rev11" && python build_mounts.py > "$HERE/rec_mounts.log" 2>&1)
cd "$R/print-v44-nano" && rm -rf .cache/phase1 .cache/swap && ./run_v44.sh
