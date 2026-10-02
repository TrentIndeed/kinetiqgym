# Safety

**Status: prototype design. It has not been built or load-tested as published.** Treat every number here as a design value
until your own build has passed the tests below.

## What can hurt you

- **Cable load.** The machine is designed for 890 N (200 lbf) on the cable. A rope, an anchor or a printed part that fails
  under load releases that energy at the handle. Inspect the rope, the anchor wraps and the fairlead before every session;
  replace a frayed rope at once.
- **Battery.** Two 5S lithium-polymer packs in series make 30-42 V and can deliver very high current. Use the specified
  BMS and fuses, never bypass them, charge only with the BMS connected, and store and charge the packs on a fire-safe surface.
- **Motor torque.** The ODrive can drive the drum with up to about 13 N·m. Keep fingers, hair and loose clothing away from the
  drum, gears and the rope exit while it is powered.
- **Regenerative braking.** Lowering the weight charges the battery. If the BMS stops charging (full pack, over-temperature),
  the ODrive trips on over-voltage and **the cable goes slack for that rep**. Charge to about 80 % so braking energy has room.

## Rules for every build

1. **Payout limit in software.** Home the drum fully wound and set the ODrive position limits (`docs/firmware-setup.md`):
   `pos_min = 0`, `pos_max = 13.26` turns. The two hard stops on the fairlead carrier (+-48.4 deg) are only a backstop for
   assembly and hand-turning: the worm drive cannot be back-driven, so a stop hit under load locks the drum through the
   gears and can strip the m0.8 gears or break the printed lug.
2. **Keep the 3 dead wraps** of rope on the drum at full payout. Never run the rope off the drum.
3. **Fuses:** 40 A 58 V main fuse, 3 A 58 V regulator fuse, 7.5 A 58 V charge fuse. Automotive 32 V fuses are not rated for
   this pack voltage.
4. **First power-up** with the rope unloaded: check the inrush at the power button (the BMS may trip; lengthen its
   short-circuit delay in the BMS app if it does), the direction of the drum, the soft limits and the ODrive over-voltage trip.
5. **Load test** before training: hang a static load in steps up to 1.5 x your planned use, with nobody in the rope's path.
6. Print the structural parts in the specified material (PA-CF / PETG-CF), with the infill and walls in `docs/printing.md`,
   and print the fit coupons first.

## No warranty

The design is shared under the licences in `LICENSE.md` **without any warranty**. You build and use it at your own risk.
