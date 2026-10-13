# Electronics and firmware setup

> **Draft.** The control software is not released yet: the touchscreen app for the Raspberry Pi, the Teensy control
> firmware and the phone app are published after the prototype has been built and load-tested. This page lists what the
> setup must achieve before the motor is ever powered with the rope attached. The values are design values, to be
> confirmed on the prototype.

## What runs where

| Part | Role | Status |
|---|---|---|
| ODrive Pro (battery builds) or ODrive S1 (Lite) | motor control, current and voltage limits, encoder | third-party firmware, configured by you |
| Teensy 4.0 (battery builds) | machine control: modes, limits, homing; talks to the ODrive over CAN | released after testing |
| Raspberry Pi 4 and touch screen (battery builds) | resistance, the repetition graph and the controls; talks to the Teensy over USB | released after testing |
| XIAO ESP32-C3 and knob (Lite) | Bluetooth link to the phone app; talks to the ODrive S1 over CAN | released after testing |
| Phone app | settings, workouts and history over Bluetooth | released after testing |

The ODrive is a third-party controller with its own firmware and terms. Check every setting against the documentation for
your ODrive firmware version.

## Power path (battery builds)

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
  32.4 A for the TP2700 pair) and no more than the BMS, wiring and junction are sized for. The draft value is 28 A.
- If the BMS stops accepting charge (full pack, over-temperature), the ODrive trips on over-voltage and the cable goes
  slack. The 80 % charge level is there to prevent this.

**Current.** Set the motor current limit for your motor and your build's peak force, inside the controller's rating. On the
ODrive Pro, 70 A is the continuous figure and 100 A is available for about 3 s. The main build reaches 158 lb as a peak
(about 74 A); sustained sets run lower (about 150 lb).

**Motor and encoder.**

- Enter your motor's pole pairs and torque constant, and run the motor calibration.
- The encoder is the controller's on-board magnetic sensor, reading the diametric magnet glued into the drum shaft end. It is
  absolute within one turn only, so the drum must be homed at every power-up.
- Run the anticogging calibration, and add a small friction feed-forward. Together they correct the back-drive feel,
  including the drag of the level-wind's gears and lead screw.
- Inertia compensation: the firmware adds the rotor's inertia times the drum's measured acceleration to the torque command,
  so the rotor does not feel like a flywheel. Measure the rotor inertia with a spin-down test; do not take it from a
  listing.

## Payout window (must be set)

The drum is direct drive: one motor turn is one drum turn, about 110 mm of rope at the rope's radius. The level-wind moves
3.6 mm per drum turn.

| Check | Design value |
|---|---|
| Tracked rope, fully wound to full payout | about 2.11 m, 19.2 drum turns |
| Dead wraps left on the drum at full payout | 3 (wound on by hand during assembly) |
| Traveller hard stops | about 1.3 drum turns past each end of the track |

1. **Home** at every power-up: wind the rope in at low, current-limited torque until the handle stops at the exit. That
   position is zero (fully wound).
2. **Payout limit:** from zero, the full tracked length less a small margin, so the three dead wraps always stay on the
   drum.
3. Enforce the window in the controlling firmware and, where your ODrive firmware supports position limits, in the ODrive
   as well.

The traveller's hard stops (the far-end stand's foot and the screw-end tower's foot) are an assembly and hand-turning
backstop only. The lead screw is geared to the drum, so a stop hit under power locks the drum through the printed gears.

## First power-up checklist

1. Rope off the drum or unloaded, nobody in its path.
2. Power on. If the BMS trips on the ODrive's capacitor inrush, lengthen the BMS short-circuit delay in the BMS app.
3. Calibrate the motor and the encoder.
4. Turn the drum slowly by command. Confirm which direction winds the rope in, and that the traveller moves toward the
   screw-end tower while winding.
5. Home, then set and test the payout window with the rope attached and no load.
6. Check the over-voltage trip and the regen limit with light lowering loads.
7. Static load test in steps (see the [safety reference](https://kinetiqgym.com/docs/SAFETY.html)).

## Teensy 4.0 (battery builds)

- Power: 5 V from the regulator to VIN. **Cut the VIN-VUSB pad**: the Teensy is also connected to the Pi by USB.
- CAN: Teensy CAN TX/RX to the SN65HVD230 board, then CAN H, CAN L and GND to the ODrive's CAN header (twisted pair).

## Lite (ODrive S1 on wall power)

- The 36 V supply cannot absorb braking energy. Configure the S1's brake resistor output for the 2 Ω resistor bank (two
  1 Ω resistors in series) so regenerative energy goes into the resistors.
- Set the DC current limits to what the Mean Well LOP-600-36 can deliver: 600 W with airflow (400 W by convection), 150 %
  for 3 s.
- The S1 has its own on-board magnetic encoder over the same drum-shaft magnet. Homing and the payout window are the same as
  above.
