"""Round 13: printed loops under the cover top that the two main wire passages hang in. Shared by build_v44_shell.py (the loops
are printed with the covers: fused to the ceiling) and build_v44_wires.py (the wires are routed through a slot in each loop).

Each loop is two posts down from the ceiling and a bar across their feet: printed with the cover (ceiling on the bed) the bar is a
short bridge between the posts, no supports. The harness is threaded through before the far connectors go on.
  front passage (over the motor, runs along Y): the regulator feed + return, the fan pair and the Teensy USB, front boards -> back
  back passage (over the drum, runs along X): the regulator feed + return and the fan pair, on to the fuses, WAGO and fan
"""
import numpy as np
import cadquery as cq

ZT, W = 96.5, 3.0                       # cover top and wall (ceiling underside Z 93.5)
WALL, T = 2.4, 5.0                      # loop wall and its width along the run
CLIPS = [
    dict(name='front_1', c=(-16.0, -95.0), run='y', w=14.0, h=5.5, zb=86.0, cover='V44_PRINT_cover_left_screen'),
    dict(name='front_2', c=(-16.0, -55.0), run='y', w=14.0, h=5.5, zb=86.0, cover='V44_PRINT_cover_left_screen'),
    dict(name='back_1', c=(110.0, -36.0), run='x', w=10.0, h=5.5, zb=83.0, cover='V44_PRINT_cover_centre_exit'),
    dict(name='back_2', c=(140.0, -36.0), run='x', w=10.0, h=5.5, zb=83.0, cover='V44_PRINT_cover_centre_exit'),
]
BY = {c['name']: c for c in CLIPS}
PASSAGES = {'front': ['front_1', 'front_2'], 'back': ['back_1', 'back_2']}
# wires in each loop, in slot order across the opening (their insulation OD), left to right
SLOTS = {'front': [('WIRE_USB_Teensy_to_Pi', 3.8), ('WIRE_regulator_VIN+_from_inline_fuse_18AWG', 1.8), ('WIRE_regulator_VIN-_to_WAGO_18AWG', 1.8),
                   ('WIRE_5V_fan_plus_24AWG', 1.3), ('WIRE_5V_fan_minus_24AWG', 1.3)],
         'back': [('WIRE_regulator_VIN+_from_inline_fuse_18AWG', 1.8), ('WIRE_regulator_VIN-_to_WAGO_18AWG', 1.8),
                  ('WIRE_5V_fan_plus_24AWG', 1.3), ('WIRE_5V_fan_minus_24AWG', 1.3)]}

def _box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))

def _frame(c):
    """(along-run axis index, across-run axis index) and the clip's across / along extents."""
    return (1, 0) if c['run'] == 'y' else (0, 1)

def solid(c):
    a, v = _frame(c); ca, cv = c['c'][a], c['c'][v]; w, zb = c['w'], c['zb']; top = ZT - W + 0.5
    pieces = [(cv - w / 2 - WALL, cv - w / 2, zb - WALL, top), (cv + w / 2, cv + w / 2 + WALL, zb - WALL, top), (cv - w / 2 - WALL, cv + w / 2 + WALL, zb - WALL, zb)]
    out = []
    for v0, v1, z0, z1 in pieces:
        lo, hi = [0.0, 0.0], [0.0, 0.0]
        lo[a], hi[a] = ca - T / 2, ca + T / 2; lo[v], hi[v] = v0, v1
        out.append(_box(lo[0], hi[0], lo[1], hi[1], z0, z1))
    return out[0].fuse(*out[1:]).clean()

def slot(c, k, passage):
    """Centre of the k-th wire's slot in clip c: resting 0.3 mm above the bar, 0.6 mm apart across the opening."""
    a, v = _frame(c); ods = [od for _, od in SLOTS[passage]]
    x = c['c'][v] - c['w'] / 2 + 0.5 + sum(od + 0.6 for od in ods[:k]) + ods[k] / 2
    p = [0.0, 0.0, c['zb'] + ods[k] / 2 + 0.3]; p[v] = x; p[a] = c['c'][a]
    return p

def vias(wire_id, start_xy):
    """Entry / exit points through every loop the wire uses, in the order met from its start (start_xy = its first point)."""
    passes = []
    for passage, names in PASSAGES.items():
        ids = [n for n, _ in SLOTS[passage]]
        if wire_id in ids:
            k = ids.index(wire_id)
            passes += [(BY[n], k, passage) for n in names]
    s = np.asarray(start_xy[:2], float); out = []
    # order the loops along the wire: greedy nearest from the start
    todo = list(passes); cur = s
    while todo:
        j = min(range(len(todo)), key=lambda i: np.linalg.norm(np.asarray(todo[i][0]['c']) - cur))
        c, k, passage = todo.pop(j); p = np.asarray(slot(c, k, passage)); a, _ = _frame(c)
        e0, e1 = p.copy(), p.copy(); e0[a] -= T / 2 + 2.0; e1[a] += T / 2 + 2.0
        if np.linalg.norm(e0[:2] - cur) > np.linalg.norm(e1[:2] - cur): e0, e1 = e1, e0
        out += [tuple(map(float, e0)), tuple(map(float, e1))]; cur = e1[:2]
    return out
