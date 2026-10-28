# Build instructions

> **Draft build order.** This is the assembly order for the main build as designed now (October 2026). It has not been
> confirmed on hardware yet. Steps, screw lengths and torques will be checked, corrected and photographed on the
> prototype, then released with the verified CAD and build files. Read the
> [safety reference](https://kinetiqgym.com/docs/SAFETY.html) before you start.

Order matters: some parts cannot be reached once others are in. The steps describe the main build (Freerchobby MP8085
motor, ODrive Pro, 10S battery). The budget build is a separate, simpler design: see the end of this page.

**What carries the load.** A bolted 6061 aluminum frame (base plate, rear plate and motor face plate, joined by screws and
three corner gussets) carries the rope load, together with the drum, the two bearing holders and the rack side. Nothing is
welded or turned on a lathe, and every load-bearing screw goes to a nut: a nut in a window cut through the plate, in a
pocket, or keyed in a notch in the drum tube's end. Printed parts bolt to the frame: the two end pieces, the level-wind,
the exit, the screw-end tower, the gears, the brackets and the covers.

## 0. Before you start

1. Read the [safety reference](https://kinetiqgym.com/docs/SAFETY.html). The machine stores energy in the rope, the battery
   and the motor.
2. Order the parts for your build from the [parts list](https://kinetiqgym.com/docs/BOM.html). The motor ships from its
   maker, the battery packs are built to order, and the BMS, fuses and coupling come from different sellers.
3. Tools you need:
   - a drill (a drill press helps), a bench vise, and 3.4 and 4.5 mm drills for the edge holes;
   - M2.5, M3 and M10 taps with a tap handle, only if your laser or CNC service does not tap the few holes that are still
     threaded (the latch slider, the fuse-block pad and the two ball plungers): none of them is in the rope's load path;
   - 3, 4 and 8 mm H7 reamers (unless your service reams the latch-pin holes), and a vise or arbor press for the dowel pins;
   - a hacksaw, a file and an abrasive cut-off wheel (the shaft, the rail and the motor's rear shaft are cut to length);
   - a 3D printer with a 256 x 256 mm bed that prints PAHT-CF (a hardened nozzle and a filament dryer);
   - a soldering iron with heat-set insert tips;
   - metric hex keys (one ball-end), a 7 mm socket, and a torque driver that reads 75 in-lb;
   - a crimper for ferrules and ring terminals, a soldering iron for the BMS pads, and a multimeter;
   - calipers and a deburring tool.
4. Print the fit coupons in the material you will use and tune the insert and clearance holes before the large prints
   ([printing.md](printing.md)). Print the drill guides and the tube-end guide as well: section 1 needs them.
5. Measure what you bought: both battery packs (the bay opening is 44 mm); the motor's shaft, keyway, rear hub, lead exit and
   the depth of its four M5 threads; the flange of the F6001 exit bearings (1.5 mm is assumed); and the toggle clamp's flange
   holes and outline before the rack side's mating plate is cut.

## 1. Make the metal and print the parts

### Cut and machine

1. Laser-cut the 6061-T6 plates:
   - 0.250 in: the base plate (with its two floor ears and the slots for the face plate's and holders' tabs), the motor face
     plate (two tabs, the bolt circles, a Ø16 mm shaft hole and five nut windows), the two drum flanges and the latch slider;
   - 0.375 in: the rear plate (four keyholes for the rack studs, with V tops and narrow throats, and its nut windows);
   - 1.5 mm (1/16 in) sheet: the trigger link;
   - 2 mm steel: the four bearing cheeks.
2. Mill on the base plate's underside the ten hex pockets for the rail's M4 nuts, and on its top the 1.5 mm deep pocket for
   the MGW15 rail.
3. Mill the two drum bearing holders from 3/8 in 6061-T6: face them to 8.4 mm, a 28 H7 bore (28.000-28.021 mm) for the
   6001 bearing, a tab for the slot in the base plate, two nut windows near the bottom edge, and two 3.4 mm holes for the
   cheek bolts. Mill the bore after a test cut.
4. Cut the three corner gussets from 1/4 in 6061-T6, each with four nut windows and a notch for the motor phase leads.
5. Mill the rack side:
   - the 3/4 in mating plate: four stud seats (a 10.2 mm hole with a 12.03 mm counterbore 2 mm deep), a hex pocket in its back
     for each stud's DIN 439 M10 thin nut, the latch's keeper pocket, a 3 mm slot across its back for each cheek, and the
     pockets for the toggle clamp's four M6 nuts and its pad bar;
   - the two 1/2 in cheeks: the 1 in pin hole, three nut windows each, and the three M5 holes from the front edge into them;
   - the pad bar, 6061, 83 x 34 x 12.7 mm, with a blind hole for the clamp's spindle.
6. Mill the ODrive heatsink from a 1/2 in 6061 offcut: 15 fins along the fan's flow, the stepped bore round the drum hub,
   and a slot in its foot for an M3 nut.
7. Cut to length. Nothing is turned: every round part is used at the size it is bought.
   - the drum tube (6061-T6, 7/8 in OD x 1/8 in wall), square, to 162 mm;
   - the 12 mm shaft, from 300 mm to 262 mm, with a cut-off wheel;
   - the MGW15 rail, from 250 mm to 213 mm, with an abrasive cut-off wheel; deburr the end;
   - the Tr8 lead screw, from 250 mm to 245 mm; clean up the thread's end so the nut starts.
8. Drum tube ends: through the printed tube-end guide (a boss centers it in the bore), drill four 4.5 mm holes 6 mm deep
   into each end on the hub's 16 mm square, then saw and file the four nut notches through the wall to the guide's side
   marks. The M4 nuts in them key the flanges and hub to the tube: nothing is tapped.
9. Finish the plate holes:
   - rear plate: the two 4 mm H7 and one 8 mm H7 latch-pin holes (through), two blind 3 mm holes in its outer face for the
     trigger-link pins, and the two M10 threads for the ball plungers;
   - drum flanges: the countersinks on the outer faces; the left flange also takes three 4.5 mm lacing holes: deburr and
     round both edges of these (about 0.5 mm);
   - latch slider: 2 x M2.5 for the trigger-link screws;
   - base plate: 2 x M3 for the fuse-block pad (there is no room for a nut there; it carries no rope load);
   - countersink every hole a screw enters flush.

### Drill the edge holes

A few holes go into the edge of a plate, where a laser cutter cannot reach. Each one runs from the edge into a window cut
through the plate, where its nut sits: nothing in the load path is tapped. Drill them by hand through the printed drill
guides ([printing.md](printing.md)):

1. Clamp the part in a vise, edge up.
2. Slip the guide over the edge and push it against its end stop.
3. Drill through each guide bore with the clearance drill, to the depth in the table: into the window.
4. Deburr, and check each hole with its screw and nut.

| Part and edge | Holes | Drill and depth | Guide located by |
|---|---|---|---|
| Rear plate, bottom edge (0.375 in) | 6 x M4 | 4.5 mm, 13.6 mm deep | an end stop on the plate's motor end |
| Motor face plate, back edge (0.250 in) | 2 x M3 | 3.4 mm, 11.8 mm deep | an end stop on the plate's bottom edge |
| Motor face plate, bottom edge (0.250 in) | 3 x M3 | 3.4 mm, 11.8 mm deep | an end stop on its front end; its two tabs sit in pockets in the guide |
| Each drum bearing holder, bottom edge (3/8 in) | 2 x M4 | 4.5 mm, 13.6 mm deep | an end stop on its front end; the tab in a pocket |
| Each corner gusset, bottom edge (1/4 in) | 2 x M3 | 3.4 mm, 10.8 mm deep | an end stop on the toe's front end |
| Each corner gusset, back edge (1/4 in) | 2 x M3 | 3.4 mm, 11.8 mm deep | the notch's top face |

### Print

Print the parts listed in [printing.md](printing.md): PAHT-CF for the level-wind, exit, tower and gears, PA-CF for the end
pieces, PETG-CF for the covers, and PETG or PLA for the drill guides. Print the screw-end tower on its side.

### Heat-set inserts

The insert pockets are cut for the 3DZWMAN 380-piece insert kit. Press each insert in square to the face with the soldering
iron and an insert tip. Most go in on the bench before the part is fitted; the steps below say when.

## 2. Frame and end pieces

The frame is bolted together. Assemble it first:

1. Base plate on the bench, top up.
2. Rear plate onto the base plate's back edge, flush at the back. An M4 nut into each of the six windows near its bottom edge
   (from inside), then 6 x M4 countersunk up through the base plate into those nuts, heads flush underneath. Hold each nut
   with a finger or a 7 mm wrench. Snug them only: they are tightened after the corner gussets are in, which carry the
   joint's bending.
3. Motor face plate down into its two slots in the base plate, against the rear plate. An M3 nut into each of its five
   windows (from the drum side), then 3 x M3 countersunk up through the base plate and 2 x M3 countersunk through the rear
   plate into them. All flush. Square the face plate to the base plate before tightening.

Build the battery-end piece on the bench:

4. Push the captive M5 nut into the hex pocket under its floor (for the fuse block's battery-end bolt).
5. Main fuse: the Blue Sea 5191 MRBF block on its printed pad (the pad's rails take its raised section), then the 40 A MRBF
   fuse over the stud. The pad insulates the block (pack +) from the aluminum base plate.
6. Battery-end bolt: M5 x 14 socket head and a fender washer, loose. Two ring terminals go under the washer when wiring.
7. M8 nut on the fuse stud, loose until wiring (75 in-lb maximum).
8. Heat-set the WAGO bracket inserts into the bay wall, and the three M4 inserts into the inner lap (the top strip over the
   rack studs' heads).
9. Lower the WAGO bracket onto the bay wall from above: 2 x M3. It sits over the fuse stud, so the fuse goes on first.

Motor end:

10. Motor-end piece (floor, rear wall, handle loop and rear housing) against the frame. Its rear housing lies on the outside
    of the rear plate.
11. Housing land: 6 x M4 countersunk through the land and the rear plate, washer and nyloc nut inside. The heads sit flush;
    the service lid covers them later.
12. Heat-set the four M2 inserts for the service lid into the housing land.
13. Latch pins. Press the two 3 x 18 mm link pins through the housing land into the blind holes in the rear plate. Press
    the two 4 x 16 mm slider guide pins and the 8 x 16 mm anvil pin through the rear plate from inside, flush with its
    inner face. Support the plate round each hole while pressing.

Corner gussets (they go in before the bearing holders and the drum, which cover their bottom screws):

14. An M3 nut into each of a gusset's four windows, then set it in the inside corner beside a lower stud column, on the base
    plate and against the rear plate's inner face. The notch at the corner is for the motor phase leads. Do the same with
    the other two.
15. Each gusset: 2 x M3 countersunk up from under the base plate into its bottom nuts, and 2 x M3 countersunk from outside
    through the rear plate into its back nuts, all flush, **Loctite 243**. Snug the bottom screws first, then the back ones,
    then tighten all: each gusset must bear on both plates.
16. Now tighten the six rear-plate screws from step 2.

Battery end:

17. Slide the battery-end piece (floor, step wall, bay wall, saddles, fuse block and WAGO bracket) in from the right against
    the frame. Its lap strip slides along the inside of the rear plate.
18. Battery-end lap: 3 x M4 countersunk through the outer top land and the rear plate into the inner lap's inserts.
19. Floor ears: one M4 x 18 countersunk up through each base-plate ear and the printed seat over it (head flush
    underneath), then a washer and an M4 nut inside. Tighten with a hex key below and a 7 mm socket above. Do this now:
    the boards, the motor and the screw-end tower cover them later.
20. Fuse-block pad: 2 x M3 socket head down through its bosses into the base plate's two threaded holes. Do this before the
    ODrive and the wiring.

## 3. Level-wind rail and traveller

The drum module comes down over the rail, so the rail goes in first.

1. An M4 nut into each of the ten hex pockets under the base plate (a dab of grease holds it).
2. MGW15 rail (213 mm) into its pocket in the base plate: 10 x M4 x 6 socket head down through the rail into the nuts.
3. Slide the MGW15H block on from the rail's right end. Keep its plastic retainer in until it is on the rail, or the balls
   fall out.
4. Printed traveller frame onto the block: 2 x M4 x 10 into the block's front holes (hex key through the access holes,
   before the rollers). The back pair stays empty: at the ends of the track it passes under the drum flanges.
5. Travelling rollers: one NATR6-PP track roller per roller, between the frame plates. Each rests on its inner ring on a
   0.9 mm boss, so the outer ring runs clear.
6. Roller shoulder bolts (ISO 7379, 6 x 16 mm) down from the top, heads sunk.
7. T8 brass flange nut into the frame's nut block: 4 x M3 x 10 low-head screws.

## 4. Drum module

Build the drum module on the bench and lower it in as one piece.

1. Drum tube on the bench: an M4 nut into each of the four notches at each end (a dab of grease holds them).
2. Flanges: **Loctite 638** on both tube end faces, then the left flange (the one with the lacing holes, the lacing holes up)
   on one end and the right flange on the other.
3. Slide the 12 mm shaft through both flanges so they set square to it, then 4 x M4 x 12 countersunk through the right
   flange into its nuts, **Loctite 243**, flush. Tighten while the 638 is wet. Slide the shaft back out; it goes back in at
   step 8. The drum needs 24 h before any load.
4. Rope clamp screws: 4 x M3 x 14 countersunk into the left flange from its inner face (they stick out of its outer face).
5. One goBILDA 1301 hub, flat face on the left flange, spigot toward the bearing: 4 x M4 x 20 button head through the hub
   and the flange into the left tube-end nuts, **Loctite 243**. The hub drives the drum through these bolts; the nuts key
   the tube to the flange.
6. Rope termination: from the barrel side, pass the rope end out through lacing hole 1 (above the hub), along the outer
   face and back in through hole 2, across the inner face and out through hole 3. That makes two U-turns round the
   aluminum.
7. Rope clamp ring over the hub onto the left flange, both outer runs in its grooves and the four screws through it, an M3
   nut into each pocket. Snug the nuts, pull the rope back through the lacing until it is tight, tie an overhand stopper
   knot (7 mm at most) in the tail, seat it in the pocket at the end of the tail groove, trim, then tighten. The dead wraps
   and the two metal U-turns leave the clamp a small part of the pull.
8. Shaft (12 mm round, 262 mm): slide it through the hub and both flanges with **Loctite 638** in the hub bore and in both
   flange holes. Set it flush with the gear hub's position at the right end; about 21 mm then sits in the coupling.
   Tighten the hub clamp. **Leave it 24 h before any load**: a clamp alone can slip below the drum's torque at full load.
9. Encoder magnet (diametric, 6 x 5 mm) into the right shaft end: epoxy, centered.
10. Each bearing holder on the bench: the inner steel cheek; the 6001-2RS into the holder with **Loctite 641** on its outer
    ring (by hand, or a light press on the outer ring only); the outer cheek; 2 x M3 x 16 with nuts.
11. Slide the two holders onto the shaft ends with **Loctite 641 on the shaft under each inner ring**. The rope load turns
    with the shaft, so a loose inner ring would creep. The 641 gives about 10 minutes of working time: do steps 12-15
    within it.
12. Drum 81T gear on its hub (the second 1301 hub) onto the right shaft end, after the right holder. It drives the lead
    screw at 81T : 45T, 3.6 mm of traverse per drum turn.
13. The Ruland coupling onto the left shaft end, loose.
14. Lower the module onto the base: each holder's tab drops into its slot in the base plate.
15. An M4 nut into each of the two windows near each holder's bottom edge, then 2 x M4 countersunk up through the base plate
    into them, heads flush underneath. Snug them only: the shafts are lined up when the motor goes in (section 6).

## 5. Front board plate

The board plate goes in before the motor, which sits over its screws.

1. Heat-set the board plate's inserts.
2. Board plate onto the base plate: 2 x M3 socket head up from below.
3. Printed standoffs, then the regulator, Teensy and CAN perfboards: M2.5 through each board and standoff into the plate's
   inserts. **Screw the Teensy perfboard down before plugging the Teensy into its sockets**: two of its screws sit under
   the Teensy.

## 6. Motor

Direct drive: the motor turns the drum through the coupling, with no belt or gear between them.

1. On the bench, cut the motor's rear prop shaft flush with its rear hub (the hub is part of the rotor: it stays). A bimetal
   hacksaw blade (24-32 TPI) does it; if it skates, the shaft is hardened, so use a cut-off wheel. Wrap the motor in tape
   or a bag first so no filings reach the magnets. Hold the shaft or the stator end in a padded vise, never the can (it is
   the rotor). File the end and pick up any dust with tape.
2. Take the key out of the front shaft (the Ruland coupling clamps the round shaft).
3. Glue the 10 k NTC thermistor to the stator where the leads come out, with its leads alongside the phase leads.
4. The four Ø10 x 10 mm spacers against the face plate.
5. Motor in from the left, its shaft into the coupling. Lead the three phase leads and the thermistor leads out through the
   12 mm grommet in the face plate.
6. 4 x M5 x 25 socket head through the plate and the spacers into the motor's own M5 threads (4 x M5 on the Ø56 mm circle).
7. Line up the shafts. The face plate is bolted to the frame, so the shafts are lined up at the bearing holders: their tabs
   sit in slots with about 0.3 mm of play at each end. Snug the holder screws, tighten both coupling clamps, then tighten
   the holder screws.

## 7. Lead screw and timing the level-wind

The traveller rides on the rail and is driven by the lead screw, which is geared to the drum (81T : 45T, Tr8 x 2): it moves
3.6 mm per drum turn and lays the rope side by side on the drum.

1. Far-end screw stand: heat-set the two M3 inserts into its front leg. It stands behind the screen, its front leg on the
   plate in front of the rail; its foot is the block's hard stop at full payout.
2. Stand screws: 2 x M3 countersunk up through the plate into the leg's inserts.
3. 688ZZ into the stand from the right, against its lip, with a drop of **Loctite 641** on its outer ring (the seat has one
   lip; the 641 keeps the bearing from walking out). This end floats: radial support only.
4. Screw-end tower (printed PAHT-CF, printed on its side): push an M4 nut into the slot at each end of its foot. It stands
   on the plate past the rail's end and takes the screw's thrust.
5. Tower screws: 4 x M4 countersunk up through the base plate: the end two into the slot nuts, the flange two with washers
   and nuts on top.
6. MR128ZZ into the tower wall, centered (Loctite 641 or a press fit). It sits 0.66 mm short of each face, so the thrust
   washers bear on the wall and never on the bearing.
7. On the bench, bolt the 45T gear to the goBILDA Sonic Hub: 4 x M4 x 12 button head on the 16 mm pattern, the gear on the
   hub face toward the drum.
8. Lower the gear and hub in 8 mm left of the drum gear, through the notch in the tower web, then slide them 8 mm right
   into mesh with the 81T. Hold them there until the screw is through.
9. Inner F8-16M thrust bearing between the hub and the tower: the washer with the larger bore goes against the tower (it
   stays still); the snug one turns with the screw. The outer one goes the same way round.
10. Lead screw (Tr8 x 2, 245 mm) in from the right: through the tower, the thrust bearing and the hub, then turn it through
    the T8 nut and into the far-end 688.
11. Outer F8-16M and the 8 mm collar: push the collar against the bearing and tighten its set screw.
12. **Time the level-wind.** Wind the three dead wraps on by hand, side by side, ending one wrap before the start of the
    track. The rope's lead from the anchor crosses the bare barrel behind them. Turn the screw until the traveller's
    rollers sit on the rope where it leaves the bottom of the drum at the start of the track.
13. With the traveller in time, tighten the Sonic Hub's two pinch bolts. From then on the gears keep the traveller in
    step, and the collar and the hub hold the screw against the two thrust bearings.

## 8. Exit bracket and top tie

1. Fixed roller bracket on the bench: heat-set its inserts (4 x M3 in the front face, 2 x M5 in the top plate, 2 x M4 in
   the back face); push 3 x M4 nuts into the foot slots from the back.
2. Fixed rollers: one NATR6-PP track roller per roller into the bracket pockets, each on its 0.9 mm boss (inner ring only).
3. Fixed-roller shoulder bolts (6 x 16 mm) up from under the foot, through the access bores, into the top-plate inserts.
4. Bracket down onto the front edge of the base plate, in front of the carriage: 3 x M4 countersunk up through the plate
   into the foot nuts. Its flange is the exit's structure.
5. Top tie over the traveller and the drum: 2 x M4 down into the bracket's inserts (ball-end hex key from above).
6. Tie rear screws: 2 x M4 countersunk from the back, flush in the rear plate, through the plate and the tie, washer and nut
   on the tie. The tie carries the exit load to the rear wall, so it is bolted through, not screwed into inserts.

## 9. Electronics, battery and harness

1. ODrive bracket: an M3 nut into the slot in each foot first, then slide it in from the right: 2 x M3 countersunk up
   through the plate into those nuts.
2. On the bench: the machined heatsink onto the heat spreader's free face with the 0.25 mm thermal tape (clean both faces
   with alcohol, press for 15 s), its M3 nut slid into the slot in its foot, and a thin film of thermal paste under the foot.
3. ODrive Pro with its heat spreader, heatsink and terminal block: 4 x M4 x 12 through the spreader into the bracket, nuts
   in the bracket pockets. The heatsink's foot rests on the base plate: 1 x M3 countersunk up through the plate into its
   foot nut.
4. WAGO 221-615 lever nut into its bracket.
5. Battery bay: stick the 1 mm EVA hold-down pads under the two cradle roofs. For the TP2700 pair, put the printed spacer
   in first (its 4 mm plate against the outer panel, its 12 mm block at the front).
6. Pack A (bottom) in from the front through the cradle, leads first; then the 2 mm EVA separator; then pack B (top). The
   opening is 44 mm, about 0.5 mm a side for the TP3300 (43 mm by the maker's estimate).
7. Wire the harness: follow [wiring.md](wiring.md). At the main fuse, pack + and the charge lead go on ring terminals under
   the battery-end washer (M5, tongues to the front); ODrive DC+ (tongue to the right) and the regulator feed go on the
   output stud under the M8 nut, **75 in-lb maximum**. Fit the block's insulating cover. The motor thermistor goes to the
   ODrive's motor-thermistor input. Leave the Pi, screen, BMS and fan leads ready to plug in as the covers come down. Plug
   the pack connectors in only with the BMS switched off.

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
   the anvil pin. The rod's end drops into its seat in the land. The slider and the mating plate are hard-anodized: no
   grease on the tongue.
2. Finger-bar nuts: 2 x M2.5 nuts and their washers into the channel in the land, under where the link lies.
3. Trigger link onto its two pins: 2 x M2.5 flat head through the link and the 3 mm spacers into the tapped slider bar
   (**Loctite 243**).
4. Service lid into its rim: 4 x M2 countersunk into the inserts. Its pads hold the link on its pins and its rib closes the
   spring channel.
5. Finger bar through the lid's slots onto the link: 2 x M2.5 socket head into the nuts under the link.
6. Check: slide the finger bar 12.7 mm toward the motor end and let it go. The slider should snap home.

## 12. Rack side and hanging the unit

The rack side stays on the rack. It fits a 3 x 3 in upright with 1 in pin holes in its side faces.

1. Studs, on the bench: measure the rear plate at the four keyhole necks and stack the 0.3 and 0.1 mm shims under each stud
   head for a slip fit (about 0.05-0.1 mm). A DIN 439 M10 thin nut into each hex pocket in the mating plate's back, then the
   four shoulder studs (ISO 7379, 12 x 12 mm, M10 x 16) through their seats into the nuts. Each shoulder sits in its
   counterbore, which locates it.
2. Cheeks onto the mating plate's back, the front edge of each in its slot: an M5 nut into each of the three windows, then
   3 x M5 countersunk from the plate's front, **Loctite 243**. Before they are tight, stand the plate on the upright and shim
   each cheek to it (about 0.05 mm a side), then tighten.
3. Toggle clamp (DE-STA-CO 630-M) onto the plate's front face below the unit: 4 x M6 into the nuts in the pockets in its
   back. Its spindle is an M10 x 40 hex bolt in the plunger's thread with two jam nuts, its end in the pad bar's blind hole.
4. Rack side onto the upright: hang it with the cheeks either side, push the 1 in hitch pin through the left cheek, the
   upright and the right cheek, and clip it. Any pair of side holes at the height you want.
5. Push the lever over center: the pad bar presses the upright's face, the plate pivots on the pin and its top band clamps.
   The first time, set the spindle's length with the jam nuts so the lever goes over center with a firm push.
6. Pull the trigger: the finger bar 12.7 mm toward the motor end. The tongue retracts. Hold it there.
7. Offer the unit up: the four stud heads through the keyhole entries until the rear plate sits flat on the mating plate.
8. Lower the unit 12 mm. The stud shoulders pass the keyholes' narrow throats and settle in their V tops, centered; the two
   ball plungers push the plate onto the stud heads.
9. Let the trigger go: the spring pushes the tongue into the mating plate's pocket, and its 5° top wedges it there. Check
   that the unit cannot lift.

To take the unit off: pull the trigger, lift it 12 mm, and pull it back. To take the rack side off: lift the lever and pull
the pin.

## 13. Before powering

A finished assembly is not a training-ready machine. Before the motor is powered with the rope attached:

1. Work through [firmware-setup.md](firmware-setup.md): limits, calibration, homing, the motor thermistor and the payout
   window.
2. Follow the first power-up and load-test steps in the
   [safety reference](https://kinetiqgym.com/docs/SAFETY.html).
3. Wait at least 24 h after the Loctite 638 steps before loading the drum.

The control software (Pi app, Teensy firmware, phone app) is released after the prototype has been tested.

## The budget build

The budget build is a separate, simpler design with its own frame: 1/4 in and 1/8 in 6061 plate and aluminum and steel
angle bought near size, cut with a hacksaw and drilled through printed stand-ins, with every load-bearing screw into a nut.
It hangs on the rack upright on one 1 in hitch pin. The same MP8085 sits in an outside pod and turns a 1 in drum tube on a
20 mm shaft, in two flange bearings, through a steel clamp coupling; a printed gear pair drives the level-wind's lead screw,
and the exit is the main build's swivel. The ODESC, its fan and its heat spreader are on the unit; the 48 V supply, the
mains inlet and its switch are in a floor box, with one cable up the rack. A knob, a start/stop button and a phone app
(Bluetooth) set the weight. Its build order is published with its verified files; its parts are in the
[parts list](https://kinetiqgym.com/docs/BOM.html) and its wiring is summarized in [wiring.md](wiring.md).
