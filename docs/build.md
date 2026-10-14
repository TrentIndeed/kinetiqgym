# Build instructions

> **Draft build order.** This is the assembly order for the aluminum prototype being built now (October 2026). It has not
> been confirmed on hardware yet. Steps, screw lengths and torques will be checked, corrected and photographed on the
> prototype, then released with the verified CAD and build files. Read the
> [safety reference](https://kinetiqgym.com/docs/SAFETY.html) before you start.

Order matters: some parts cannot be reached once others are in. The steps describe the main build (APS 8072S motor, 10S
battery). Section 6 covers all five motors, and the Lite (wall-power) differences are at the end.

**What carries the load.** A bolted 6061 aluminum frame (base plate, rear plate and motor face plate, joined by screws and
three machined corner brackets) carries the rope load, together with the drum, the two machined bearing holders and the
rack side. Every joint is bolted. Printed parts bolt to the frame: the two end pieces, the level-wind, the exit, the
screw-end tower, the gears, the brackets and the covers.

## 0. Before you start

1. Read the [safety reference](https://kinetiqgym.com/docs/SAFETY.html). The machine stores energy in the rope, the battery
   and the motor.
2. Order the parts for your build from the [parts list](https://kinetiqgym.com/docs/BOM.html). Some motors are wound to
   order, the battery packs are built to order, and the BMS, fuses and coupling come from different sellers.
3. Tools you need:
   - a drill (a drill press helps), a bench vise, and 2.5 and 3.3 mm drills;
   - M3 and M4 taps with a tap handle, plus M2.5 and M10 taps if your laser or CNC service does not tap those holes;
   - 3, 4 and 8 mm H7 reamers (unless your service reams the latch-pin holes), and a vise or arbor press for the dowel pins;
   - a 3D printer with a 256 x 256 mm bed that prints PAHT-CF (a hardened nozzle and a filament dryer);
   - a soldering iron with heat-set insert tips;
   - metric hex keys (one ball-end), a 7 mm socket, and a torque driver that reads 75 in-lb;
   - a crimper for ferrules and ring terminals, a soldering iron for the BMS pads, and a multimeter;
   - calipers, a deburring tool, and (MP80100 and C80100 only) a bimetal hacksaw and a file.
4. Print the fit coupons in the material you will use and tune the insert and clearance holes before the large prints
   ([printing.md](printing.md)). Print the drill guides as well: section 1 needs them to drill the metal.
5. Measure what you bought: both battery packs (the bay opening is 44 mm), the motor's shaft, bolt pattern and lead exit,
   and the flange of the F6001 exit bearings (1.5 mm is assumed).

## 1. Make the metal and print the parts

### Cut and machine

1. Laser-cut the 6061-T6 plates:
   - 0.250 in: the base plate (with its two floor ears), the motor face plate (two bolt circles and a Ø16 mm shaft hole),
     the two drum flanges and the latch slider;
   - 0.375 in: the rear plate (four keyholes for the rack studs);
   - 5/16 in: the two rack cheeks (the right one is notched round two stud tips);
   - 1.5 mm (1/16 in) sheet: the trigger link;
   - 2 mm steel: the four bearing cheeks.
2. Machine the two drum bearing holders from 6061-T6: an 8.4 mm upright on four 4 mm feet, a 28 H7 bore
   (28.000-28.021 mm) for the 6001 bearing, two 3.4 mm holes for the cheek bolts, and the four feet tapped M4. Mill the
   bore after a test cut.
3. Machine the three corner brackets (6061-T6, 6.35 mm web, each with a notch for the motor phase leads).
4. Machine the rack side's 3/4 in mating plate: 4 x M10 (drilled 8.5 mm and tapped through), a 5 mm deep slot across its
   back for each cheek, the keeper pocket at its left edge, and three countersunk M4 holes per cheek from its front face.
5. Cut the two motor face plate brackets from 1 x 1 x 1/4 in 6061 angle: each 16 mm wide, with the upright leg trimmed to
   16 mm tall so it stays under every motor's screw heads. Drill and tap one M4 hole in the foot and one in the leg.
6. Cut the drum tube (6061-T6, 1-1/4 in OD x 0.250 in wall) square to 100 mm.
7. Tap, ream and countersink the plate holes:
   - base plate: 3 x M3 for the rail and 2 x M3 for the fuse-block pad; countersink every hole a screw enters from below
     (including the six rear-plate screws and the two face-plate bracket screws);
   - rear plate: the two 4 mm H7 and one 8 mm H7 latch-pin holes (through), two blind 3 mm holes in its outer face for the
     trigger-link pins, and two countersunk M3 holes for the face plate's back edge;
   - motor face plate: two M4 holes countersunk on the motor side, for the bracket legs;
   - drum flanges: four M3 holes each on a 12.7 mm radius (between the hub's M4 holes), countersunk on the outer face, for
     the tube screws. The left flange also takes 4 x M4 (hub) and 4 x M3 (rope clamp), tapped, and three 4.5 mm lacing
     holes: deburr and round both edges of these (about 0.5 mm);
   - latch slider: 2 x M2.5 for the trigger-link screws.

### Drill and tap the edge holes

A few holes go into the edge of a plate or the end of the tube, where a laser cutter cannot reach. Drill them by hand
through the printed drill guides ([printing.md](printing.md)):

1. Clamp the part in a vise, edge up.
2. Slip the guide over the edge and push it against its end stop (the tube guide is centered by a boss in the bore).
3. Drill through each guide bore with the tap drill, at least to the depth in the table.
4. Tap by hand with the tap handle, clearing the chips often. Deburr, and check each hole with its screw.

| Part and edge | Holes | Drill | Thread and depth | Guide located by |
|---|---|---|---|---|
| Rear plate, bottom edge (0.375 in) | 6 | 3.3 mm | M4, 12 mm deep | an end stop on the plate's motor end |
| Motor face plate, back edge (0.250 in) | 2 | 2.5 mm | M3, 10 mm deep | an end stop on the plate's bottom edge |
| Each rack cheek, front edge (5/16 in) | 3 | 3.3 mm | M4, 14 mm deep | an end stop on the cheek's bottom edge |
| Drum tube, each end | 4 | 2.5 mm | M3, 9 mm deep | a boss that centers it in the bore |

Every screw that goes into these holes gets **Loctite 243** at assembly.

### Print

Print the parts listed in [printing.md](printing.md): PAHT-CF for the level-wind, exit, tower and gears, PA-CF for the end
pieces, PETG-CF for the covers, and PETG or PLA for the drill guides. Print the screw-end tower on its side.

### Heat-set inserts

The insert pockets are cut for the 3DZWMAN 380-piece insert kit. Press each insert in square to the face with the soldering
iron and an insert tip. Most go in on the bench before the part is fitted; the steps below say when.

## 2. Frame and end pieces

The frame is bolted together. Assemble it first:

1. Base plate on the bench, top up.
2. Rear plate onto the base plate's back edge, flush at the back: 6 x M4 x 18 countersunk up through the base plate into its
   bottom edge, heads flush underneath, **Loctite 243**. Snug them only. They are tightened in step 18, after the corner
   brackets are in: the brackets carry the joint's bending.
3. Motor face plate brackets: the two angle brackets on the base plate, 1 x M4 x 12 countersunk up through the base plate
   into each foot.
4. Motor face plate down onto the brackets, against the rear plate: 1 x M4 x 12 countersunk from the motor side through the
   face plate into each bracket leg, and 2 x M3 x 18 countersunk from outside through the rear plate into the face plate's
   back edge. All flush, **Loctite 243** on all. Square the face plate to the base plate before tightening.

Build the battery-end piece on the bench:

5. Push the captive M5 nut into the hex pocket under its floor (for the fuse block's battery-end bolt).
6. Main fuse: the Blue Sea 5191 MRBF block on its printed pad (the pad's rails take its raised section), then the 40 A MRBF
   fuse over the stud. The pad insulates the block (pack +) from the aluminum base plate.
7. Battery-end bolt: M5 x 14 socket head and a fender washer, loose. Two ring terminals go under the washer when wiring.
8. M8 nut on the fuse stud, loose until wiring (75 in-lb maximum).
9. Heat-set the WAGO bracket inserts into the bay wall, and the three M4 inserts into the inner lap (the top strip over the
   rack studs' heads).
10. Lower the WAGO bracket onto the bay wall from above: 2 x M3. It sits over the fuse stud, so the fuse goes on first.

Motor end:

11. Motor-end piece (floor, rear wall, handle loop and rear housing) against the frame. Its rear housing lies on the outside
    of the rear plate.
12. Housing land: 6 x M4 x 25 countersunk through the land and the rear plate, washer and nyloc nut inside. The heads sit
    flush; the service lid covers them later.
13. Heat-set the four M2 inserts for the service lid into the housing land.
14. Latch pins. Press the two 3 x 18 mm link pins through the housing land into the blind holes in the rear plate. Press
    the two 4 x 16 mm slider guide pins and the 8 x 16 mm anvil pin through the rear plate from inside, flush with its
    inner face. Support the plate round each hole while pressing.

Corner brackets (they go in before the bearing holders and the drum, which cover their foot screws):

15. Set the three corner brackets in the inside corner beside the lower stud columns, each on the base plate and against
    the rear plate's inner face. The notch at the corner is for the motor phase leads.
16. Feet: 1 x M5 countersunk up from under the base plate through each foot (flush), washer and nut on the foot. Back legs:
    2 x M5 countersunk from outside through the rear plate and each leg (flush), washer and nut inside. Nothing is tapped.
17. Snug the foot nuts, then the back nuts, then tighten all. Each bracket must bear on both plates.
18. Now tighten the six rear-plate screws from step 2.

Battery end:

19. Slide the battery-end piece (floor, step wall, bay wall, saddles, fuse block and WAGO bracket) in from the right against
    the frame. Its lap strip slides along the inside of the rear plate.
20. Battery-end lap: 3 x M4 countersunk through the outer top land and the rear plate into the inner lap's inserts.
21. Floor ears: one M4 x 18 countersunk up through each base-plate ear and the printed seat over it (head flush
    underneath), then a washer and an M4 nut inside. Tighten with a hex key below and a 7 mm socket above. Do this now:
    the boards, the motor and the screw-end tower cover them later.
22. Fuse-block pad: 2 x M3 socket head down through its bosses into the tapped base plate. There is no room for a nut. Do
    this before the ODrive and the wiring.

## 3. Level-wind rail and traveller

The drum module comes down over the rail, so the rail goes in first.

1. MGN15 rail (200 mm) straight on the base plate: 3 x M3 into the tapped holes. Leave its two end holes free: the screw
   stand and the tower bolt through them later.
2. Slide the MGN15H carriage on from the rail's end. Keep its plastic retainer in until it is on the rail, or the balls
   fall out.
3. Printed traveller frame onto the carriage: 4 x M3 x 8 through the access holes (before the rollers).
4. Travelling rollers: two 626ZZ per roller, between the frame plates. Each pair rests on its inner ring on a 0.9 mm boss,
   so the outer rings run clear.
5. Roller shoulder bolts (ISO 7379, 6 x 16 mm) down from the top, heads sunk.
6. T8 brass flange nut into the frame's nut block: 4 x M3 x 10 low-head screws.

## 4. Drum module

Build the drum module on the bench and lower it in as one piece.

1. Drum: clean the tube's end faces, put **Loctite 638** on both, and set a flange on each end (the left flange is the one
   with the hub and rope-clamp holes). 4 x M3 x 12 countersunk through each flange into the tapped tube end,
   **Loctite 243**, flush.
2. Square the flanges: slide the 12 mm drum shaft through both flange holes while the 638 is wet, then tighten the flange
   screws. Slide the shaft back out once they are tight; it goes back in at step 7. The drum needs 24 h before any load.
3. Drill the four M4 holes of one goBILDA 1301 hub out to 4.4 mm, so its screws clamp it to the flange.
4. Turn that hub over: flat face on the left flange, spigot toward the bearing. 4 x M4 x 12 button head into the tapped
   flange. The hub drives the drum through these four preloaded screws.
5. Rope termination: from the barrel side, pass the rope end out through lacing hole 1 (above the hub), along the outer
   face and back in through hole 2, across the inner face and out through hole 3. That makes two U-turns round the
   aluminum.
6. Rope clamp ring over the hub onto the left flange, both outer runs in its grooves: 4 x M3 x 12 countersunk, flush, into
   the tapped flange. Snug the screws, pull the rope back through the lacing until it is tight, tie an overhand stopper
   knot (7 mm at most) in the tail, seat it in the pocket at the end of the tail groove, trim, then tighten. The dead wraps
   and the two metal U-turns leave the clamp about 7 % of the pull.
7. Shaft (12 mm round, 200 mm, uncut): slide it through the hub and both flanges with **Loctite 638** in the hub bore and
   in both flange holes. Set it flush with the gear hub's position at the right end; about 22 mm then sits in the coupling.
   Tighten the hub clamp. **Leave it 24 h before any load**: a clamp alone slips at about 6-8 N·m, and the drum sees up to
   17.1 N·m.
8. Encoder magnet (diametric, 6 x 5 mm) into the right shaft end: epoxy, centered.
9. Each bearing holder on the bench: the inner steel cheek; the 6001-2RS into the holder with **Loctite 641** on its outer
   ring (by hand, or a light press on the outer ring only); the outer cheek; 2 x M3 x 16 with nuts.
10. Slide the two holders onto the shaft ends with **Loctite 641 on the shaft under each inner ring**. The rope load turns
    with the shaft, so a loose inner ring would creep. The 641 gives about 10 minutes of working time: do steps 11-14
    within it.
11. Drum 81T gear on its hub (the second 1301 hub) onto the right shaft end, after the right holder. It drives the lead
    screw at 81T : 45T, 3.6 mm of traverse per drum turn.
12. Ruland coupling onto the left shaft end, loose.
13. Lower the module onto the base. The holder feet sit over their eight holes.
14. 8 x M4 x 10 countersunk up through the base plate into the tapped holder feet, **Loctite 243**, heads flush underneath.
    Snug them only: the shafts are lined up when the motor goes in (section 6).

## 5. Front board plate

The board plate goes in before the motor, which sits over its screws.

1. Heat-set the board plate's inserts.
2. Board plate onto the base plate: 2 x M3 socket head up from below.
3. Printed standoffs, then the regulator, Teensy and CAN perfboards: M2.5 through each board and standoff into the plate's
   inserts. **Screw the Teensy perfboard down before plugging the Teensy into its sockets**: two of its screws sit under
   the Teensy.

## 6. Motor

All five builds use the same face plate, which is drilled for both bolt patterns. Direct drive: the motor turns the drum
through the coupling, with no belt or gear between them.

| Motor | Spacers | Screws | Coupling |
|---|---|---|---|
| APS 8072S (main, Lite) | 4 x M5, 10 x 3 mm | 4 x M5 x 14 on the Ø59 mm circle | Ruland MCLX-12-10-F |
| MP80100, APS C80100 | 4 x M5, Ø10 x 10 mm | 4 x M5 x 25 on the Ø56 mm circle | Ruland MCLX-12-12-F |

1. MP80100 and C80100 only: on the bench, cut the bell-end shaft (Ø12 mm, threaded M12) to a 10 mm stub. A bimetal
   hacksaw blade (24-32 TPI) does it in a few minutes; if it skates, the shaft is hardened, so use a cut-off wheel. Wrap
   the motor in tape or a bag first so no filings reach the magnets. Hold the shaft or the finned stator end in a padded
   vise, never the can (it is the rotor). File the end and pick up any dust with tape.
2. Motor spacers against the face plate.
3. Motor in from the left, its shaft into the coupling. Lead the three phase leads out through the 12 mm grommet in the
   face plate.
4. Motor screws through the plate and the spacers.
5. Line up the shafts. The face plate is bolted to the frame, so the shafts are lined up at the bearing holders: their foot
   holes give about ±0.35 mm. Snug the holder feet, tighten both coupling clamps, then tighten the holder feet.

## 7. Lead screw and timing the level-wind

The traveller rides on the rail and is driven by the lead screw, which is geared to the drum (81T : 45T, Tr8 x 2): it moves
3.6 mm per drum turn and lays the rope side by side on the drum.

1. Far-end screw stand: heat-set the M3 insert into its front leg and push an M3 nut into the slot in its foot (from the
   left). It stands on the rail's left end; its foot is the carriage's hard stop at full payout.
2. Stand screws: 2 x M3 countersunk up through the plate, one into the front leg's insert, one through the rail's end hole
   into the foot's nut.
3. 688ZZ into the stand from the right, against its lip, with a drop of **Loctite 641** on its outer ring (the seat has one
   lip; the 641 keeps the bearing from walking out). This end floats: radial support only.
4. Screw-end tower (printed PAHT-CF, printed on its side): heat-set its four M4 inserts into the foot. It stands on the
   rail's right end and takes the screw's thrust (about 636 N at 158 lb).
5. Tower screws: 4 x M4 countersunk up through the base plate, and 1 x M3 up through the plate, the rail's end hole and the
   foot, with a washer and nut on top.
6. MR128ZZ into the tower wall, centered (Loctite 641 or a press fit). It sits 0.66 mm short of each face, so the thrust
   washers bear on the wall and never on the bearing.
7. On the bench, bolt the 45T gear to the goBILDA Sonic Hub: 4 x M4 x 12 button head on the 16 mm pattern, the gear on the
   hub face toward the drum.
8. Lower the gear and hub in 8 mm left of the drum gear, through the notch in the tower web, then slide them 8 mm right
   into mesh with the 81T. Hold them there until the screw is through.
9. Inner F8-16M thrust bearing between the hub and the tower: the washer with the larger bore goes against the tower (it
   stays still); the snug one turns with the screw. The outer one goes the same way round.
10. Lead screw (Tr8 x 2, 200 mm, uncut) in from the right: through the tower, the thrust bearing and the hub, then turn it
    through the T8 nut and into the far-end 688. It ends about 25 mm past the stand.
11. Outer F8-16M and the 8 mm collar: push the collar against the bearing and tighten its set screw.
12. **Time the level-wind.** Wind the three dead wraps on by hand, side by side, ending one wrap before the start of the
    track. The rope's lead from the anchor crosses the bare barrel behind them. Turn the screw until the traveller's
    rollers sit on the rope where it leaves the bottom of the drum at the start of the track.
13. With the traveller in time, tighten the Sonic Hub's two pinch bolts. From then on the gears keep the traveller in
    step, and the collar and the hub hold the screw against the two thrust bearings.

## 8. Exit bracket and top tie

1. Fixed roller bracket on the bench: heat-set its inserts (4 x M3 in the front face, 2 x M5 in the top plate, 2 x M4 in
   the back face); push 3 x M4 nuts into the foot slots from the back.
2. Fixed rollers: two 626ZZ per roller into the bracket pockets, each pair on its 0.9 mm boss (inner ring only).
3. Fixed-roller shoulder bolts (6 x 16 mm) up from under the foot, through the access bores, into the top-plate inserts.
4. Bracket down onto the front edge of the base plate, in front of the carriage: 3 x M4 countersunk up through the plate
   into the foot nuts. Its flange is the exit's structure.
5. Top tie over the traveller and the drum: 2 x M4 down into the bracket's inserts (ball-end hex key from above).
6. Tie rear screws: 2 x M4 x 18 countersunk from the back, flush in the rear plate, through the plate and the tie, washer
   and nut on the tie. The tie carries the exit load to the rear wall, so it is bolted through, not screwed into inserts.

## 9. Electronics, battery and harness

1. ODrive bracket: an M3 nut into the slot in each foot first, then slide it in from the right: 2 x M3 countersunk up
   through the plate into those nuts.
2. ODrive Pro with its heat spreader and terminal block: 4 x M4 x 12 through the spreader into the bracket, nuts in the
   bracket pockets.
3. WAGO 221-615 lever nut into its bracket.
4. Battery bay: stick the 1 mm EVA hold-down pads under the two cradle roofs. For the TP2700 pair, put the printed spacer
   in first (its 4 mm plate against the outer panel, its 12 mm block at the front).
5. Pack A (bottom) in from the front through the cradle, leads first; then the 2 mm EVA separator; then pack B (top). The
   opening is 44 mm, about 0.5 mm a side for the TP3300 (43 mm by the maker's estimate).
6. Wire the harness: follow [wiring.md](wiring.md). At the main fuse, pack + and the charge lead go on ring terminals under
   the battery-end washer (M5, tongues to the front); ODrive DC+ (tongue to the right) and the regulator feed go on the
   output stud under the M8 nut, **75 in-lb maximum**. Fit the block's insulating cover. Leave the Pi, screen, BMS and fan
   leads ready to plug in as the covers come down. Plug the pack connectors in only with the BMS switched off.

## 10. Covers, exit and rope

On the bench:

1. The left cover (screen side, motor end cap printed in) and the right cover (exit, grille, battery end cap printed in).
   Heat-set the cover inserts.
2. Battery front pad: 2 mm adhesive EVA (or a TPU print) inside the right cover's front wall, over the packs' end faces. It
   holds the packs against the rear rib.
3. Screen into the front window, then its bezel and the screen retaining frame: 2 x M3 x 8 countersunk from the front.
4. Raspberry Pi up to its ceiling bosses in the left cover: M2.5 from below through the board.
5. BMS up to the right cover's ceiling: 4 x M3 x 12 countersunk from above, washers and nuts below.
6. Fan duct and the Noctua fan: 4 x M3 x 25 countersunk from the back.

On the machine:

7. Lower both covers onto the base. Plug in the Pi, the screen's flat HDMI cable and USB-C cable, the BMS and the fan leads as they come down.
8. Cover feet: M3 countersunk up from below.

Exit swivel, built on the bench right before it goes on:

9. Exit carrier: drop the three hub-retainer nuts in through the rope bore into their pockets, and the rail-clamp nuts into
   their rear pockets.
10. Exit pulleys: two F6001-2RS flanged bearings, flanges on opposite sides (the rope runs on the outer rings), on two
    ISO 7379 12 x 25 mm (M10) shoulder bolts through both cheeks.
11. On each axle, from the far side: two M12 washers over the shoulder, then an M10 washer and the nyloc nut, snug. The
    shoulder ends inside the M12 washers, so the nut clamps the pulleys' inner rings. If the nut bottoms first, add a third
    M12 washer.
12. The two 5 x 60 mm stainless side rails into their grooves, then the two printed rail caps: 6 x M3 x 8 countersunk,
    flush.
13. Exit bearing housing: the two 16008-2RS bearings in from the front, one after the other, then the front outer-race
    retainer.
14. Carrier hub through the bearing pair; the 2 mm rear inner-race retainer; 3 x M3 x 8 countersunk into the hub-retainer
    nuts.
15. Exit swivel onto the right cover's front wall (the housing's back stands on the wall): 4 x M3 x 40 countersunk, flush
    in the front retainer, through the housing and the wall into the fixed roller bracket's flange inserts.

Rope and rear:

16. Thread the rope from the bottom of the drum: between the travelling rollers, between the fixed rollers, into the exit
    on its axis, then between the pulleys and the side rails. It rises in one straight line (about 11°) and only runs over
    bearings. Wind it on under light tension.
17. Cover backs: M3 countersunk from the back into the cover bosses.
18. Charge port (XT60E-F) and the power switch into the rear I/O panel, then the panel into the back step. Charge port:
    2 x M2.5 x 5 countersunk (countersink the flange holes), self-tapping into the backing frame. Panel tabs: 2 x M2.5 x 5,
    self-tapping into the step wall.

## 11. Rear latch, trigger and service lid

1. On the bench, pass the guide rod through the spring and the slider bar. Push the slider toward the motor end to compress
   the spring, lower its arms' slots over the two guide pins, and let go: the spring pushes it home and the tongue rests on
   the anvil pin. The rod's end drops into its seat in the land.
2. Finger-bar nuts: 2 x M2.5 nuts and their washers into the channel in the land, under where the link lies.
3. Trigger link onto its two pins: 2 x M2.5 flat head through the link and the 3 mm spacers into the tapped slider bar
   (**Loctite 243**).
4. Service lid into its rim: 4 x M2 countersunk into the inserts. Its pads hold the link on its pins and its rib closes the
   spring channel.
5. Finger bar through the lid's slots onto the link: 2 x M2.5 socket head into the nuts under the link.
6. Check: slide the finger bar 12.7 mm toward the motor end and let it go. The slider should snap home.

## 12. Rack side and hanging the unit

The rack side stays on the rack. It fits a 3 x 3 in upright with 1 in pin holes.

1. Rack side, on the bench: stand each cheek's front edge in its slot across the back of the mating plate. 3 x M4 x 25
   countersunk from the plate's front face into each cheek's edge, **Loctite 243**, heads flush (they lie against the rear
   plate).
2. Screw the four shoulder studs (ISO 7379, 12 x 12 mm, M10 x 16) into the mating plate, a 2 mm shim under each head,
   **Loctite 243**.
3. Rack side onto the rack: its two cheeks round the upright, the rack's 1 in pin through both cheeks and the upright, clip
   fitted. The mating plate's back face bears on the upright. A hitch pin needs at least 92 mm between its head and its
   clip hole.
4. Pull the trigger: the finger bar 12.7 mm toward the motor end. The tongue retracts. Hold it there.
5. Offer the unit up: the four stud heads through the keyhole entries until the rear plate sits flat on the mating plate.
6. Lower the unit 12 mm. The stud necks drop into the keyhole tops.
7. Let the trigger go: the spring pushes the tongue into the mating plate's pocket. Check that the unit cannot lift.

To take the unit off: pull the trigger, lift it 12 mm, and pull it back.

## 13. Before powering

A finished assembly is not a training-ready machine. Before the motor is powered with the rope attached:

1. Work through [firmware-setup.md](firmware-setup.md): limits, calibration, homing and the payout window.
2. Follow the first power-up and load-test steps in the
   [safety reference](https://kinetiqgym.com/docs/SAFETY.html).
3. Wait at least 24 h after the Loctite 638 step before loading the drum.

The control software (Pi app, Teensy firmware, phone app) is released after the prototype has been tested.

## Lite build differences

The Lite uses the same frame, rack side, drivetrain, level-wind, exit and motor body as the main build. The motor is an
APS 8072S wound to about 25 Kv, and it runs from the wall.

**Left out:** the battery packs, pads and spacer, the BMS, the main fuse block and its pad, the WAGO and its bracket, the
charge port, the rear I/O panel, the power switch, the Raspberry Pi, the screen and its frame, the Teensy, and the ODrive Pro
with its terminal block (its bracket stays).

**Added:**

1. Section 3, before the rail: the two 50 W, 1 Ω brake resistors flat on the base plate, thermal paste under each,
   2 x M3 into the tapped plate for each. The base plate is their heatsink.
2. Section 3: the earth stud. An M4 ring terminal (the green-yellow leads crimped on) and a star washer, M4 into the tapped
   base plate. Check continuity from the inlet's earth pin to the base plate and to the rear plate.
3. Section 5: the XIAO ESP32-C3 on the perfboard in place of the Teensy.
4. Section 9: solder the ODrive S1's power, phase and brake leads to its pads first. Then, on the bench, the S1 on its
   6061 plate (thermal pad between them, 4 x M3 into the tapped plate), and the plate onto the ODrive bracket with the
   same 4 x M4 x 12 and nuts.
5. Section 9: the power supply tray (heat-set its four M3 inserts and its two floor inserts first) down into the battery
   bay, 2 x M3 into the floor inserts. Then the Mean Well LOP-600-36 onto the tray bosses, solder side to the tray, with
   4 x M3 into the tray inserts. The back-bottom screw (the supply's earth) takes a star washer and the two earth ring
   terminals.
6. Section 10: the knob encoder (EC11) through the left cover's front from inside, its M7 nut outside, then the knob. The
   C14 inlet and the rocker switch snap into the right cover's back step from outside. Put the mains leads on their tabs
   before the cover is lowered.

The Lite's mains and DC wiring are summarized in [wiring.md](wiring.md).
