# Printing

> **Draft.** These settings and hole sizes are for the main build as designed now. They have not been validated by a load
> test. The print files are released with the verified CAD after the prototype is tested. The budget build prints its parts
> in PETG; its print list comes with its verified files.

The bolted 6061 aluminum frame, the drum and the rack side carry the rope load. The printed parts bolt to that frame: the
two end pieces, the level-wind, the exit, the screw-end tower, the gears, the brackets and the covers. Every part fits a
256 x 256 mm bed. The print files come in the assembly's orientation: turn each part in the slicer as listed below.

## Materials

| Material | Parts |
|---|---|
| **PAHT-CF**, dried before printing | load-path parts: the 81T drum gear and the 45T screw gear, the traveller frame, the fixed roller bracket, the top tie, the far-end screw stand, the screw-end tower, the rope clamp ring, the exit bearing housing, the exit carrier, its retainers and rail caps |
| **PA-CF** (or PAHT-CF), dried | the motor-end and battery-end pieces, the ODrive bracket, the latch finger bar and the service lid |
| **PETG-CF** (or PA-CF) | the two covers (each with its end cap printed in) and the rear I/O panel |
| **PETG** | the screen frame, the front board plate and its standoffs, the WAGO bracket, the fan duct, and the battery spacer for the TP2700 pair |
| **PETG or PLA** | the drill guides (see below) |
| **TPU 95A** (optional) | the three battery pads, flat, 15-20 % gyroid; or cut them from 1 mm and 2 mm EVA foam sheet |

The carbon-fiber filaments wear brass nozzles: use a hardened nozzle.

## Settings

Suggested for the structural parts (PAHT-CF and PA-CF), not yet validated by a load test:

- 0.2 mm layers;
- 5-6 walls;
- 6 top and 6 bottom layers;
- 40-50 % gyroid infill.

## Orientation

| Part | Face on the bed |
|---|---|
| Screw-end tower | **on its side, web flat on the bed.** Its bending then runs along the layers. Never print it upright. |
| Top tie | on its side, so the layers run along the bar |
| End pieces | underside down |
| Covers | top down (the wire loops bridge; no supports) |
| Rope clamp ring | outer face down (grooves and knot pocket up) |
| 81T drum gear | gear face down |
| 45T screw gear | hub face up |
| Fixed roller bracket | flange face down |
| Traveller frame | carriage plate down |
| Far-end screw stand | foot down |
| Front board plate | back face down |
| Rear I/O panel | outer face down |
| Battery pads | flat |
| TP2700 battery spacer | side plate down |

The bearing seats, the nut bore and the screw holes in the level-wind parts run horizontally. A hole printed on its side
can droop at the top: check each against its fit coupon before assembly.

## Heat-set inserts

The pockets are cut for the **3DZWMAN 380-piece insert kit**. Other brands' inserts have other sizes and may not grip.

| Thread | Insert (length x outer Ø) | Pocket hole |
|---|---|---|
| M2 | 3 x 3.2 mm | 2.9 mm |
| M2.5 | 4 x 4.0 mm | 3.6 mm |
| M3 | 4 x 4.2 mm | 4.0 mm |
| M4 | 5 x 5.0 mm | 4.6 mm |
| M5 | 5 x 7.0 mm | 6.4 mm |

Pockets are one millimeter deeper than the insert, with a 0.5 mm lead-in. Press each insert in square to the face with a
soldering iron and an insert tip, and let it cool before loading it.

Other printed holes: clearance M2.5 2.9 / M3 3.6 / M4 4.7 mm; self-tapping pilots M2.5 2.2 / M3 2.6 mm.

## Drill guides

The frame is bolted together, and a few of its holes go into the edge of a plate or the end of the drum tube, where a laser
cutter cannot reach. Printed drill guides make them accurate by hand. Each guide is a cap that slips over the edge, with an
end stop that locates the holes, and guide bores 20 mm long sized for the drill (drill + 0.15 mm). The edge holes are
clearance holes that run into nut windows cut through the plate: nothing in the load path is tapped.

| Guide | Holes | Drill | Located by |
|---|---|---|---|
| Rear plate, bottom edge | 6 | 4.5 mm (M4) | an end stop on the plate's motor end |
| Motor face plate, back edge | 2 | 3.4 mm (M3) | an end stop on the plate's bottom edge |
| Motor face plate, bottom edge | 3 | 3.4 mm (M3) | an end stop on its front end; its tabs sit in pockets in the guide |
| Drum bearing holder, bottom edge (one guide for both) | 2 | 4.5 mm (M4) | an end stop on its front end; the tab in a pocket |
| Corner gusset, bottom edge (one guide for all three) | 2 | 3.4 mm (M3) | an end stop on the toe's front end |
| Corner gusset, back edge | 2 | 3.4 mm (M3) | the notch's top face |
| Drum tube end (use it on both ends) | 4 | 4.5 mm (M4), 6 mm deep | a boss that centers it in the bore; side marks for the four nut notches |

- Print them in PETG or PLA, cap face down so the bores print vertical, with 100 % infill round the bores.
- Clamp the part in a vise edge up, push the guide against its end stop and drill through the bores into the windows. On
  the drum tube, saw and file the nut notches to the guide's marks. The depths are in the [build instructions](build.md).
- A worn guide is reprinted.

## Fit coupons first

Print the fit coupons in the same material and on the same printer before the large parts. Each one tests a few sizes
around the design value:

1. **Insert pockets** M2.5 / M3 / M4 at -0.15 / nominal / +0.15 mm. Press an insert into each and use the size that goes
   in straight and holds a tightened screw.
2. **Clearance holes** M2.5 / M3 / M4 at -0.2 / nominal / +0.2 mm. The screw should slide through the nominal hole without
   forcing.
3. **Battery slice:** a 10 mm slice of the battery cradle (44.0 mm opening: the TP3300's 43 mm plus 0.5 mm a side). Slide a
   real pack through it both ways. A TP2700 pack goes in on its printed spacer.
4. **688 bearing seat:** slices of the screw-end tower wall with 15.90 to 16.20 mm bores (the design uses 16.10). Use the
   tightest that seats the bearing flush by hand or in a vise without splitting the ring.
5. **Roller shoulder holes:** 6.0 to 6.3 mm (the design uses 6.2) with the 10.4 mm head counterbore. The shoulder should
   slide in without wobble and the head should sit below the face.
6. **M5 and M4 inserts:** M5 pockets at 6.25 / 6.40 / 6.55 mm and M4 pockets at -0.15 / nominal / +0.15 mm.
7. **T8 nut seat:** bores of 10.4 to 10.8 mm (the design uses 10.8) for the brass nut's 10.2 mm body, with the flange's M3
   insert pockets. Check that the bore stays round with the inserts set: only 0.6-0.75 mm is left between them.
8. **Lead-screw clearance:** 8.6 / 8.9 / 9.2 mm (the design uses 9.2). The screw must turn freely: the nut is the only
   contact.

If a different size works best in your material, note it. Hole sizes are easy to change in the editable CAD, which is
released with the verified build files.
