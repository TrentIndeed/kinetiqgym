# Modifying the design

The design is meant to be adapted: a different motor, a rotary encoder instead of the touch screen, a different battery.
This release ships the parts as FreeCAD files with their full feature history and as STEP; fully sketch-based,
parameter-driven parts are planned for the next release.

## How the CAD is organised

- `cad/freecad/<printed|cnc>/V44_<variant>_assembly.FCStd`: the whole machine. Every part is a link to its own file in `parts/`.
  A part that takes heat-set inserts is a container holding the part and its inserts.
- `cad/freecad/<variant>/parts/<part>.FCStd`: one part with its feature tree (boxes, cylinders, cuts, fuses, fillets, moves).
  Each feature is labelled with the build-script line that made it. Change a size or a placement and recompute.
- `cad/freecad/<variant>/V44_<variant>_drivetrain_motion.FCStd`: Assembly-workbench motion study of the drivetrain.
- `cad/step/`: the same parts as STEP for any CAD program, plus one assembly STEP per variant.
- `cad/dxf/`: 2-D profiles of the flat parts.
- Supplier parts (motor driver, bearings, gears, boards...) are simple placeholders of the right size; get the real CAD
  from `cad/vendor/README.md`.
- `source/`: the Python (CadQuery) scripts that generate everything. They are the source of truth, but in this release they
  still expect the full design workspace; a self-contained build is planned.

Variants: **printed** (PA-CF bottom plate with aluminium flat bars under it) and **cnc** (aluminium bottom plate).

## Swapping the motor

What the motor touches:

| Interface | Where | Change |
|---|---|---|
| Face mount | the 4 mm motor face plate (`V43_METAL_motor_face_4mm`) + two printed gussets | hole pattern and pilot bore for your motor |
| Shaft | the NBK MSTS-25-10-12 coupling (10 mm motor, 12 mm drum shaft) | coupling bore for your shaft |
| Envelope | motor body about 80 x 82 mm at the motor end (X -77 to -3) | the end cap, covers and the board plate around it |
| Leads | three phase leads through a 12 mm grommet in the face plate to the ODrive terminal | lead exit and length |
| Electrical | ODrive Pro limits (current, voltage), torque constant | `firmware-setup.md` |

Torque at the drum is the motor torque (direct drive): the cable force is about torque / 0.025 m (rope radius on the drum).

## Swapping the batteries

1. Measure both actual packs, including leads and connector bodies. Record length, width and height; do not rely only on nominal capacity.
2. Open a copy of the assembly and the saddle/retainer part files. Edit the relevant feature dimensions. For a STEP-only workflow, import the solids, create a constrained rectangular envelope sketch, and use new additive/subtractive features for your revised mount.
3. Add padding and lead-bend clearance to the envelope. Keep the BMS, wires and mounting screws outside the straight removal path. Test both pack envelopes together, including staggered removal.
4. Recompute the covers and check intersections and retaining surfaces. Print a fit sample before committing to a full enclosure; export the updated STEP/STL and update the BOM and revision.
5. Review series count, fully charged voltage, BMS, charger, fuse/wire sizing and regenerative charge limits as a system before powered testing. Capacity alone does not establish compatibility.

The reference is two 5S packs in series (10S, 42 V fully charged). The [website adaptation guide](https://kinetiqgym.com/#modify) illustrates the pack envelope and motor interfaces. Its diagrams are measurement guides, not dimensioned manufacturing drawings.

## Rotary encoder instead of the touch screen

What the screen touches:

| Interface | Where | Change |
|---|---|---|
| Front window | the left cover (`V44_PRINT_cover_left_screen`), 4 in window | replace the window with a panel hole for the encoder (and a small display if wanted) |
| Screen frame | `MOUNT_screen_rear_retaining_frame_printed` + 2 x M3 legs into inserts | not needed |
| Pi + DSI ribbon | Raspberry Pi 4 hanging from the cover ceiling, ribbon to the screen | optional: the Teensy can run the machine alone |
| Encoder | quadrature A/B + push switch to free Teensy pins, 3.3 V | firmware |

## Contributing changes back

The hardware is CERN-OHL-S-2.0 (share-alike): if you distribute a modified version, publish your modified design files under
the same licence. Pull requests and issues are welcome: see `CONTRIBUTING.md`.
