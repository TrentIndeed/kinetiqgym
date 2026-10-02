#!/bin/sh
# Detached: FreeCAD part files + assemblies (incremental), then the motion studies. Writes regen.out / regen.done.
cd "$(dirname "$0")"; rm -f regen.done; : > regen.out; t0=$(date +%s)
./make_freecad.sh both >> regen.out 2>&1 && echo "parts+assemblies $(( $(date +%s)-t0 )) s" >> regen.out
./make_freecad.sh both --motion >> regen.out 2>&1 && echo "motion $(( $(date +%s)-t0 )) s" >> regen.out
echo ok > regen.done
