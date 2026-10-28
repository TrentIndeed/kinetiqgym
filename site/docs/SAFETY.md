# Safety

**Status: prototype design. It has not been built or load-tested yet.** Treat every number here as a design value until
your own build has passed the tests below.

## What can hurt you

- **Cable load.** The main build is designed to hold 220 lb (979 N) on the cable through a 20-30 s set, and the budget build
  180 lb (801 N). These are design targets, not yet verified: the motor's torque against current and the controllers'
  currents are still to be bench-tested. In the load study every part of the main build passes 1.5x: the frame and rack side
  at 220 lb (the lowest, the rack side's pad bar, at about 1.6x), the level-wind and the drum at 234 lb, the most the
  ODrive's 80 A can pull. Every structural part and bolt of the budget build passes 1.5x at 180 lb. These are calculations,
  to be confirmed by load testing.
  A rope, its clamp, a roller, the exit or the rack mount that fails under load releases that energy at the handle.
  Inspect the rope, the rope clamp, the rollers and the exit before every session, and replace a frayed rope at once.
- **Rope wear.** The main build's 7/8 in drum bends the 1/8 in rope tighter than the usual 8:1 ratio, by choice, so the rope
  wears sooner. Look along the part that winds on the drum every ~20 sessions (monthly for light use) and replace the rope
  when it is fuzzy or has broken yarns, looks glazed or fused, is flat, stiff or noticeably thinner, or is cut. With no
  published fatigue data for it, start by replacing it every 6 months of regular use, and adjust from what you see.
- **Rack mount.** The main build hangs on four studs on the rack side and is held by a spring latch. The rack side goes on a
  3 x 3 in upright with one 1 in hitch pin through the upright's side holes, and a toggle-clamp lever presses it against the
  upright's face. The budget build hangs on the upright on one 1 in hitch pin. Your rack must be anchored and able to take
  the pull. Fit the pin's clip, check that the lever is over center, and check that the latch has snapped home (the unit
  cannot lift) before every session.
- **Battery (main build).** Two 5S LiPo packs in series: 30-42 V, able to deliver very high current. Use the specified BMS
  and fuses and never bypass them. Charge only through the charge port with the BMS connected, with a 42.0 V (10S) charger.
  Store and charge the packs on a fire-safe surface, and never use a swollen or damaged pack.
- **Mains (budget build).** The budget build's 48 V supply sits in a floor box fed from the wall. Mains wiring can kill:
  have it checked by someone qualified, check earth continuity from the inlet's earth pin, and never run it with the floor
  box open.
- **Motor torque.** The motor can drive the drum with up to about 13 N·m. Keep fingers, hair and loose clothing away from
  the drum, the gears, the lead screw, the rollers and the exit while it is powered.
- **Heat.** A full-force set heats the motor quickly: by the design estimate the main build manages about two full 220 lb
  sets back to back before the motor's thermistor starts to roll the current back, and the resistance then drops. Do not
  disable the thermistor limit.
- **Regenerative braking.** On the main build, lowering the weight charges the battery. If the BMS stops accepting charge
  (full pack, over-temperature), the ODrive trips on over-voltage and **the cable goes slack**. Charge to about 80 % for
  training so braking energy has room. On the budget build, braking energy goes into two resistors on the inner plate,
  which get hot.

## Rules for every build

1. **Payout window in software.** Home the drum fully wound at every power-up and set the payout limit
   ([setup reference](https://kinetiqgym.com/docs/firmware-setup.html)). The traveller's hard stops at each end of its
   rail are only a backstop for assembly and hand-turning: the lead screw is geared to the drum, so a stop hit under power
   locks the drum through the printed gears and can strip them.
2. **Keep the dead wraps** of rope on the drum at full payout (3 on the main build). Never run the rope off the drum.
3. **Fuses rated 58 V DC (main build):** the 40 A MRBF main fuse, the 3 A regulator fuse and the 10 A charge fuse, in holders
   rated 58 V. Common 32 V automotive fuses and holders are not rated for this pack voltage.
4. **Bolted joints and adhesives.** Every load-bearing screw goes to a nut; nothing in the load path is screwed into a
   tapped hole or an insert. Loctite 243 on the gusset, drum and rack-cheek screws. The drum flanges are bonded to the tube,
   and the hub to the shaft, with Loctite 638: no load for 24 h. Check the frame and rack-side screws after the load test.
5. **First power-up** with the rope unloaded and nobody in its path: check the inrush at the power button (the BMS may
   trip; lengthen its short-circuit delay in the BMS app if it does), the drum's direction, the motor thermistor reading,
   the payout window, the over-voltage trip and the regen limit.
6. **Bench-test the drive** before training at the rated force: the motor's torque against current, the controller's
   current through a 30 s set, and the motor's heat over several sets.
7. **Load test** before training: hang a static load in steps up to 1.5 x your planned use, with nobody in the rope's path.
   Then test powered, starting light.
8. **Printed parts:** print them in the specified materials, with the walls and infill in the
   [printing reference](https://kinetiqgym.com/docs/printing.html), and print the fit coupons first. The screw-end tower
   must be printed on its side.

## No warranty

The design is shared under the licenses in `LICENSE.md` **without any warranty**. You build and use it at your own risk.
