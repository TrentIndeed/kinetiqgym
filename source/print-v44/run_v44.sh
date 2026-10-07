#!/bin/sh
# Full V44 rebuild: sources -> placed parts -> vendor swaps -> mocks -> CAD updates -> structure (bottom plate, ladder, uprights) -> enclosure. Run from print-v44/.
# Round 8: unchanged parts, vendor swaps and clash pairs come from .cache/ (see v44cache.py). ./run_v44.sh --clean rebuilds everything.
set -e
export PYTHONIOENCODING=utf-8
if [ "$1" = "--clean" ]; then rm -rf .cache; fi
t0=$(date +%s)
step() { s=$(date +%s); python "$1" > "$2" 2>&1; echo "$1: $(( $(date +%s) - s )) s"; }
step register_sources.py register.log
rm -rf cnc printed
step build_v44_phase1.py phase1.log
step swap_real_cad.py swap.log
step mock_models.py mock.log
step teensy_fit.py teensy.log                                 # W7: Teensy 4.0 supplier CAD, centreline perfboard screws
step build_v44_chassis.py chassis.log
step build_v44_structure.py structure.log
step build_v44_shell.py shell.log
step build_v44_fasteners.py fasteners.log                       # round 13: screws, nuts, washers, inserts; holes checked and cut to size
step hardware_summary.py hwsum.log                             # round 13: buy list (hardware-summary.md)
step export_print_files.py printfiles.log                       # round 13: print-files/ STL + index
step build_v44_wires.py wires.log                               # round 10: harness (routes cached in .cache/)
step check_walls.py walls.log
step verify_payout_limits.py payout-limits.log                 # R14: payout range + the fairlead carrier swept through its stops vs every part
grep -h "register cache\|part cache\|swap memo" register.log phase1.log swap.log || true
echo "total: $(( $(date +%s) - t0 )) s"
tail -5 shell.log; tail -3 fasteners.log; tail -3 wires.log; tail -3 walls.log
