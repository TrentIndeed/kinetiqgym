#!/bin/sh
# Resume the V44 pipeline from the fastener step (history recorded). Writes run_rest.out and run_rest.done.
cd "$(dirname "$0")"
export FCHIST=1 PYTHONPATH="$(cd .. && pwd)/fchist/boot" PYTHONIOENCODING=utf-8
rm -f run_rest.done; : > run_rest.out
t0=$(date +%s)
for s in build_v44_fasteners:fasteners hardware_summary:hwsum export_print_files:printfiles build_v44_wires:wires check_walls:walls verify_payout_limits:payout-limits; do
  f=${s%%:*}; l=${s##*:}; st=$(date +%s)
  if ! python -X faulthandler $f.py > $l.log 2>&1; then echo "$f FAILED" >> run_rest.out; tail -5 $l.log >> run_rest.out; echo failed > run_rest.done; exit 1; fi
  echo "$f: $(( $(date +%s)-st )) s" >> run_rest.out
done
echo "total $(( $(date +%s)-t0 )) s" >> run_rest.out; echo ok > run_rest.done
