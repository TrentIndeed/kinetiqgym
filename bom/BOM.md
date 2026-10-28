# Bill of materials

> **Draft.** This is the parts list for the builds as designed now (October 2026). It is confirmed, with exact hardware
> counts, in the verified release after a prototype has been load-tested. Links are examples checked in October 2026;
> prices and stock change. Nothing here is endorsed by the suppliers.

The [website budget](https://kinetiqgym.com/build#parts) has the same list with dated prices, per-build totals and
editable prices.

**How the list is organized.** The **main list** is what a builder has to buy, in order of importance, from motor and
controller to hardware and metal stock. Fasteners and small bulk parts are counted by the pieces used; the note gives the
pack. The **accessory list** is what many builders already have. The last section gives typical costs for having the main
build's metal made.

## The builds

| Build | Max rope force, held through a set | Motor | Controller | Power | Frame |
|---|---|---|---|---|---|
| **Main** | 220 lb | Freerchobby MP8085, 50 Kv | ODrive Pro | 10S battery (2 x 5S LiPo) | bolted 6061 plate frame, about 515 mm long |
| **Budget** | 180 lb | Freerchobby MP8085, 50 Kv, in an outside pod | ODESC V4.2 | 48 V wall supply in a floor box | plate and angle bought near size, about 480 mm across |
| **Wall** | 300 lb | Hobbywing XRotor V11130 | Flipsky 75200 (VESC) | 1,000 W wall supply | in design: no parts list yet |

**Ratings.** Each rating is a design target held through a 20-30 s set (with about 3 minutes' rest), not yet verified. The
motor's torque against current and the controllers' current ratings are still to be bench-tested, and nothing has been
load-tested. The 10 lb minimum is designed to feel like 10 lb: the drums are small and light, and the firmware cancels part
of the motor's inertia (about 29 % of the felt mass on the main build, 24 % on the budget build).

- **Main:** the bolted 6061 aluminum frame, the 10S battery and the touchscreen. The drum is 7/8 in OD x 1/8 in wall 6061
  tube used as bought: 220 lb takes about 75 A from the ODrive Pro. 2.6 m of pull. A machined heatsink and a 40 mm fan cool
  the ODrive, and a thermistor on the motor's stator lets it roll the current back when the motor runs hot. In the load
  study every part passes 1.5x: the frame and rack side at 220 lb (the lowest, the rack side's pad bar, at about 1.6x), the
  level-wind and drum at 234 lb, the most the ODrive's 80 A can pull.
- **Budget:** its own simpler frame, cut with a hacksaw and drilled through printed guides, hung on the rack upright with one
  hitch pin. The motor sits in an outside pod and turns a 1 in drum tube on a 20 mm shaft through a steel clamp coupling.
  2.0 m of pull. 180 lb takes about 69 A from the ODESC, whose 70 A rating is the seller's and unverified: bench-test it
  first (if it only holds 53 A, the build tops out near 138 lb). A knob, a start/stop button and a phone app (Bluetooth) take
  the place of the battery and the screen. In the load study every structural part and bolt passes 1.5x at 180 lb.
- **Wall:** for people without a rack: it bolts to wall studs or concrete. It is in design; its parts list follows once the
  CAD is done.

Direct drive only: the motor turns the drum through a clamp coupling, with no belt or gear between them. Nothing is welded
or turned on a lathe: round parts are bought at their final size and cut to length. Every load-bearing joint is a bolt and
a nut.

## Main list

### Motor and controller

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 1 | [Freerchobby MP8085 outrunner, 50 Kv, sensored](https://www.freerchobby.cc/products/mp-8085-kv270-outrunner-brushless-motor-for-e-skateboard-bike-rc-drone?variant=34635792810145) | Both | Both builds' motor, off the shelf: Ø80 x 92 mm, 12 mm keyed shaft, 1.5 kg, 4 x M5 on Ø56 mm. $145 at the maker's store plus about $30 DHL/UPS shipping (shown only at checkout, so an estimate; a US tariff may apply); ships in about 4-5 days. Cut its rear prop shaft flush with the rear hub. Its torque against current is still to be measured: the ratings depend on it. |
| 1 | [ODrive Pro ODv44-ST](https://shop.odriverobotics.com/products/odrive-pro) | Main | Controller only; the heat spreader is separate. 220 lb takes about 75 A through a set (current limit 75.5 A): inside the datasheet's 80 A with active cooling. Still to be bench-tested. |
| 1 | [ODrive Pro heat spreader](https://shop.odriverobotics.com/) | Main | The machined heatsink and the fan mount on it (ODrive's own heatsink-and-fan kit does not fit the bay). |
| 1 | [ODESC V4.2 56 V controller (SEQURE)](https://www.amazon.com/dp/B0FH9DXFG7) | Budget | 180 lb takes about 69 A through a 30 s set. The seller's 70 A continuous rating is unverified: bench-test it (68 A for 30 s, three times, 3 min rest) before relying on it; if it only holds 53 A, the budget build tops out near 138 lb. 4.2 stars (5 ratings) on Amazon; SEQURE direct is $43.99 plus shipping and duties. |
| 1 | [NTC thermistors, 10 k, B3950, 10-pack (TIEXYE)](https://www.amazon.com/dp/B0F3X2G4D2) | Both | One glued to the motor's stator, read by the controller's thermistor input: it rolls the current back when the motor runs hot. Priced by the piece: 1 of a 10-pack ($7.99). The listing says 3590B, likely a typo for 3950: measure one. |
| 1 | Thermally conductive adhesive tape, 0.25 mm (3M 8810 or equal), one sheet | Main | Holds the machined 6061 heatsink on the ODrive's heat spreader. |
| 1 | [Thermal pad, 100 x 100 x 0.5 mm (ARCTIC TP-3)](https://www.amazon.com/dp/B09V53W559) | Budget | Between the ODESC and its aluminum heat spreader. 4.7 stars (2,791). |

### Power and battery

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 2 | [Thunder Power TP2700-5SR70](https://www.thunderpowerrc.com/products/tp2700-5sr70) | Main | 5S 2.7 Ah LiPo, EC5 leads. Two packs in series, on the printed TP2700 spacer. For more charge, the bay also takes 2 x TP3300-5SR70 (3.3 Ah, 122 Wh a pair against 100 Wh, regen to 39.6 A; $134.99 each, no spacer). |
| 1 | [JBD 10-17S 80 A smart BMS (same port, Bluetooth)](https://www.ebay.com/itm/398016908803) | Main | US-stocked (a California eBay seller, 2-4 day delivery). Same port, so regen charges through it; NTC probe. The CAD is sized for its 102 x 65 x 12 mm board. Set over-charge to 4.20-4.25 V per cell in its app. |
| 1 | [Blue Sea 5191 MRBF terminal fuse block](https://www.amazon.com/dp/B0019ZBTV4) | Main | 58 V DC; upright on a printed insulating pad. |
| 2 | [Blue Sea 5176 MRBF 40 A fuse](https://www.amazon.com/dp/B0016HTXAY) | Main | 58 V DC; one spare. |
| 2 | [MINI 58 V 10 A fuse (Littelfuse 0997010.WXN)](https://www.digikey.com/en/products/result?keywords=0997010.WXN) | Main | The charge-port line (charging the packs). 10 A in place of the 7.5 A 099707.5WXN, out of stock with no date; it still protects the 16 AWG charge lead. |
| 2 | [MINI 58 V 3 A fuse (Littelfuse 0997003.WXN)](https://www.digikey.com/en/products/result?keywords=0997003.WXN) | Main | The 5 V regulator feed. Digi-Key F5004-ND; ordinary MINI blades are 32 V. |
| 2 | [Inline MINI fuse holder, 58 V DC (Littelfuse 0FHM0003ZXJS)](https://www.digikey.com/en/products/detail/littelfuse-commercial-vehicle-products/0FHM0003ZXJS/29571868) | Main | 20 A, 18 AWG leads, rated 58 V DC (the Amazon holders are 32 V). |
| 1 | [Mean Well LRS-600N2-48 power supply](https://www.trcelectronics.com/products/mean-well-lrs-600n2-48) | Budget | 48 V, 600 W (1,200 W for 5 s), in the floor box: the budget build runs from the wall. From TRC Electronics, a US distributor, tariff included (a cheaper unrated Amazon listing may not be genuine). Holding 180 lb takes about 394 W. |
| 1 | [Mains inlet, pre-wired with fuse and lit rocker switch (10 A 125 V)](https://www.amazon.com/dp/B09DRLYD2Z) | Budget | The floor box's mains inlet and on/off switch. 4.7 stars (164). |
| 1 | [Wall cord, C13 to NEMA 5-15P, 16 AWG, 10 ft (Monoprice)](https://www.amazon.com/dp/B003KQ0O9S) | Budget | The floor box to a 120 V outlet. 4.7 stars (180). |
| 1 | [Brake resistors, 1 Ω 100 W aluminum, 5-pack (Comidox)](https://www.amazon.com/dp/B077ZMFZM6) | Budget | Two wired in series (2 Ω, the ODESC's value) on the inner plate: the wall supply cannot take braking energy, so it goes into them. Priced by the piece: 2 of a 5-pack ($9.99). 4.6 stars (140). |
| 1 | [Power cable, 14 AWG 2-core silicone, tinned copper, 10 ft (Haerkn)](https://www.amazon.com/dp/B0B9JBG1SH) | Budget | From the floor box up the rack to the unit, cut to length. 4.6 stars (335). |

### Drum and rope

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 1 | [Ruland MCLX-12-12-F clamp coupling](https://www.ruland.com/mclx-12-12-f.html) | Main | One-piece steel, 12 mm motor / 12 mm drum, 29 mm OD x 45 mm, 105 N·m: 5.6x the drum's torque at 1.5 x 220 lb. The motor's key comes out; McMaster-Carr 2469K73 ($69.98) is the keyed version. Ruland web store (registered users get 5% off). |
| 1 | [McMaster-Carr 2469K52 clamp coupling, 20 x 12 mm](https://www.mcmaster.com/2469K52/) | Budget | Steel, Ø42 x 65 mm, 350 N·m: the motor's shaft (key out) to the 20 mm drum shaft. Next-day from McMaster-Carr; the Ruland MCLX-20-12-F is the same part. No rated aluminum coupling in this bore pair was found. |
| 1 | 12 mm round steel shaft, 300 mm | Main | The drum shaft (a 12 mm linear shaft), cut to 262 mm with a cut-off wheel. |
| 1 | [Drum shaft, 20 mm h7 ground 1045 steel, cut to 258 mm (Misumi NSFHR20-258)](https://us.misumi-ec.com/vona2/result/?Keyword=NSFHR20-255) | Budget | Not hardened, so it can be drilled for the two cross bolts. Misumi USA cuts it to length (the 260 mm price; shipping not shown). |
| 1 | [Drum tube, 6061-T6 round tube, 1 in OD x .065 in wall, 12 in](https://www.metalsupermarkets.com/product/aluminum-round-tube-6061/) | Budget | Cut into the drum barrel (110 mm) and the two mount spacers (78 mm each). A common size at metal suppliers such as Metal Supermarkets (online price, October 27) or Online Metals. Used as bought: no lathe. |
| 1 | [6001-2RS bearings, 2-pack](https://www.amazon.com/dp/B07GVN7GQ7) | Main | Two bearings required. |
| 2 | [goBILDA 1301-0016-0012 hub](https://www.servocity.com) | Main | The drum hub and the 81T gear hub. |
| 1 | [SHF20 shaft supports, 4-pack (HiPicco)](https://www.amazon.com/dp/B0BHZKD6Q8) | Budget | One used, on the drum adapter. 4.5 stars (26). |
| 1 | [KFL004 flange bearings, 20 mm, 2-pack (S SYDIEN)](https://www.amazon.com/dp/B0F3D8BG1X) | Budget | Both used: the drum's left end on the inner plate, its right end on the right plate. 4.3 stars (195). |
| 1 | [AmSteel-Blue rope, 1/8 in x 25 ft (2,300 lb)](https://www.amazon.com/dp/B0B8WKH8L1) | Both | One rope in use (about 3.5-4 m) and the rest for the next one. The main build's 7/8 in drum bends it tighter than the usual 8:1, by choice: inspect it every ~20 sessions and replace it when fuzzy, glazed, flat, stiff or a strand is broken, or after about 6 months of use. 4.8 stars (378). |

### Level-wind and exit

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 1 | MGW15 rail, 250 mm, with an MGW15H block | Main | The traveller rail, cut to 213 mm with an abrasive cut-off wheel and deburred. Estimate: about $5 more than a 200 mm MGN15 set; the listing is still to be picked. |
| 1 | [MGN15 rails, 200 mm, with MGN15H blocks, 2-pack (Coavoo)](https://www.amazon.com/dp/B0D7CLND4B) | Budget | One rail and block used, uncut: the guide. Priced by the piece: 1 of the 2-pack ($49.99). 4.7 stars (7). |
| 1 | Tr8 x 2 lead screw, 250 mm, with brass flange nut | Main | Single start (a 3D-printer Z screw), cut to 245 mm. Estimate: the 200 mm 2-pack is $11.99. |
| 1 | [Tr8 x 2 lead screw, 200 mm, brass nut, 2-pack (Vichan)](https://www.amazon.com/dp/B0B8RKSDJV) | Budget | Used uncut. Pick "200mm / 2pcs Tr8X2". 4.4 stars (468). |
| 1 | [goBILDA 1309-0016-0008 Sonic Hub, 8 mm](https://www.gobilda.com/1309-series-sonic-hub-8mm-bore/) | Main | The 45T screw gear hub. goBILDA has it in stock (ServoCity showed it sold out on Oct 12); not the 8 mm REX version. |
| 4 | NATR6-PP track rollers, 6 mm bore | Main | The two travelling and two fixed rollers, one each, on the 6 x 16 mm shoulder bolts. Estimate per roller. |
| 1 | [626ZZ bearings, 10-pack](https://www.amazon.com/dp/B07JHKBG4X) | Budget | The guide and fixed rollers. 4.7 stars (759). |
| 1 | [688ZZ bearings, 5-pack](https://www.amazon.com/dp/B08199J4RJ) | Main | Lead screw far end, in the printed stand. |
| 1 | [MR128ZZ bearings, 10-pack](https://www.amazon.com/dp/B089GG2YCT) | Main | Lead screw fixed end, in the tower wall. |
| 1 | [F8-16M thrust bearings, 4-pack](https://www.amazon.com/dp/B07QLTXJDH) | Main | Lead screw fixed end, both directions. |
| 1 | [F8-16M thrust ball bearings, 2-pack (uxcell)](https://www.amazon.com/dp/B07PMRH7NJ) | Budget | The lead screw's fixed end, both directions (3.0 kN static). 4.7 stars (94). |
| 1 | [8 mm set-screw shaft collars, 10-pack](https://www.amazon.com/dp/B08SK2LNNV) | Main | Holds the screw against the thrust pair. Priced by the piece: 1 of a 10-pack ($8.89). |
| 1 | [8 mm shaft collars, 10-pack](https://www.amazon.com/dp/B08SK2LNNV) | Budget | The lead screw's ends. Priced by the piece: 2 of a 10-pack ($8.89). 4.7 stars (229). |
| 1 | [F608ZZ flanged bearings, 4-pack](https://www.amazon.com/dp/B0F4QWGCTV) | Budget | The lead screw's two bearings. 4.5 stars (59). |
| 1 | [M12 flat washers, 304, 25-pack (uxcell)](https://www.amazon.com/dp/B0DDGMJ6YS) | Budget | Two on the lead screw and one under the low mount spacer bolt's nut. Priced by the piece: 3 of a 25-pack ($6.99). |
| 1 | [ISO 7379 shoulder bolts 6 x 16, M5, 6-pack](https://www.amazon.com/dp/B0DP6ZRSTT) | Main | The four roller axles. Priced by the piece: 4 of a 6-pack ($8.99). |
| 1 | [16008-2RS bearings 40 x 68 x 9, 2-pack](https://www.amazon.com/dp/B0CMXGZMG8) | Both | The exit swivel pair. uxcell 2-pack. 4.7 stars (7). |
| 1 | [F6001-2RS flanged bearings, 4-pack](https://www.amazon.com/dp/B09BVV9BYZ) | Both | Exit pulleys: the rope runs on the outer ring. |
| 1 | [ISO 7379 shoulder bolts 12 x 25, M10, 2-pack](https://www.amazon.com/dp/B077GX5R3H) | Main | Exit pulley axles; next-day delivery (12 x 20 ships in two weeks). Two M12 washers go on each shoulder. |
| 1 | [Shoulder bolts 12 x 25 mm, M10, 304, 2-pack (MECCANIXITY)](https://www.amazon.com/dp/B0FDQZJQY1) | Budget | The exit pulley axles. 4.9 stars (17). |
| 1 | [M12 flat washers, DIN 125A 13 x 24 x 2.5, 25 pcs](https://www.amazon.com/dp/B0FQHCTQ5N) | Main | Two on each exit axle shoulder, so the nut still clamps the pulleys. 2.5 mm thick (thinner ones leave the shoulder proud). Priced by the piece: 4 of 25 ($8.39). |
| 1 | [Dowel pins 5 x 60 mm, 304 stainless, 24-pack](https://www.amazon.com/dp/B0FZHR1NP3) | Both | The exit's two side rails. Priced by the piece: 2 of a 24-pack ($8.49). |

### Rack side and latch

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 1 | [DE-STA-CO 630-M straight-line toggle clamp, flange base](https://www.destaco.com/clamping/manual/straight-line-action-clamps/straight-line-action-clamps-630/productdetails.630-M.html) | Main | The lever that locks the rack side to the upright (2,500 lbf holding): hang the plate, push the hitch pin through, push the lever over center. To take it off: lift the lever, pull the pin. FreerTool $69.63, Zoro $102.99 (October 2026). Its spindle is an M10 x 40 hex bolt (8.8) with two jam nuts. |
| 1 | Rear mount and latch small parts | Main | Four ISO 7379 12 x 12 mm shoulder screws (M10 x 16, 12.9) with four DIN 439 M10 thin nuts and 12 x 18 mm shim washers, two M10 x 19 ball spring plungers, the latch's hardened dowel pins (2 x 3 x 18, 2 x 4 x 16, 1 x 8 x 16 mm), its 0.5 x 4 x 40 mm stainless spring, 1.2 mm stainless rod and two M2.5 x 3 mm spacers. Estimate for the set. |

### Controls and screen

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 1 | [Teensy 4.0](https://www.pjrc.com/store/teensy40.html) | Main | Board allowance; use non-lockable reference. |
| 1 | [Waveshare SN65HVD230 CAN board](https://www.amazon.com/dp/B00KM6XMXO) | Main | 3.3 V CAN transceiver. |
| 1 | [Pololu D42V55F5 regulator](https://www.pololu.com/product/5571) | Main | #5571, 5 V output, 60 V maximum input. |
| 1 | [Raspberry Pi 4 Model B](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) | Main | 2 GB reference budget; actual memory variant/retailer may differ. |
| 1 | [Waveshare 4 inch HDMI LCD (C)](https://www.amazon.com/dp/B09QKR364V) | Main | 720 x 720 square capacitive display: HDMI video, USB-C touch. |
| 1 | [Flat HDMI cable kit, HDMI to 90-degree micro-HDMI, 10 cm](https://www.amazon.com/dp/B0HGXD92P2) | Main | Screen to the Pi's HDMI 0, under the Pi's edge. You assemble it (the plugs and the flat cable ship separately). |
| 1 | [Right-angle USB-C cable, 1 ft, 2-pack](https://www.amazon.com/dp/B0FG7Z6QLX) | Main | The screen's touch and power, to a Pi USB port. |
| 1 | [90-degree USB-A adapters, 4-pack](https://www.amazon.com/dp/B0C7V37X25) | Main | The right angle at the Pi's USB port. |
| 1 | [Noctua NF-A4x10 5V fan](https://www.amazon.com/dp/B00NEMGCIA) | Both | Main build: cools the ODrive through its duct and the machined heatsink. Budget build: blows across the ODESC. Both run from the 5 V regulator. 4.8 stars (3,969). |
| 1 | [Right-angle micro-USB cable, pack](https://www.amazon.com/dp/B08BZD66H4) | Main | Short setup/board cable. |
| 1 | [Seeed XIAO ESP32-C3](https://www.amazon.com/dp/B0B94JZ2YF) | Budget | On the perfboard by the ODESC: Bluetooth to the phone app, the knob and the start button, UART to the ODESC. 4.7 stars (386). |
| 1 | [EC11 push-button rotary encoders with knob caps, 6-pack](https://www.amazon.com/dp/B0C6Q67V97) | Budget | The dial on the motor's front: turn it to set the weight. 4.7 stars (71). |
| 1 | [Pololu APM81815 5 V regulator carrier (#5267)](https://www.pololu.com/product/5267) | Budget | 5.05-72 V in, 1.1 A: runs the XIAO and the fan from 48 V, on the perfboard. Plus shipping (not sold on Amazon). |
| 1 | [AS5047P encoder board (Autoro)](https://www.amazon.com/dp/B0H15G7NPX) | Budget | Reads the drum's position for the controller. 5.0 stars (5). |
| 1 | [Diametric magnets, 6 x 2.5 mm, 50-pack (KuntaiMag)](https://www.amazon.com/dp/B0H1578MWG) | Budget | The encoder's magnet, in the drum's end. Priced by the piece: 1 of 50 ($20.98). |
| 1 | [Tactile switches, 12 x 12 x 7.3 mm, 25-pack (Gikfun)](https://www.amazon.com/dp/B01E38OS7K) | Budget | One, behind the flush start/stop button. Priced by the piece: 1 of 25 ($9.78). 4.7 stars (362). |
| 1 | [Capacitors, 47 µF 63 V, 10-pack (JCCON)](https://www.amazon.com/dp/B0D78NSH96) | Budget | One across the regulator's input. Priced by the piece: 1 of 10 ($4.99). |
| 1 | 10 kΩ resistor and 1 µF ceramic capacitor | Budget | The motor thermistor's divider at the ODESC; from any kit. |

### Connectors and charging

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 1 | [42 V 2 A charger (10S)](https://www.amazon.com/dp/B08JYSZX78) | Main | Fit an XT60 male plug (about 1.5 h per charge). |
| 1 | [Amass XT60E-F, 10-pack](https://www.amazon.com/dp/B09SL2MNN1) | Both | Main build: the panel charge socket. Budget build: the floor box's output. One used. |
| 1 | [EC5 connectors, 10 pairs](https://www.amazon.com/dp/B08GPR7SVR) | Main | Retail pack for pack and BMS connections. |
| 1 | [5S JST-XH balance leads, 10-pack](https://www.amazon.com/dp/B073ZGF8D9) | Main | Pack-to-BMS sense harness. |
| 1 | [WAGO 221-615, 15-pack](https://www.amazon.com/dp/B07CJR8MH4) | Main | Five-port 10 AWG connector; one used. |
| 1 | [APIELE 12 mm latching switch, 2-pack](https://www.amazon.com/dp/B083QMF2J1) | Main | BMS signal switch; LED not wired in reference. |
| 1 | [XT60 pairs with 14 AWG silicone leads, 2-pack](https://www.amazon.com/dp/B07BF8154S) | Budget | The power cable's ends. 4.7 stars (311). |
| 1 | [Amass XT60E-M panel plugs, 10-pack](https://www.amazon.com/dp/B07YJMCDC3) | Budget | The unit's rear power port; one used. 4.8 stars (144). |
| 1 | [5.5 mm gold bullet connectors, 6 pairs (OliRC)](https://www.amazon.com/dp/B07YV6B8VL) | Budget | Three pairs on the motor's phase leads. Priced by the piece: 3 of 6 pairs ($7.99). |
| 1 | [JST-PH 2.0 6-pin plug and socket pairs, 150 mm, 20 pairs](https://www.amazon.com/dp/B0BKSNM7NF) | Budget | Extends the motor's Hall sensor cable (check its plug first). Priced by the piece: 2 of 20 ($9.59). |

### Adhesives and spacers

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 1 | [Loctite 638 retaining compound, 50 mL](https://www.amazon.com/dp/B000O01EV0) | Main | Bonds the drum flanges to the tube ends and the drum hub to the round shaft. The 10 mL listing is gone; the 50 mL bottle costs less. |
| 1 | [Loctite 641 bearing retainer](https://www.amazon.com/dp/B01MQJ92VM) | Main | Holds the drum bearings' inner rings on the shaft (the rope load turns with the shaft, so a loose ring creeps) and the bearings in their seats (drum holders, MR128ZZ, 688ZZ). Medium strength: heat to take apart. Ships from Amazon. |
| 1 | M5 aluminum spacers, Ø10 x 10 mm (5.2 mm bore) | Main | Four, between the MP8085's face and the motor face plate (4 x M5 x 25 through them). Estimate: about $6 for a 20-pack, priced by the piece. |

### Hardware

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 1 | [1/2-13 x 8 in hex cap screws, grade 8, 10-pack (Hard-to-Find Fastener)](https://www.amazon.com/dp/B00BBCV4RO) | Budget | The two mount spacer bolts through the drum-side handle's posts. Priced by the piece: 2 of 10 ($31.20). |
| 1 | [1/2-13 hex nuts, grade 8, 25-pack (Makers Bolt)](https://www.amazon.com/dp/B0D362QFSM) | Budget | The mount spacer bolts' nuts. Priced by the piece: 2 of 25 ($8.97). |
| 1 | [1/2 in SAE flat washers, grade 8, 100-pack (Makers Bolt)](https://www.amazon.com/dp/B0D65L42PZ) | Budget | Three on the mount spacer bolts. Priced by the piece: 3 of 100 ($16.97). |
| 1 | [3/8-16 x 5 in socket head cap screws, 12.9, 6 pcs](https://www.amazon.com/dp/B08VGB9L94) | Budget | The motor bay's three spacer bolts (grade 5 or 8 hex bolts from a hardware store work too). Priced by the piece: 3 of 6 ($11.99). |
| 1 | [3/8 in nuts and washers kit](https://www.amazon.com/dp/B0GQB93PG8) | Budget | For the spacer bolts. Priced by the piece: 7 of 60 ($9.99). |
| 1 | [M8 screw kit, class 12.9, 72 pcs (M8 x 30 socket heads, nuts, washers)](https://www.amazon.com/dp/B0GPXBPR31) | Budget | The KFL004 bearings' bolts and nuts. Priced by the piece: 6 of 72 ($9.99). |
| 1 | [Bolt kit M3-M6, 900 pcs](https://www.amazon.com/dp/B0CWTP62N8) | Budget | Screws 8-20 mm, nuts and washers: the base plate strips, the motor and its pod, the fan. Priced by the piece: 116 of 900 ($18.99). |
| 1 | [Lock nuts M3-M12, 170 pcs](https://www.amazon.com/dp/B0F61WKT6R) | Budget | All the nylocs. Priced by the piece: 8 of 170 ($9.99). |
| 1 | [M3 countersunk screw assortment, 30-50 mm](https://www.amazon.com/dp/B0CZQQX1TZ) | Budget | The swivel housing's four and the two M3 x 50 stack bolts. Priced by the piece: 6 of 75 ($9.69). |
| 1 | [Flat-head socket screw kit, M3/M4/M5, 304, 510 pcs with nuts (Glarks)](https://www.amazon.com/dp/B0734Q7DDG) | Budget | The covers, trays, rope clamp and start button. Priced by the piece: 47 of 510 ($15.99). |
| 1 | [M4 x 16 button-head socket screws, 304, 100 pcs](https://www.amazon.com/dp/B081JQZDF6) | Budget | The corner brackets. Priced by the piece: 15 of 100 ($8.99). |
| 1 | [M3 button-head screw kit, 304, 580 pcs](https://www.amazon.com/dp/B0D46D9D42) | Budget | The encoder board and the floor box. Priced by the piece: 18 of 580 ($4.99). |
| 1 | [M3 x 30 socket head screws with nuts, 100 sets](https://www.amazon.com/dp/B0DJP6TK7T) | Budget | The guide nut's four. Priced by the piece: 4 of 100 ($7.99). |
| 1 | [M6 x 20 flat-head socket cap screws, 10.9, 25 pcs](https://www.amazon.com/dp/B085M34WJL) | Budget | The base strips through the plates, flush (14 N·m). Priced by the piece: 8 of 25 ($8.99). |
| 1 | [M6 x 16 button-head socket cap screws, 10.9, 80 pcs](https://www.amazon.com/dp/B0FY5TFKPB) | Budget | The base strips up through the base plate (14 N·m). Priced by the piece: 8 of 80 ($8.54). |
| 1 | [M5 x 45 hex bolts with nuts, 304, 10 sets (MECCANIXITY)](https://www.amazon.com/dp/B0FGJB2283) | Budget | The drum's two cross bolts (one hacksawn to 32 mm). Priced by the piece: 2 of 10 ($7.69). |
| 1 | [M6 x 40 socket screws, part-threaded, 12.9, 10-pack (uxcell)](https://www.amazon.com/dp/B012T9NG0K) | Budget | The roller axles. Priced by the piece: 4 of 10 ($7.49). |
| 1 | [M5 x 12 flat-head socket screws, 304, 25-pack](https://www.amazon.com/dp/B0CTB9CF3V) | Budget | The roller brackets. Priced by the piece: 4 of 25 ($5.99). |

### Frame stock

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 1 | 6061-T6 aluminum plate, drum tube and heatsink stock, to cut yourself | Main | 0.250, 0.375, 0.500 and 0.750 in plate, a 1/2 in offcut for the ODrive heatsink and the 7/8 in OD x 1/8 in wall drum tube (cut to 162 mm and used as bought), from a metal supplier, enough for one build. You cut and drill it: a CNC router or laser, a drill and the printed drill guides; no lathe. No CNC: have the metal made instead (below). |
| 1 | [6061 plate, 6 x 6 in (6.0 mm), single (PATIKIL)](https://www.amazon.com/dp/B0DGWZBNS2) | Budget | The inner plate. 4.7 stars (41). |
| 2 | [6061 plate, 6 x 8 in (6.0 mm, Uxney)](https://www.amazon.com/dp/B0GYXY2BJN) | Budget | The right plate, and the exit plate cut to 188 mm. 4.6 stars (16). |
| 1 | [6061 flat bar, 1/4 x 4 x 8 in](https://www.amazon.com/dp/B0GFNBPJB3) | Budget | The cheek, hacksawn to 6 in. 4.8 stars (30). |
| 1 | [Steel angle, 1.6 x 1.6 x 0.18 in, A36, 12 in (Rocaris)](https://www.amazon.com/dp/B0FM29RL2V) | Budget | Hacksawn into four 19 mm corner brackets for the exit plate and the 44 mm cheek strip. 4.6 stars (14). |
| 1 | [6061-T651 sheet, 12 x 12 x 1/8 in](https://www.amazon.com/dp/B0BZPL1D4K) | Budget | The base plate, the left plate, the heat spreader and the drum flange, all from this one sheet, drilled through printed stand-ins. 4.6 stars (134). |
| 1 | [Aluminum angle, 1 x 1 x 1/8 in, 6061-T6, 12 in, 3 pcs (YLJNGUS)](https://www.amazon.com/dp/B0DXF1MMN4) | Budget | The inner, right and exit strips, 58, 43 and 110 mm, from one piece. 4.5 stars (66). |

### Load-path screws and small parts (main build)

Every screw the rope load passes through goes to a nut: a nut in a window cut through the plate, in a pocket, or keyed in a
notch in the drum tube's end. The exact counts come with the verified build files; these are the ones that matter.

| Qty | Part | Used for |
|---|---|---|
| 6 | M4 countersunk screws, nuts in the rear plate's windows | the rear plate to the base plate |
| 5 | M3 countersunk screws, nuts in windows | the motor face plate (3 through the base plate, 2 through the rear plate) |
| 12 | M3 countersunk screws, nuts in windows | the three corner gussets (2 up through the base plate and 2 through the rear plate each) |
| 4 | M4 countersunk screws, nuts in windows | the two drum bearing holders |
| 8 | M4 hex nuts, keyed in notches sawn in the drum tube's ends | the drum flanges and hub |
| 4 + 4 | M4 x 12 countersunk and M4 x 20 button head screws | the right flange; the hub and left flange |
| 4 | M3 x 14 countersunk screws, nuts in the printed clamp ring | the rope clamp |
| 10 | M4 x 6 socket head screws, nuts in pockets under the base plate | the MGW15 rail |
| 4 | M5 x 25 socket head screws through the Ø10 x 10 mm spacers | the motor, into its own M5 threads |
| 4 | Shoulder screws ISO 7379, 12 x 12 mm, M10 x 16, 12.9, each into a DIN 439 M10 thin nut | the rear mount's four studs |
| 4 | Shim washers 12 x 18 mm (DIN 988), 0.3 and 0.1 mm | under the stud heads, fitted at assembly |
| 2 | Ball spring plungers, M10 x 19, 6 mm ball | keep the rear plate on the stud heads |
| 6 | M5 x 35 countersunk screws, nuts in windows | the two rack cheeks to the mating plate |
| 4 | M6 x 25 socket head screws, nuts in pockets | the toggle clamp |
| 1 | M10 x 40 hex bolt (8.8) and 2 M10 jam nuts | the toggle clamp's spindle |
| 2 + 1 + 2 | Dowel pins 4 x 16, 8 x 16 and 3 x 18 mm, hardened (ISO 8734) | the latch slider guides, the latch anvil, the trigger-link guides |
| 1 | Compression spring, 0.5 mm wire x 4 mm OD x 40 mm, 302 stainless | the latch return |
| 1 | Stainless rod 1.2 mm, cut to 39.4 mm | the spring's guide rod |
| 2 | Round spacers M2.5 x 3 mm, 5 mm OD, aluminum | between the trigger link and the slider |
| 1 | Diametric magnet 6 x 5 mm (N45SH) | the encoder, glued into the drum shaft's end |

## Accessory list: check your parts bin first

Not in the main list's total. Buy only what is missing.

| Qty | Item | Builds | Notes |
|---|---|---|---|
| 1 | Drills and taps | Main | 3.4 and 4.5 mm drills for the edge holes (drilled by hand through the printed guides into the nut windows), and M2.5, M3 and M10 taps with a handle for the few holes that are still threaded (the fuse-block pad, the latch slider, the two ball plungers) if your service does not tap them. |
| 1 | [USB isolator for controller setup](https://shop.odriverobotics.com/) | Both | Protects the PC when you set up the ODrive or the ODESC over USB. |
| 1 | [Super Lube synthetic grease, 3 oz](https://www.amazon.com/dp/B000XBH9HI) | Both | Lead screw and gears. |
| 1 | Silicone wire, mixed gauges | Main | 10 to 24 AWG; lengths in the wiring reference. |
| 1 | [Silicone wire 12 AWG, red and black, 3 ft each (BNTECHGO)](https://www.amazon.com/dp/B01AQU3ST8) | Budget | The motor's three phase leads extended to the ODESC (measure the leads first). |
| 1 | [M5 ring terminals, pack](https://www.amazon.com/dp/B0DM8FW4LV) | Main | 12–10 AWG terminals; verify selected listing. |
| 1 | Ferrules & heat-shrink | Both | Consumables allowance; crimping tools excluded. |
| 1 | [Low-profile female header strips](https://www.amazon.com/dp/B0948H7FPP) | Main | Teensy socket: 2 x 14-pin low-profile machined-pin female. |
| 1 | [Prototype perfboards, pack](https://www.amazon.com/dp/B072Z7Y19F) | Both | Main build: three small boards (Teensy, CAN, regulator). Budget build: one (the XIAO and the regulator). |
| 1 | MicroSD card | Main | For the Raspberry Pi. |
| 2 | [PAHT-CF filament, 1 kg spool](https://www.amazon.com/dp/B0F37YW223) | Main | The end pieces, level-wind, exit, tower, gears and brackets. |
| 1 | PETG-CF filament, 1 kg spool | Main | The covers. |
| 1 | [PETG filament, 1 kg x 2 (ELEGOO)](https://www.amazon.com/dp/B0D41Y3WWZ) | Budget | The budget build's printed parts and covers. 4.6 stars (2,386). |
| 1 | [1 mm EVA foam roll](https://www.amazon.com/dp/B0BXJHVH5M) | Main | Battery pads: or print them in TPU 95A. |
| 1 | [2 mm EVA foam sheet](https://www.amazon.com/dp/B08YXYN327) | Main | Battery pads: or print them in TPU 95A. |
| 1 | Cable ties & thread locker | Both | Assembly consumables allowance. |
| 1 | [Hitch pin, 1 x 5 in, with R-clip, 2-pack (YuGtcen)](https://www.amazon.com/dp/B0DRF883JL) | Both | One used. Or your rack's own 1 in pin: the main build's rack side needs about 5 in usable between the head and the clip hole. |
| 1 | [Steel snap hook, 396 lb (seller's rating)](https://www.amazon.com/dp/B09LXKGBHM) | Both | Clips the handle to the rope. 4.8 stars (170). |
| 1 | [D-handle, 880 lb (Yes4All)](https://www.amazon.com/dp/B00FX34KDW) | Both | Or any cable attachment you have. 4.8 stars (2,589). |
| 1 | [3DZWMAN heat-set insert kit, 380 pcs (M2 to M8, with tips)](https://www.amazon.com/dp/B0D2R955CL) | Main | The insert pockets in every printed part are cut for this kit: M2 3 x 3.2, M2.5 4 x 4.0, M3 4 x 4.2, M4 5 x 5.0, M5 5 x 7.0 mm (length x outer diameter). Other brands may not grip. |
| 1 | [Heat-set inserts, 380-piece kit (3DZWMAN)](https://www.amazon.com/dp/B0D2R955CL) | Budget | 20 M3 for the covers, the motor tray, the floor box lid and the encoder cap. Priced by the piece: 20 of 380 ($18.99). |
| 1 | [Loctite 641 bearing retainer](https://www.amazon.com/dp/B01MQJ92VM) | Budget | The lead screw's two flanged 608 bearings. |
| 1 | [Metric socket screw assortment](https://www.amazon.com/dp/B0FJFVG31G) | Main | Purchase pack; the exact sizes and counts come with the build files. |
| 1 | [M4 button-head assortment](https://www.amazon.com/dp/B0BJQ4M7D5) | Main | Purchase pack; the exact sizes and counts come with the build files. |
| 1 | [M3 flat-head assortment](https://www.amazon.com/dp/B0GS8FZLTK) | Main | Purchase pack; the exact sizes and counts come with the build files. |
| 1 | [M3 x 25 flat-head screws, pack](https://www.amazon.com/dp/B0H5JVF4K4) | Main | Purchase pack; the exact sizes and counts come with the build files. |
| 1 | [M4 x 10 flat-head screws, pack](https://www.amazon.com/dp/B0956VQVJ2) | Main | Purchase pack; the exact sizes and counts come with the build files. |
| 1 | [M4 flat-head assortment](https://www.amazon.com/dp/B0CW5Y4RQY) | Main | Purchase pack; the exact sizes and counts come with the build files. |
| 1 | [M2.5 x 5 flat-head screws, pack](https://www.amazon.com/dp/B0CG1NVX6J) | Main | Purchase pack; the exact sizes and counts come with the build files. |
| 1 | [M2.5 socket screw assortment](https://www.amazon.com/dp/B0FG2BYJSR) | Main | Purchase pack; the exact sizes and counts come with the build files. |
| 1 | [M2.5 x 5 socket screws, pack](https://www.amazon.com/dp/B0GM84W3X8) | Main | Purchase pack; the exact sizes and counts come with the build files. |
| 1 | M3 x 40 countersunk screws, pack | Main | Exit clamp, 4 needed. |
| 1 | M3 x 10 low-head socket screws (DIN 7984), pack | Main | Lead screw nut flange, 4 needed. |
| 1 | M10 nyloc nuts and washers | Main | Exit pulley axles, 2 of each. |
| 1 | [Lock-nut & washer assortment](https://www.amazon.com/dp/B0F1FGKC1C) | Main | Purchase pack; the exact sizes and counts come with the build files. |
| 1 | [Plain hex-nut assortment](https://www.amazon.com/dp/B097N3SGCD) | Main | Purchase pack; the exact sizes and counts come with the build files. |

The exact screw sizes and counts come with the verified build files.

## No CNC? Have the metal made

Main build. Typical costs for having the metal parts made for one machine: about $310-545 in all. Prices depend on the shop, the
quantity and the lead time, so get quotes. This replaces the aluminum line in the main list. Ready-made metal kits are planned after testing.
The budget build needs no CNC: its plate and angle are bought near size and cut with a hacksaw.

| Item | Typical cost (USD) | Notes |
|---|---|---|
| [Laser-cut plate set, 6061-T6](https://sendcutsend.com) | 200-300 | The base, rear and motor face plates (with their nut windows), the drum flanges and the latch slider (0.250 and 0.375 in), plus the four 2 mm steel bearing cheeks, cut from the DXF files at an instant-priced laser service such as SendCutSend. The prototype's plates came to about $200-300 at SendCutSend (October 2026). Countersinking is extra, charged per hole. |
| Thick plate parts: drum holders, corner gussets, rack side and ODrive heatsink | 100-225 | The two 3/8 in drum bearing holders, the three 1/4 in corner gussets, the rack side's mating plate, its two 1/2 in cheeks and pad bar, and the finned ODrive heatsink, milled from plate (no machined blocks, no lathe). The 28 mm bearing bores are finished to H7. |
| Drum tube, 6061-T6, 7/8 in OD x 1/8 in wall, 162 mm | 10-20 | From a metal supplier such as Metal Supermarkets or Online Metals, cut square (reference: about $8.50 a foot). Used as bought: no lathe. |

The holes in the plate edges are drilled by hand through the printed drill guides, into nut windows cut through the plates.
The drum tube's end notches are sawn and filed through a printed tube-end guide.

## Printed parts

Main build (materials and settings in [printing.md](https://kinetiqgym.com/docs/printing.html)):

- **PAHT-CF:** the 81T drum gear, the 45T screw gear, the traveller frame, the fixed roller bracket, the top tie, the
  far-end screw stand, the screw-end tower, the rope clamp ring, the exit bearing housing, the exit carrier, its retainers
  and rail caps.
- **PA-CF:** the motor-end and battery-end pieces, the ODrive bracket, the latch finger bar and the service lid.
- **PETG-CF:** the two covers (end caps printed in) and the rear I/O panel.
- **PETG:** the screen frame, the front board plate and its standoffs, the WAGO bracket, the fan duct, and the TP2700
  battery spacer (only with the TP2700 pair).
- **TPU 95A or EVA foam:** the three battery pads.
- **PETG or PLA:** the drill guides and the drum tube-end guide (tools, not parts of the machine).

The budget build prints its covers, motor pod, floor box, gears and smaller parts in PETG (about 2 kg); its print list comes
with its verified files.
