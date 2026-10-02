#!/bin/sh
# Fairlead module changed: audit -> publish -> V44 pipeline (history recorded) -> payout/stop verification.
set -e
HERE=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$HERE")
export FCHIST=1 PYTHONPATH="$HERE/boot" PYTHONIOENCODING=utf-8
t0=$(date +%s)
cd "$R/stock-drive-study" && rm -f audit_partial.jsonl && python audit_voltra_module10.py > "$HERE/rec_audit.log" 2>&1 && echo "audit $(( $(date +%s)-t0 )) s"
python publish_fairlead_module10_packing.py > "$HERE/rec_publish.log" 2>&1 && echo "publish $(( $(date +%s)-t0 )) s"
cd "$R/print-v44-nano" && ./run_v44.sh > "$HERE/rec_pipeline.log" 2>&1 && echo "pipeline $(( $(date +%s)-t0 )) s"
python verify_payout_limits.py > payout-limits.log 2>&1 && echo "verify $(( $(date +%s)-t0 )) s"
