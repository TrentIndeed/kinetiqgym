# Safety

**Status: prototype design. It has not been built or load-tested yet.** The aluminum prototype is being built now. Treat
every number here as a design value until your own build has passed the tests below.

## What can hurt you

- **Cable load.** The main build is rated for a 158 lb (703 N) peak pull on the cable; the 220 lb builds for a 220 lb
  (979 N) peak. In the load study every member of the bolted frame, the drum and the rack side passes 1.5x at 220 lb (the
  weakest, the rack cheek screws, at 2.9x); the level-wind rail is the one part below that, at about 1.3x on the last few
  wraps. These are calculations, to be confirmed by load testing.
  A rope, its clamp, a roller, the exit or the rack mount that fails under load releases that energy at the handle.
  Inspect the rope, the rope clamp, the rollers and the exit before every session, and replace a frayed rope at once.
- **Rack mount.** The unit hangs on four studs on the rack side and is held by a spring latch. The rack side clamps round a
  3 x 3 in upright with the rack's 1 in pin. Your rack must be anchored and able to take the pull. Fit the pin's clip, and
  check that the latch has snapped home (the unit cannot lift) before every session.
- **Battery.** The battery builds use two 5S LiPo packs in series: 30-42 V, able to deliver very high current. Use the
  specified BMS and fuses and never bypass them. Charge only through the charge port with the BMS connected, with a 42.0 V
  (10S) charger. Store and charge the packs on a fire-safe surface, and never use a swollen or damaged pack.
- **Mains (Lite).** The Lite has a 36 V supply inside, fed from the wall. Mains wiring can kill: have it checked by someone
  qualified, check earth continuity from the inlet's earth pin to the base plate and the rear plate, and never run it with
  the covers off.
- **Motor torque.** The motor can drive the drum with up to about 13 N·m (main build) or 17 N·m (220 lb builds). Keep
  fingers, hair and loose clothing away from the drum, the gears, the lead screw, the rollers and the exit while it is
  powered.
- **Regenerative braking.** Lowering the weight charges the battery. If the BMS stops accepting charge (full pack,
  over-temperature), the ODrive trips on over-voltage and **the cable goes slack**. Charge to about 80 % for training so
  braking energy has room. On the Lite, braking energy goes into two resistors on the base plate, which get hot.

## Rules for every build

1. **Payout window in software.** Home the drum fully wound at every power-up and set the payout limit
   ([setup reference](https://kinetiqgym.com/docs/firmware-setup.html)). The traveller's hard stops at each end of its
   rail are only a backstop for assembly and hand-turning: the lead screw is geared to the drum, so a stop hit under power
   locks the drum through the printed gears and can strip them.
2. **Keep the 3 dead wraps** of rope on the drum at full payout. Never run the rope off the drum.
3. **Fuses rated 58 V DC:** the 40 A MRBF main fuse, the 3 A regulator fuse and the 10 A charge fuse, in holders rated
   58 V. Common 32 V automotive fuses and holders are not rated for this pack voltage.
4. **Bolted joints and adhesives.** Loctite 243 on every screw into the frame's, drum's and rack cheeks' tapped edge holes.
   The drum flanges are bonded to the tube, and the hub and flanges to the shaft, with Loctite 638: no load for 24 h. Check
   the frame and rack-side screws after the load test.
5. **First power-up** with the rope unloaded and nobody in its path: check the inrush at the power button (the BMS may
   trip; lengthen its short-circuit delay in the BMS app if it does), the drum's direction, the payout window, the
   over-voltage trip and the regen limit.
6. **Load test** before training: hang a static load in steps up to 1.5 x your planned use, with nobody in the rope's path.
   Then test powered, starting light.
7. **Printed parts:** print them in the specified materials, with the walls and infill in the
   [printing reference](https://kinetiqgym.com/docs/printing.html), and print the fit coupons first. The screw-end tower
   must be printed on its side.

## No warranty

The design is shared under the licenses in `LICENSE.md` **without any warranty**. You build and use it at your own risk.
