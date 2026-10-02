# Printing

All printed parts are in `print/` (STL, in the assembly frame: orient them in the slicer, see the "face down" column in
`print/README.md`). Every hole is already at its final size for the inserts and screws.

## Materials

- **Structural** (bottom plates, fairlead carrier and back plate, ODrive bracket, bearing cartridges, gussets): PA-CF
  (PAHT-CF), dried before printing.
- **Covers and end caps:** PETG-CF or PA-CF.
- **Light brackets** (screen frame, board plate, WAGO bracket, fan duct): PETG is fine.

Suggested settings for the structural parts (not yet validated by a load test): 0.2 mm layers, 5-6 walls, 6 top/bottom layers,
40-50 % gyroid infill, print the bottom plates flat on their underside. All parts fit a 256 mm bed (Bambu P2S class).

## Fit coupons first

`print/fit-coupons/` tests the tolerances in your material before the big prints:

1. Insert pockets M2.5 / M3 / M4 at -0.15 / nominal / +0.15 mm (Ruthex RX, pockets 3.6 / 4.0 / 5.6 mm).
2. Clearance holes M2.5 / M3 / M4 and the 5.2 mm pulley axle at -0.2 / nominal / +0.2 mm.
3. A 10 mm slice of the battery saddle (40.0 mm inside): slide a pack through it.
4. The exit pulley axles, 21.13 mm apart, with the carrier walls.
5. The 6809 bearing seat (58 mm): the bearing should press in by hand.

If your printer needs different sizes, adjust the holes in the FreeCAD parts (or the `source/` scripts) and re-export.
