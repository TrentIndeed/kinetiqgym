"""V44 stepped back wall (user sketch, Sept 29; round 11 follows it closer). Shared by build_v44_structure.py (rear plate,
bottom-plate outline, handle, clevis) and build_v44_shell.py (covers, end caps, bosses).

The back wall moves toward the front by zone:
  A  X -81..80   (motor end to the rack mount):  -22.5 mm -> rear plate inner face Y -20 (just behind the motor, face plate and gussets)
  B  X 80..181   (rack mount):                   -27.0 mm -> inner face Y -24.5, 2.5 mm behind the drum (its 2 mm sweep clearance kept)
  C  X 181..248  (WAGO beside the fan, fuse holder under both, ODrive terminal): unchanged (inner face Y 2.5); back step unchanged.
The handle moves with zone A, the rack clevis with zone B. The Pi's USB plugs keep a small hood in zone A (X 0..66, top only).
Round 11: the step walls (and the 6 mm walls joining the plates) sit on the shallower zone's side, behind its plate, so the deeper
zone keeps its full length inside (the WAGO sits right at the zone B/C step).
"""
INNER0, OUTER0, COVER0 = 2.5, 8.5, 5.5          # rear plate inner / outer face and cover back (Y1E) before round 9
ZONES = [(-81.0, 80.0, -22.5), (80.0, 181.0, -27.0), (181.0, 248.0, 0.0)]
PI_HOOD = None                                           # round 12: the Pi moved 15 mm toward the screen; its USB plugs fit inside, no hood

def dy(x):
    for x0, x1, d in ZONES:
        if x < x1 or (x0, x1, d) == ZONES[-1]:
            return d if x < 248.0 else 0.0
    return 0.0

def inner(x): return INNER0 + dy(x)
def outer(x): return OUTER0 + dy(x)
def cover_back(x): return COVER0 + dy(x)

def connectors():
    """(x0, x1, y0, y1) of the 6 mm connector walls between zones, placed inside the shallower zone (behind its plate)."""
    out = []
    for (a0, a1, da), (b0, b1, db) in zip(ZONES, ZONES[1:]):
        if db > da: out.append((a1 - 6.0, a1, INNER0 + da, OUTER0 + db))
        else: out.append((a1, a1 + 6.0, INNER0 + db, OUTER0 + da))
    return out
