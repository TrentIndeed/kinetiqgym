# Bill of materials

> **Draft.** This is the parts list for the prototype being built now (October 2026). It is confirmed, with exact hardware
> counts, in the verified release after the prototype has been load-tested. Links are examples checked in October 2026;
> prices and stock change. Nothing here is endorsed by the suppliers.

The [website budget](https://kinetiqgym.com/build#parts) has the same list with dated prices, per-build totals and
editable prices.

**How the list is organized.** The **main list** is what a builder has to buy, in order of importance, from motor and
controller to adhesives. It assumes you make the metal and printed parts yourself (laser cutting or CNC, a drill with taps,
and a 3D printer). The **accessory list** is what many builders already have. The last section gives typical costs for having
the metal made.

**What the builds share.** Every build uses the same bolted 6061 aluminum frame, drum, level-wind, exit and rack side.
The shared parts are sized for the 220 lb peak builds: in the load study every member passes 1.5x at 220 lb, to be
confirmed by load testing. Direct drive only: the motor turns the drum through a clamp coupling,
with no belt or gear between them.

## The five builds

| Build | Peak rope force | Motor | Controller | Power | Size (about) |
|---|---|---|---|---|---|
| **Main** | 158 lb | APS 8072S outrunner, 50 Kv | ODrive Pro | 10S battery (2 x 5S LiPo) | 400 x 227 x 103 mm |
| **Lite** | 158 lb | APS 8072S, wound to about 25 Kv | ODrive S1 | 36 V wall supply inside | 400 x 227 x 103 mm |
| **MP80100** | 158 lb | MP80100 outrunner, 50 Kv | ODrive Pro | 10S battery | 444 x 227 x 103 mm |
| **MP80100 wye** | 220 lb peak | MP80100 rewired wye, about 29 Kv | ODrive Pro | 10S battery | 444 x 227 x 103 mm |
| **C80100** | 220 lb peak | APS C80100, wound to about 25 Kv | ODrive Pro | 10S battery | 429 x 227 x 103 mm |

- **Main:** the reference build. A light rotor (about 2.5 kg felt at the rope before compensation), about 13 N·m.
- **Lite:** the low-cost build on the main build's frame, mount and motor body, plugged into the wall. A Mean Well 36 V,
  600 W supply inside, an ODrive S1 with two brake resistors on the base plate, and a phone app (Bluetooth) and a knob in
  place of the battery, the Raspberry Pi and the touchscreen. At about 25 Kv, 158 lb takes 37-45 A.
- **MP80100:** the same frame with a 44 mm longer motor bay. About 4 kg felt at the rope; ships from China.
- **MP80100 wye:** if the 50 Kv motor is wound delta, re-terminating it in wye gives about 29 Kv, so 220 lb takes about
  60 A (the ODrive Pro gives 70 A continuous). Ask the seller how it is wound before buying for 220 lb.
- **C80100:** wound to order at about 25 Kv, so 220 lb takes about 52-63 A on the ODrive Pro. The motor is 15 mm shorter
  than the MP80100.

**Motor mounting parts by build:**

| Builds | Coupling | Spacers and screws | Before fitting |
|---|---|---|---|
| Main, Lite | Ruland MCLX-12-10-F (10 mm motor, 12 mm drum) | 4 x M5 spacers 10 x 3 mm, 4 x M5 x 14 (Ø59 mm circle) | - |
| MP80100, MP80100 wye, C80100 | Ruland MCLX-12-12-F (12 mm motor, 12 mm drum) | 4 x M5 spacers Ø10 x 10 mm, 4 x M5 x 25 (Ø56 mm circle) | cut the bell-end shaft to a 10 mm stub |

In the tables below, **Battery builds** means Main, MP80100, MP80100 wye and C80100.

## Main list

### Motor and controller

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 1 | APS 8072S outrunner, 50 Kv | Main | Alien Power Systems (UK). Sensored, 10 mm keyed shaft. |
| 1 | [MP80100 outrunner, 50 Kv, sensored](https://www.aliexpress.us/item/3256805081566856.html) | MP80100, MP80100 wye | Ships from China (3-4 weeks). For 220 lb, ask the seller whether it is wound delta. |
| 1 | [APS C80100 outrunner, sensored, custom ~25 Kv](https://alienpowersystem.com) | C80100 | Alien Power Systems (UK): ask for the ~25 Kv winding and its price. Ø80 x 92 mm, 4 x M5 on Ø56, 12 mm keyed shaft. |
| 1 | APS 8072S outrunner, custom ~25 Kv | Lite | Wound to order. Same body, mount and 10 mm keyed shaft as the main build's motor. |
| 1 | [ODrive Pro](https://shop.odriverobotics.com/products/odrive-pro) | Battery builds | Controller only; the heat spreader is separate. 70 A continuous. |
| 1 | [ODrive S1, solder-pad version](https://shop.odriverobotics.com/products/odrive-s1) | Lite | 40 A continuous on its heat spreader, 80 A peak, 12-50.5 V, on-board magnetic encoder. Screws to a 6061 plate you make; the ODrive bracket stays. |
| 1 | [ODrive Pro heat spreader](https://shop.odriverobotics.com/) | Battery builds | |

### Battery and power

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 2 | [Thunder Power TP2700-5SR70](https://www.thunderpowerrc.com/products/tp2700-5sr70) | Battery builds | 5S 2.7 Ah LiPo, EC5 leads. Two in series on the printed spacer. For more charge the bay also takes 2 x TP3300-5SR70 (122 Wh a pair against 100 Wh, regen up to 39.6 A; no spacer). Built to order in the US. |
| 1 | [Mean Well LOP-600-36 power supply](https://www.jameco.com/z/LOP-600-36-MEAN-WELL-600W-Low-Profile-Energy-Efficient-Medical-Open-Frame-Power-Supply-36V-11-1A-Convection-16-7A-with-Fan_2410207.html) | Lite | 36 V open frame: 400 W by convection, 600 W with airflow, 150 % for 3 s. About a 3-week lead time. |
| 1 | [JBD 10-17S 80 A smart BMS, same port, Bluetooth](https://www.ebay.com/itm/398016908803) | Battery builds | US-stocked. Same port, so regen charges through it; NTC probe. The bay is sized for its 102 x 65 x 12 mm board. Set over-charge to 4.20-4.25 V per cell. |
| 1 | [Blue Sea 5191 MRBF terminal fuse block](https://www.amazon.com/dp/B0019ZBTV4) | Battery builds | 58 V DC; stands on a printed insulating pad. |
| 2 | [Blue Sea 5176 MRBF 40 A fuse](https://www.amazon.com/dp/B0016HTXAY) | Battery builds | 58 V DC; one spare. |
| 1 | [50 W 1 Ω aluminum-housed resistors, 5-pack](https://www.amazon.com/dp/B0F43QWVM3) | Lite | Two in series (2 Ω) as the S1's brake resistor, screwed flat to the base plate, which is their heatsink. |
| 2 | [MINI 58 V 10 A fuse (Littelfuse 0997010.WXN)](https://www.digikey.com/en/products/result?keywords=0997010.WXN) | Battery builds | The charge-port line; one spare. |
| 2 | [MINI 58 V 3 A fuse (Littelfuse 0997003.WXN)](https://www.digikey.com/en/products/result?keywords=0997003.WXN) | All | The 5 V regulator feed; one spare. Ordinary MINI blades are 32 V. |
| 2 | [Inline MINI fuse holder, 58 V DC (Littelfuse 0FHM0003ZXJS)](https://www.digikey.com/en/products/detail/littelfuse-commercial-vehicle-products/0FHM0003ZXJS/29571868) | All | 20 A, 18 AWG leads, rated 58 V DC (most inline holders are 32 V). |
| 1 | [C14 panel-mount inlet, 10 A, 2-pack](https://www.amazon.com/dp/B07PVP7GL2) | Lite | The mains inlet, snapped into the back step. |
| 1 | [KCD1 rocker switch, 10 A 125 V / 6 A 250 V](https://www.amazon.com/dp/B0DX1JY5BW) | Lite | Mains on/off in the line lead, beside the inlet. |

### Drum and rope

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 1 | [Ruland MCLX-12-10-F clamp coupling](https://www.ruland.com) | Main, Lite | One-piece steel, 10 mm motor / 12 mm drum, 105 N·m. The drum needs up to 17.1 N·m (25.7 with the 1.5x margin). Check a distributor before ordering. |
| 1 | [Ruland MCLX-12-12-F clamp coupling](https://www.ruland.com) | MP80100, MP80100 wye, C80100 | One-piece steel, 12 mm motor / 12 mm drum, 105 N·m. |
| 1 | 12 mm steel drum shaft, 200 mm | All | Round (a 12 mm linear shaft), used uncut. |
| 1 | [6001-2RS bearings, 2-pack](https://www.amazon.com/dp/B07GVN7GQ7) | All | The drum shaft, in the two machined holders. |
| 2 | [goBILDA 1301-0016-0012 clamping hub, 12 mm round bore](https://www.servocity.com) | All | The drum hub and the 81T gear hub. |
| 1 | 1/8 in UHMWPE rope | All | About 3 m. |

### Level-wind and exit

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 1 | [MGN15H rail 200 mm with block, 2 sets](https://www.amazon.com/dp/B0D7CLND4B) | All | The traveller rail (one spare set). |
| 1 | [Tr8 x 2 lead screw, 200 mm, 2-pack](https://www.amazon.com/dp/B0B8RKSDJV) | All | With brass flange nuts; used uncut. Pick "200mm / 2pcs Tr8X2". |
| 1 | [goBILDA 1309-0016-0008 Sonic Hub, 8 mm bore](https://www.gobilda.com/1309-series-sonic-hub-8mm-bore/) | All | The 45T screw gear's hub. Not the 8 mm REX version. |
| 1 | [626ZZ bearings, 10-pack](https://www.amazon.com/dp/B07JHKBG4X) | All | The travelling and fixed rollers; 8 used. |
| 1 | [688ZZ bearings, 5-pack](https://www.amazon.com/dp/B08199J4RJ) | All | The lead screw's far end, in the printed stand. |
| 1 | [MR128ZZ bearings, 10-pack](https://www.amazon.com/dp/B089GG2YCT) | All | The lead screw's fixed end, in the tower wall. |
| 1 | [F8-16M thrust bearings, 4-pack](https://www.amazon.com/dp/B07QLTXJDH) | All | The lead screw's fixed end, both directions. |
| 1 | [8 mm set-screw shaft collars, 10-pack](https://www.amazon.com/dp/B08SK2LNNV) | All | Preloads the thrust pair. |
| 1 | [ISO 7379 shoulder bolts 6 x 16, M5, 6-pack](https://www.amazon.com/dp/B0DP6ZRSTT) | All | The four roller axles. |
| 1 | [16008-2RS bearings 40 x 68 x 9, 2-pack](https://www.amazon.com/dp/B0CMXGZMG8) | All | The exit swivel pair. |
| 1 | [F6001-2RS flanged bearings, 4-pack](https://www.amazon.com/dp/B09BVV9BYZ) | All | The exit pulleys: the rope runs on the outer ring. |
| 1 | [ISO 7379 shoulder bolts 12 x 25, M10, 2-pack](https://www.amazon.com/dp/B077GX5R3H) | All | The exit pulley axles. |
| 1 | [M12 flat washers, DIN 125A 13 x 24 x 2.5, 25 pcs](https://www.amazon.com/dp/B0FQHCTQ5N) | All | Two on each exit axle shoulder, so the nut still clamps the pulleys. 2.5 mm thick: thinner ones leave the shoulder proud. |
| 1 | [Dowel pins 5 x 60 mm, 304 stainless, 24-pack](https://www.amazon.com/dp/B0FZHR1NP3) | All | The exit's side rails. |

### Controls and screen

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 1 | [Teensy 4.0](https://www.pjrc.com/store/teensy40.html) | Battery builds | Machine control. |
| 1 | [Waveshare SN65HVD230 CAN board](https://www.amazon.com/dp/B00KM6XMXO) | All | 3.3 V CAN transceiver. |
| 1 | [Pololu D42V55F5 regulator (#5571)](https://www.pololu.com/product/5571) | All | 5 V output, 60 V maximum input. Not the D36V50F5: it is rated to 38 V and a full pack is 42 V. |
| 1 | [Seeed XIAO ESP32-C3](https://www.amazon.com/dp/B0B94JZ2YF) | Lite | Bluetooth link to the phone app and the knob; talks to the S1 over CAN through the CAN board. |
| 1 | [EC11 rotary encoders with push button and knob caps, 5-pack](https://www.amazon.com/dp/B08728K3YB) | Lite | The resistance knob, through the left cover. |
| 1 | [Raspberry Pi 4 Model B](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) | Battery builds | The budget assumes 2 GB. |
| 1 | [Waveshare 4 inch HDMI LCD (C)](https://www.amazon.com/dp/B09QKR364V) | Battery builds | 720 x 720 square capacitive touch display: HDMI video, USB-C touch. |
| 1 | [Flat HDMI cable kit, HDMI to 90-degree micro-HDMI, 10 cm](https://www.amazon.com/dp/B0HGXD92P2) | Battery builds | Screen to the Pi's HDMI 0. You assemble it. |
| 1 | [Right-angle USB-C cable, 1 ft, 2-pack](https://www.amazon.com/dp/B0FG7Z6QLX) | Battery builds | The screen's touch and power, to a Pi USB port. |
| 1 | [90-degree USB-A adapters, 4-pack](https://www.amazon.com/dp/B0C7V37X25) | Battery builds | The right angle at the Pi's USB port. |
| 1 | [Noctua NF-A4x10 5V fan](https://www.amazon.com/dp/B00NEMGCIA) | All | Cools the ODrive. |
| 1 | [Right-angle micro-USB cable, pack](https://www.amazon.com/dp/B08BZD66H4) | Battery builds | Teensy to Pi. |

### Connectors and charging

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 1 | [42 V 2 A charger (10S)](https://www.amazon.com/dp/B08JYSZX78) | Battery builds | Fit an XT60 male plug (about 1.5 h per charge). |
| 1 | [Amass XT60E-F, 10-pack](https://www.amazon.com/dp/B09SL2MNN1) | Battery builds | The panel charge socket; one used. |
| 1 | [EC5 connectors, 10 pairs](https://www.amazon.com/dp/B08GPR7SVR) | Battery builds | Pack and BMS connections. |
| 1 | [5S JST-XH balance leads, 10-pack](https://www.amazon.com/dp/B073ZGF8D9) | Battery builds | Pack-to-BMS balance leads. |
| 1 | [WAGO 221-615, 15-pack](https://www.amazon.com/dp/B07CJR8MH4) | Battery builds | Five-port lever nut for 10 AWG, the switched negative junction; one used. |
| 1 | [APIELE 12 mm latching switch, 2-pack](https://www.amazon.com/dp/B083QMF2J1) | Battery builds | The power button: a signal to the BMS soft-switch input. |

### Adhesives and spacers

| Qty | Part | Builds | Notes |
|---|---|---|---|
| 1 | [Loctite 638 retaining compound, 50 mL](https://www.amazon.com/dp/B000O01EV0) | All | Bonds the drum hub and the drum flanges to the round shaft. |
| 1 | [Loctite 641 bearing retainer](https://www.amazon.com/dp/B01MQJ92VM) | All | Holds the drum bearings' inner rings on the shaft (the rope load turns with the shaft, so a loose ring creeps) and the bearings in their seats (drum holders, MR128ZZ, 688ZZ). Medium strength: heat to take apart. |
| 1 | [M5 aluminum spacers 10 x 3 mm, 20-pack](https://www.amazon.com/dp/B0CQ2R5GDW) | All | The 3 mm spacers under the APS 8072S face. |

### Small parts for the latch, rack side and encoder

| Qty | Part | Used for |
|---|---|---|
| 4 | Shoulder screw ISO 7379, 12 x 12 mm, M10 x 16 thread, 12.9 steel | the rack side's four studs |
| 4 | Shim washer 12 x 18 x 2 mm (DIN 988) | under each stud head |
| 2 | Dowel pin 4 x 16 mm, hardened (ISO 8734) | latch slider guides |
| 1 | Dowel pin 8 x 16 mm, hardened (ISO 8734) | latch anvil |
| 2 | Dowel pin 3 x 18 mm, hardened (ISO 8734) | trigger-link guides |
| 1 | Compression spring 0.35 mm wire x 3 mm OD x 45 mm, stainless | latch return; to be chosen and tested on the prototype |
| 1 | Stainless rod 1.2 mm, cut to 39.4 mm | the spring's guide rod |
| 2 | Round spacer M2.5 x 3 mm, 5 mm OD, aluminum | between the trigger link and the slider |
| 3 + 6 | M5 countersunk screws, 18 mm and 22 mm, with 9 M5 nyloc nuts and 9 washers | the three corner brackets |
| 6 | M4 x 18 countersunk screws | the rear plate to the base plate |
| 4 | M4 x 12 countersunk screws | the motor face plate brackets |
| 2 | M3 x 18 countersunk screws | the rear plate into the motor face plate's back edge |
| 8 | M3 x 12 countersunk screws | the drum flanges to the tube |
| 6 | M4 x 25 countersunk screws | the mating plate into the rack cheeks |
| 4 | M2 x 5 countersunk screws | the service lid |
| 1 | Diametric magnet 6 x 5 mm (N45SH) | the encoder, glued into the drum shaft end |

## Accessory list: check your parts bin first

Not in the main list's total. Buy only what is missing.

| Qty | Item | Builds | Notes |
|---|---|---|---|
| 1 | 6061-T6 stock for machining it yourself | All | Only if you machine the metal yourself: 0.250, 0.375 and 0.750 in plate, a short bar for the bearing holders, 1 x 1 x 1/4 in angle for the motor face plate brackets, and the drum tube, from a local metal shop. About $160 for one build. |
| 1 | Taps and drills for the edge holes | All | M3 and M4 taps with a tap handle, and 2.5 and 3.3 mm drills: the edge holes are drilled by hand through the printed guides. |
| 1 | [USB isolator](https://shop.odriverobotics.com/) | All | Protects the PC when you set up the ODrive over USB. |
| 1 | [Super Lube synthetic grease, 3 oz](https://www.amazon.com/dp/B000XBH9HI) | All | The lead screw and the gears. |
| 1 | Silicone wire, mixed gauges | All | 10 to 24 AWG; lengths in [wiring.md](https://kinetiqgym.com/docs/wiring.html). |
| 1 | [Ring terminals, pack](https://www.amazon.com/dp/B0DM8FW4LV) | Battery builds | 10 AWG M5 (pack +), 16 AWG M5 (charge +), 10 AWG 5/16 in (ODrive DC+), 18 AWG 5/16 in (regulator feed). |
| 1 | Ferrules and heat-shrink | All | |
| 1 | IEC C13 mains cord | Lite | Any standard computer or monitor power cord. |
| 1 | 6.3 mm insulated female quick-disconnects | Lite | For the inlet and rocker switch tabs. |
| 1 | Power supply mating connectors (CN1, CN2) | Lite | The AC input and 12 V auxiliary housings with crimps, as listed in the LOP-600 datasheet. |
| 1 | Ring terminals, M3.5 and M4, 10-16 AWG | Lite | The supply's DC screws, its earth screw and the earth stud in the base plate. |
| 1 | Thermal pad, 0.5 mm, 6 W/mK | Lite | Between the S1 and its plate. |
| 1 | JST GH 4-pin cable | Lite | CAN from the CAN board to the S1. |
| 1 | [Low-profile female header strips](https://www.amazon.com/dp/B0948H7FPP) | All | The Teensy socket: 2 x 14-pin low-profile machined-pin female. |
| 1 | [Prototype perfboards, pack](https://www.amazon.com/dp/B072Z7Y19F) | All | Three small boards (controller, CAN, regulator). |
| 1 | MicroSD card | Battery builds | For the Raspberry Pi. |
| 2 | [PAHT-CF filament, 1 kg spool](https://www.amazon.com/dp/B0F37YW223) | All | The end pieces, level-wind, exit, tower, gears and brackets. |
| 1 | PETG-CF filament, 1 kg spool | All | The covers. |
| 1 | [1 mm EVA foam roll](https://www.amazon.com/dp/B0BXJHVH5M) | Battery builds | Battery pads; or print them in TPU 95A. |
| 1 | [2 mm EVA foam sheet](https://www.amazon.com/dp/B08YXYN327) | Battery builds | Battery pads; or print them in TPU 95A. |
| 1 | Cable ties and thread locker (Loctite 243) | All | |
| 1 | [1 in steel hitch pin](https://www.amazon.com/dp/B08974F734) | All | Or your rack's own 1 in pin: at least 92 mm between the head and the clip hole. |
| 1 | [3DZWMAN heat-set insert kit, 380 pcs (M2 to M8, with tips)](https://www.amazon.com/dp/B0D2R955CL) | All | The insert pockets in every printed part are cut for this kit: M2 3 x 3.2, M2.5 4 x 4.0, M3 4 x 4.2, M4 5 x 5.0, M5 5 x 7.0 mm (length x outer diameter). Other brands may not grip. |
| 1 | [Metric socket screw assortment](https://www.amazon.com/dp/B0FJFVG31G) | All | |
| 1 | [M4 button-head assortment](https://www.amazon.com/dp/B0BJQ4M7D5) | All | |
| 1 | [M3 flat-head assortment](https://www.amazon.com/dp/B0GS8FZLTK) | All | |
| 1 | [M3 x 25 flat-head screws, pack](https://www.amazon.com/dp/B0H5JVF4K4) | All | |
| 1 | [M4 x 10 flat-head screws, pack](https://www.amazon.com/dp/B0956VQVJ2) | All | |
| 1 | [M4 flat-head assortment](https://www.amazon.com/dp/B0CW5Y4RQY) | All | |
| 1 | [M2.5 x 5 flat-head screws, pack](https://www.amazon.com/dp/B0CG1NVX6J) | All | |
| 1 | [M2.5 socket screw assortment](https://www.amazon.com/dp/B0FG2BYJSR) | All | |
| 1 | [M2.5 x 5 socket screws, pack](https://www.amazon.com/dp/B0GM84W3X8) | All | |
| 1 | M3 x 40 countersunk screws, pack | All | The exit clamp, 4 needed. |
| 1 | M3 x 10 low-head socket screws (DIN 7984), pack | All | The lead screw nut's flange, 4 needed. |
| 1 | M10 nyloc nuts and washers | All | The exit pulley axles, 2 of each. |
| 1 | [Lock-nut and washer assortment](https://www.amazon.com/dp/B0F1FGKC1C) | All | |
| 1 | [Plain hex-nut assortment](https://www.amazon.com/dp/B097N3SGCD) | All | |

The exact screw sizes and counts come with the verified build files.

## No CNC? Have the metal made

Typical costs for having the metal parts made for one machine: about $565-1,280 in all. Prices depend on the shop, the
quantity and the lead time, so get quotes. Not in the main list's total. Ready-made metal kits are planned after testing.

| Item | Typical cost (USD) | Notes |
|---|---|---|
| [Laser-cut plate set, 6061-T6, tapped and countersunk](https://sendcutsend.com) | 250-450 | The base, rear and motor face plates, the rack cheeks and the drum flanges, plus the four 2 mm steel bearing cheeks, from an instant-priced laser service. Tapping and countersinking are charged per hole. |
| Machined parts: bearing holders, brackets and the mating plate | 300-800 | Two drum bearing holders (28 H7 bore), three corner brackets and the 3/4 in mating plate (M10 threads, cheek slots) from an online CNC service. One-off US quotes sit at the top of the range; overseas services cost less and take two to three weeks. |
| Drum tube, 6061, 1-1/4 in OD x 0.250 in wall, 100 mm | 15-30 | From a local metal shop, cut square; ask for T6. |

The holes in the plate edges and the tube ends are drilled and tapped by hand through the printed drill guides, and the
two motor face plate brackets are cut from 1 x 1 x 1/4 in 6061 angle (see the build instructions).

## Printed parts

Printed for every build (materials and settings in [printing.md](https://kinetiqgym.com/docs/printing.html)):

- **PAHT-CF:** the 81T drum gear, the 45T screw gear, the traveller frame, the fixed roller bracket, the top tie, the
  far-end screw stand, the screw-end tower, the rope clamp ring, the exit bearing housing, the exit carrier, its retainers
  and rail caps.
- **PA-CF:** the motor-end and battery-end pieces, the ODrive bracket, the latch finger bar and the service lid.
- **PETG-CF:** the two covers (end caps printed in) and the rear I/O panel.
- **PETG:** the screen frame, the front board plate and its standoffs, the WAGO bracket, the fan duct, and the TP2700
  battery spacer (only with the TP2700 pair).
- **TPU 95A or EVA foam:** the three battery pads.
- **PETG or PLA:** the five drill guides for the edge holes (tools, not parts of the machine).

The Lite adds a printed tray for its power supply and leaves out the battery parts, the screen frame and the rear I/O
panel.
