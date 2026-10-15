# Modifying the design

> **Draft.** The numbers below are design values for the prototype being built now; they are confirmed or corrected after
> it is load-tested. The editable CAD is released with the verified build files after that. Until then this page describes
> the interfaces in words and numbers.

The design is built to be adapted. The two interfaces most builders will change are the **battery bay** and the **motor
face**. The [website adaptation guide](https://kinetiqgym.com/build#modify) illustrates both.

## Batteries

The reference pack is two 5S LiPo packs in series: 10S, 42 V fully charged, about 30 V empty.

**The bay** takes two packs stacked, sliding in from the front through a printed cradle:

- two Thunder Power TP3300-5SR70 (about 141 x 43 x 33 mm each, by the maker's estimate) fill it: the opening is 44 mm, about
  0.5 mm a side;
- two TP2700-5SR70 fit on a printed spacer (a 12 mm block at the front and a 4 mm plate on the outer side), so both pairs
  sit against the same rear rib.

A 1 mm EVA pad under each cradle roof, a 2 mm separator between the packs, and a 2 mm pad inside the right cover's front wall
hold them. The leads leave from the packs' rear end faces into the back step.

To use another pack:

1. Measure both real packs, including leads and connector bodies: length, width and height. Do not rely on the nominal
   capacity or the listed size.
2. Compare them with the bay. Keep room for the pads, the lead bends, the BMS (it hangs from the right cover's ceiling) and
   a straight removal path through the cradle.
3. Print the battery fit coupon at your size before you print the end piece and the covers.
4. Check the electrical system as a whole:
   - the full-charge voltage must stay well under the ODrive Pro's 58 V, the regulator's 60 V and the fuses' 58 V rating,
     with room for regenerative braking (the ODrive's over-voltage trip is set at about 45 V);
   - the BMS must match the series count and chemistry, and pass charge and regen through one port;
   - recheck the charger, the fuse and wire sizes, and the regen current limit: it may not exceed the pack's charge rating
     (39.6 A for the TP3300 pair, 32.4 A for the TP2700 pair).

A pack that fits is not automatically electrically compatible.

## Motors

The drive is direct: the motor turns the drum through a rigid clamp coupling, with no belt or gear between them.

**The motor face plate** (0.250 in 6061) is bolted to the frame: it stands on two small angle brackets on the base plate and
is screwed through the rear plate into its back edge. It carries two bolt circles and a Ø16 mm shaft hole:

- 4 x M5 on Ø56 mm, on the 45° diagonals: the MP80100 and the APS C80100;
- 4 x M5 on Ø59 mm: the APS 8072S.

A different motor needs its own pattern on the same centerline (the drum axis), clear of the existing holes and of the two
brackets under the plate (their legs are 16 mm tall, under the reference motors' screw heads).

| Interface | Reference | What to check |
|---|---|---|
| Face mount | the face plate's two bolt circles; M5 spacers 3 mm long (APS 8072S) or 10 mm long (MP80100, C80100) | bolt pattern, pilot, and a spacer length that puts the shaft into the coupling |
| Shaft | One-piece steel clamp coupling, 29 mm OD x 45 mm, about 105 N·m: 12 mm on the drum side, 10 mm (McMaster-Carr 2469K23) or 12 mm (Ruland MCLX-12-12-F) on the motor side | the motor-side bore, about 20 mm of shaft in the clamp, and a rating of at least 1.5 x the peak drum torque |
| Rear shaft | the 80100 motors' bell-end shaft is cut to a 10 mm stub | what sticks out behind the motor |
| Body | 80 mm diameter outrunners; the motor bay is sized for each motor (builds about 400, 429 and 444 mm long) | the covers and end cap, with 3 mm of spin clearance to the end cap |
| Leads | three phase leads through a 12 mm grommet in the face plate, along the notches in the corner brackets, to the controller | lead exit, gauge and length |
| Controller | ODrive Pro: 70 A continuous, 100 A for 3 s, 58 V maximum. ODrive S1 (Lite): 40 A continuous, 80 A peak | the current your motor needs at your target force |

How to judge a motor:

- **Cable force ≈ motor torque ÷ drum rope radius** (17.5 mm). 158 lb (703 N) needs about 12.3 N·m; 220 lb (979 N) needs
  about 17.1 N·m.
- **Current ≈ torque ÷ torque constant**, with the torque constant about 8.27 ÷ Kv N·m per amp. At 50 Kv, 17.1 N·m takes
  about 103 A, more than the ODrive Pro's 70 A continuous. That is why the 220 lb builds use about 25-29 Kv windings (about
  52-63 A).
- **Felt inertia:** through the 17.5 mm radius, a rotor's inertia J (kg·m²) feels like about 3,265 x J kg at the rope. A
  lighter rotor feels better; the firmware can cancel part of it, but not all.
- Prefer low-voltage (48 V or less) DC brushless motors with a high pole count, close to the reference size. Avoid
  high-voltage AC servos: at this torque they are far larger and heavier than the body, or they need a reduction stage,
  which spoils the back-drive feel.
- A larger motor or a different Kv does not by itself make a safe resistance rating. The shared parts (frame, drum,
  level-wind, exit and rack side) are sized by calculation for the 220 lb peak builds; nothing is checked above that, and
  none of it is tested yet.

After a motor change, update the motor, encoder, current and thermal settings before any powered test
([firmware-setup.md](firmware-setup.md)).

## A knob instead of the touch screen

The Lite build already does this: an EC11 rotary encoder with a push button goes through the left cover where the screen
window was, and a phone app (Bluetooth, through a XIAO ESP32-C3) handles the settings. On a battery build the same change
closes the screen window and drops the screen and its frame. Whether the Raspberry Pi can also be left out depends on the
control software, which is not released yet.

## Sharing your changes

With the verified release the hardware is licensed CERN-OHL-S-2.0 (share-alike): if you distribute a modified version,
publish your modified design files under the same license. The KINETIQ and Kinetiq Gym names and logo are not licensed.
Contributions to the project open with the verified release.
