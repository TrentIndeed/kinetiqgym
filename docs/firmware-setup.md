# Electronics and firmware setup

> **Draft.** The control software is not released yet: the touchscreen app for the Raspberry Pi, the Teensy control
> firmware and the phone app are published after the prototype has been built and load-tested. This page lists what the
> setup must achieve before the motor is ever powered with the rope attached. The values are design values, to be
> confirmed on the prototype and on the bench.

## What runs where

| Part | Role | Status |
|---|---|---|
| ODrive Pro (main build) or ODESC V4.2 (budget build) | motor control, current and voltage limits, encoder, motor temperature | third-party firmware, configured by you |
| Teensy 4.0 (main build) | machine control: modes, limits, homing; talks to the ODrive over CAN | released after testing |
| Raspberry Pi 4 and touch screen (main build) | resistance, the repetition graph and the controls; talks to the Teensy over USB | released after testing |
| XIAO ESP32-C3, knob and start/stop button (budget build) | Bluetooth link to the phone app; talks to the ODESC over UART | released after testing |
| Phone app | settings, workouts and history over Bluetooth | released after testing |

The ODrive and the ODESC are third-party controllers with their own firmware and terms. Check every setting against the
documentation for your controller's firmware version.

## Power path (main build)

- Pack: two Thunder Power 5S LiPo packs (TP3300-5SR70 or TP2700-5SR70) in series: 10S, 30-42 V, through a JBD 10S BMS.
- The power button on the rear I/O panel switches the BMS (a signal only). The EC5 plugs on the packs are the service
  disconnect: plug them in with the BMS switched off.
- Charging: the XT60E-F port, a 10 A 58 V fuse, the BMS. For training, charge to about 80 %: that leaves room in the pack for
  braking energy.
- Every wire is in [wiring.md](wiring.md).

## Controller requirements

**Voltage and regenerative braking.** Lowering the weight drives the motor as a generator and pushes current back into
the pack.

- Set the DC bus over-voltage trip to about 45 V: under the ODrive Pro's 58 V and the regulator's 60 V limits.
- Limit the regenerative (negative) DC current to no more than the pack pair's charge rating (39.6 A for the TP3300 pair,
  32.4 A for the TP2700 pair) and no more than the BMS, wiring and junction are sized for. The draft value is 28 A; paying
  out 220 lb fast regenerates about 20 A.
- Limit the positive DC current to 40 A, and have the app cap the return (reel-in) speed at high force so the battery
  current stays under 36 A (90 % of the 40 A fuse). The cap only acts at high force.
- If the BMS stops accepting charge (full pack, over-temperature), the ODrive trips on over-voltage and the cable goes
  slack. The 80 % charge level is there to prevent this.

**Current.** 220 lb takes about 75 A at the main build's 12.7 mm rope radius: set the motor current limit to about 75.5 A
(80 A gives about 234 lb, and the frame is checked for that). ODrive's datasheet allows 80 A with active cooling; the
100 A burst is not used for the rating. The MP8085's torque against current is not published: measure it to 80 A before
relying on the rating. If the motor saturates early, the most it can pull is lower.

**Motor temperature.** A 10 k NTC thermistor (B3950) glued to the stator goes to the ODrive's motor-thermistor input. Set
it to roll the current back from 90 °C and cut it at 110 °C. By the design estimate the motor manages about two full
220 lb sets of 30 s back to back before the roll-back starts; lighter sets run far cooler. Log it during the first heat
runs (80 A, 30 s on, 3 min off).

**Motor and encoder.**

- Enter your motor's pole pairs and torque constant, and run the motor calibration.
- The encoder is the controller's on-board magnetic sensor, reading the diametric magnet glued into the drum shaft end. It is
  absolute within one turn only, so the drum must be homed at every power-up.
- Run the anticogging calibration, and add a small friction feed-forward. Together they correct the back-drive feel,
  including the drag of the level-wind's gears and lead screw.
- Inertia compensation: the firmware adds the rotor's inertia times the drum's measured acceleration to the torque command,
  so the rotor does not feel like a flywheel. The main build feels about 6.3 kg at the rope before compensation; cancelling
  about 29 % of it lets the 10 lb minimum feel like 10 lb. Measure the rotor inertia with a spin-down test; do not take it
  from a listing.

## Payout window (must be set)

The drum is direct drive: one motor turn is one drum turn, about 80 mm of rope at the main build's 12.7 mm rope radius.
The level-wind moves 3.6 mm per drum turn.

| Check | Design value (main build) |
|---|---|
| Tracked rope, fully wound to full payout | about 2.60 m, 32.7 drum turns |
| Dead wraps left on the drum at full payout | 3 (wound on by hand during assembly) |
| Traveller hard stops | about 1.3 drum turns past each end of the track |

1. **Home** at every power-up: wind the rope in at low, current-limited torque until the handle stops at the exit. That
   position is zero (fully wound).
2. **Payout limit:** from zero, the full tracked length less a small margin, so the three dead wraps always stay on the
   drum.
3. Enforce the window in the controlling firmware and, where your controller's firmware supports position limits, in the
   controller as well.

The traveller's hard stops (the far-end stand's foot and the screw-end tower's foot) are an assembly and hand-turning
backstop only. The lead screw is geared to the drum, so a stop hit under power locks the drum through the printed gears.

## First power-up checklist

1. Rope off the drum or unloaded, nobody in its path.
2. Power on. If the BMS trips on the ODrive's capacitor inrush, lengthen the BMS short-circuit delay in the BMS app.
3. Calibrate the motor and the encoder. Check that the motor thermistor reads room temperature.
4. Turn the drum slowly by command. Confirm which direction winds the rope in, and that the traveller moves toward the
   screw-end tower while winding.
5. Home, then set and test the payout window with the rope attached and no load.
6. Check the over-voltage trip and the regen limit with light lowering loads.
7. Static load test in steps (see the [safety reference](https://kinetiqgym.com/docs/SAFETY.html)).

## Teensy 4.0 (main build)

- Power: 5 V from the regulator to VIN. **Cut the VIN-VUSB pad**: the Teensy is also connected to the Pi by USB.
- CAN: Teensy CAN TX/RX to the SN65HVD230 board, then CAN H, CAN L and GND to the ODrive's CAN header (twisted pair).

## Budget build (ODESC V4.2 on wall power)

- **Current:** 180 lb takes about 69 A at the budget build's 14.3 mm rope radius. The ODESC's 70 A continuous rating is the
  seller's and unverified: bench-test it (68 A for 30 s, three times, with 3 min rest) before relying on it. If it only
  holds about 53 A, set the limit there: the build then tops out near 138 lb.
- **Braking:** the 48 V supply cannot absorb braking energy. Configure the ODESC's brake resistor output for the 2 Ω bank
  (two 1 Ω resistors in series) so regenerative energy goes into the resistors: about 24 A (810 W) at most when a 180 lb
  pull pays out at 1.5 m/s. Above about 1.9 m/s at full force the firmware rolls the force off.
- **Supply limits:** the Mean Well LRS-600N2-48 gives 600 W, and 1,200 W for 5 s. Holding 180 lb takes about 394 W, but
  winding the rope back in at 180 lb takes more than the supply can give for long, so the firmware caps the return speed at
  high force (about 0.26 m/s sustained at 180 lb).
- **Motor temperature:** the stator NTC, with its 10 kΩ divider, to the ODESC's thermistor input: roll the current back
  from 90 °C. By the design estimate the motor manages about three full 180 lb sets back to back before that; a 40 mm fan on
  the motor pod would raise it to about ten.
- **Encoder and feel:** the AS5047P board reads a magnet in the drum's end. The budget build feels about 5.9 kg at the rope
  before compensation; cancelling about 24 % of it lets 10 lb feel like 10 lb.
- **Payout:** 2.0 m of tracked rope; the budget build keeps about 6.7 dead wraps on its drum. Homing and the payout window
  work as above.
