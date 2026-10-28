# Modifying the design

> **Draft.** The numbers below are design values for the main build as designed now; they are confirmed or corrected after
> the prototype is load-tested. The editable CAD is released with the verified build files after that. Until then this
> page describes the interfaces in words and numbers.

The design is built to be adapted. The two interfaces most builders will change are the **battery bay** and the **motor
face**. The [website adaptation guide](https://kinetiqgym.com/build#modify) illustrates both. This page describes the main
build; the budget build runs from the wall and has no battery bay.

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

The drive is direct: the motor turns the drum through a rigid clamp coupling, with no belt or gear between them. Both
builds use an off-the-shelf motor, the Freerchobby MP8085 50 Kv: no custom windings.

**The motor face plate** (0.250 in 6061) stands on two tabs in slots in the base plate and is bolted to the base and rear
plates into nuts in its windows. It carries the MP8085's pattern, 4 x M5 on Ø56 mm on the 45° diagonals, and a Ø16 mm shaft
hole. A different motor needs its own pattern on the same centerline (the drum axis), clear of the existing holes and the
nut windows.

| Interface | Reference | What to check |
|---|---|---|
| Face mount | 4 x M5 x 25 on Ø56 mm through four Ø10 x 10 mm spacers, into the motor's own threads | bolt pattern, pilot, thread depth, and a spacer length that puts the shaft into the coupling |
| Shaft | Ruland MCLX-12-12-F one-piece steel clamp coupling, 12 mm both sides, 29 mm OD x 45 mm, 105 N·m; about 21 mm of shaft in the clamp | the motor-side bore, the clamp length, and a rating of at least 1.5 x the peak drum torque |
| Rear shaft | the MP8085's rear prop shaft is cut flush with its rear hub | what sticks out behind the motor |
| Body | Ø80 x 92 mm outrunner; the main build is about 515 mm long | the covers and end cap, with 3 mm of spin clearance to the end cap |
| Leads | three phase leads and the thermistor leads through a 12 mm grommet in the face plate, along the notches in the corner gussets, to the controller | lead exit, gauge and length |
| Temperature | a 10 k NTC on the stator to the controller's thermistor input | that your motor has room for it, or its own sensor |
| Controller | ODrive Pro: 80 A with active cooling (datasheet), 100 A for 3 s, 58 V maximum. ODESC V4.2 (budget build): 70 A by the seller, unverified | the current your motor needs at your target force, held through a set |

How to judge a motor:

- **Cable force ≈ motor torque ÷ drum rope radius** (12.7 mm on the main build's 7/8 in drum). 220 lb (979 N) needs about
  12.4 N·m.
- **Current ≈ torque ÷ torque constant**, with the torque constant about 8.27 ÷ Kv N·m per amp. At 50 Kv, 12.4 N·m takes
  about 75 A: inside the ODrive Pro's 80 A. A smaller drum lowers the current but raises the felt mass.
- **Felt inertia:** through the 12.7 mm radius, a rotor's inertia J (kg·m²) feels like about 6,200 x J kg at the rope. A
  lighter rotor feels better; the firmware can cancel part of it, but not all. The 10 lb minimum should feel like 10 lb:
  keep the felt mass under about 6.4 kg before compensation (no more than about 30 % for the firmware to cancel).
- **Heat:** the rating is held through a 20-30 s set. Check the motor's copper loss at that current and how many sets it
  takes to reach the thermistor's limit.
- Prefer low-voltage (48 V or less) DC brushless motors with a high pole count, close to the reference size. Avoid hub
  motors (their rotors feel like a flywheel) and high-voltage AC servos: at this torque they are far larger and heavier than
  the body, or they need a reduction stage, which spoils the back-drive feel.
- A larger motor or a different Kv does not by itself make a safe resistance rating. The shared parts (frame, drum,
  level-wind, exit and rack side) are sized by calculation for 220 lb, and the drum and level-wind for 234 lb (the most the
  ODrive's 80 A can pull); nothing is checked above that, and none of it is tested yet.

After a motor change, update the motor, encoder, current and thermal settings before any powered test
([firmware-setup.md](firmware-setup.md)).

## A knob instead of the touch screen

The budget build already does this: an EC11 rotary encoder with a push button and a flush start/stop button, and a phone
app (Bluetooth, through a XIAO ESP32-C3) handles the settings. On the main build the same change closes the screen window
and drops the screen and its frame. Whether the Raspberry Pi can also be left out depends on the control software, which is
not released yet.

## Sharing your changes

With the verified release the hardware is licensed CERN-OHL-S-2.0 (share-alike): if you distribute a modified version,
publish your modified design files under the same license. The KINETIQ and Kinetiq Gym names and logo are not licensed.
Contributions to the project open with the verified release.
