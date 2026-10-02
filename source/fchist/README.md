# fchist: the V44 parts in FreeCAD, with their feature history

The Python build scripts stay the source of truth. While they run with `FCHIST=1`, every CadQuery modelling call is
recorded, and `to_freecad.py` turns that record into FreeCAD part files with a real feature tree: primitives,
booleans, fillets and moves that you can open, read and edit.

```
record_run.sh       one pipeline run with recording on (fairlead module -> rev-11 mounts -> V44 pipeline; same geometry)
make_freecad.sh     FreeCAD files -> cad/single-cable/freecad/<printed|cnc>/   (./make_freecad.sh [printed|cnc|both] [part prefix ...])
```

## What you get

`freecad/<variant>/V44_<variant>_assembly.FCStd` links every part (one `App::Link` per part, grouped by subsystem, coloured,
the "complete" view shown). A part that takes heat-set inserts is an `App::Part` holding the part and its inserts, so they move together. Each part is its own file in `freecad/<variant>/parts/<part>.FCStd`.

Open a part and expand its tree. The top feature is the finished part and holds the whole build:

| Pipeline call | FreeCAD feature |
|---|---|
| `Solid.makeBox / makeCylinder / makeCone / makeSphere / makeTorus` | `Part::Box / Cylinder / Cone / Sphere / Torus` (size + Placement) |
| `cut`, `fuse`, `intersect` | `Part::Cut` (several tools: a `MultiFuse` of the tools), `Part::MultiFuse`, `Part::MultiCommon` |
| `translate`, `rotate`, `moved`, `transformShape`, page placements | the Placement of the feature they move |
| `mirror` | `Part::Mirroring` |
| `clean` | `Part::Refine` |
| `fillet`, `chamfer` | `Part::Fillet`, `Part::Chamfer` (edges found again by position) |
| `Compound.makeCompound` | `Part::Compound` |
| anything else (wire extrusions, text, sweeps, picking one solid, supplier CAD, mesh-rebuilt page parts) | a `Base:` feature holding the exact shape |

Each feature's label names the script line that made it (for example `Cut · build_v44_shell.py:142 body`), and Label2 holds
the full call site. Change a primitive's size or placement and recompute: everything after it in the tree follows.

Every part is checked against the pipeline's own shape (volume and bounding box) in `freecad-report.json`.
If a rebuilt tree does not match, the part keeps its tree and shows the exact shape on top, and the report lists it.

## Drivetrain motion (FreeCAD Assembly workbench)

`freecad/<variant>/V44_<variant>_drivetrain_motion.FCStd` (`./make_freecad.sh both --motion`, `motion.py`) is a real
Assembly-workbench study, solved by FreeCAD's own solver:

- the motor body is grounded; Revolute joints on the drum shaft, shaft 2, the worm shaft and the carrier ring (6809 pivot);
- every part that turns with a shaft is Fixed to it; **Gears** joints carry drum 60T -> shaft-2 60T and shaft-2 20T -> worm-shaft 20T;
- FreeCAD has no worm-gear joint, so the carrier ring has its own motion at exactly 1/53 of the drum (direction checked: the
  worm and ring teeth never overlap through a worm turn);
- **Simulation: motor** drives the drum +-5.5 turns over 20 s (carrier +-37 deg, inside its +-48.4 deg stops).

Open the file, switch to the Assembly workbench, double-click *Simulation: motor*, press **Run** (about 3 minutes for the
1,000 frames), then **Play** or drag the frame slider. The covers are hidden; show them from the Static parts group.
Change the motor in the *Motor: drum shaft* motion (formula in radians of time, e.g. `6.28*time` = 1 turn/s; then set the
carrier motion to the same formula divided by 53). Keep the drum under about 13 deg per frame or the gear joints lose track.

## How it works

- `boot/sitecustomize.py` installs `fchist_rec.py` when `FCHIST=1` and `fchist/boot` is on `PYTHONPATH`. The build scripts are
  unchanged, apart from two direct OCP moves that now report themselves (`build_v44_phase1.py apply()`, `teensy_fit.py`).
- Each written part file gets `<file>.fch.json` (the graph back to the first primitive, with the file's hash). Reading the file in the
  next stage continues the same history, so a part made in `build_mounts.py`, placed in phase 1, cut by the shell and drilled by
  the fasteners step is one tree. Base shapes are stored once, by content hash, in `cad/single-cable/.fchist/blobs/` (not committed).
- History files are only trusted when the part file's hash matches, so a part rebuilt without recording falls back to its exact shape.

## Next (open-source path)

Sketches: replace the `Base:` features that come from wire extrusions (wire loops, gussets, polyline profiles) with
FreeCAD Sketcher sketches + Pad, and draw the plates and brackets from sketches instead of boxes, so the
release has editable 2-D profiles (and DXF) as well as the history.
