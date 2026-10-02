# Electronics and firmware setup

The control app (Raspberry Pi touch screen + Teensy 4.0 over CAN to the ODrive) is not part of this release yet.
This page covers what must be configured before the motor is ever powered with the rope attached.

## Power path

- Pack: 2 x Thunder Power TP2700-5SR70 (5S) in series = 10S, 30-42 V, through a JBD SP17S005 10S BMS.
- The power button on the rear I/O panel switches the BMS (signal only). The EC5 plugs on the packs are the service
  disconnect: plug them in with the BMS switched off.
- Charging: XT60E-F port on the rear panel -> 7.5 A 58 V fuse -> BMS. Charge to about 80 % for training (room for braking energy).
- See `wiring.md` for every wire.

## ODrive Pro

Check the property names against the documentation for your firmware version.

| Setting | Value | Why |
|---|---|---|
| DC bus over-voltage trip | about 45 V | under the ODrive (58 V) and regulator (60 V) limits; braking energy charges the pack |
| Max regen (negative DC) current | 28 A | what the BMS and wiring are sized for |
| Motor | your motor's pole pairs, Kv, current limit | the reference motor is about 50 Kv, 13 N·m peak, 1.25 kg |
| Encoder | the ODrive Pro's on-board MA702 with the diametric magnet on the drum-shaft end | absolute within one turn only |

## Payout window (must be set)

The drum is direct-drive (one motor turn = one drum turn, 157.6 mm of rope per turn at the rope centre).

1. **Home** at power-up: wind the rope fully in until the handle stops at the exit (low torque, current-limited); that is
   position 0 (the fairlead carrier is then at +45.4 deg).
2. **Payout limit:** 13.26 turns from home (full payout is 13.36 turns, where the rope reaches the 3 hand-wound dead wraps;
   the limit keeps 16 mm in hand).
3. Enforce the window in the controlling firmware (Teensy) and, where your ODrive firmware supports position limits, in the
   ODrive as well.

The two hard stops on the fairlead carrier engage 0.45 turn past full payout (+-48.4 deg). They are an assembly / hand-turning
backstop only: the worm cannot be back-driven, so hitting a stop under power locks the drum through the gear train.

| Check | Value |
|---|---|
| Tracked rope (full wind to full payout) | 2.11 m, 13.36 drum turns |
| Carrier swing over that range | +45.4 deg (full wind) to -45.4 deg (full payout), 1/53 of a turn per drum turn |
| Hard stops | +-48.4 deg (clear at 48.4, blocked by 48.8 in CAD) |
| Rope lay pitch on the drum | 3.3-5.8 mm per turn (rope 3.175 mm), never overlapping |

## First power-up checklist

1. Rope off the drum or unloaded. Power on; if the BMS trips on the ODrive's capacitor inrush, lengthen the BMS short-circuit
   delay in the BMS app.
2. Calibrate the motor and encoder (ODrive procedure).
3. Turn the drum slowly by command: confirm the direction that winds the rope in, and that the fairlead carrier moves toward
   +45 deg while winding.
4. Set and test the payout window with the rope attached and no load.
5. Static load test in steps (see `SAFETY.md`).

## Teensy 4.0

- Power: 5 V from the regulator to VIN; **cut the VIN-VUSB pad** (it is also connected to the Pi by USB).
- CAN: Teensy CAN TX/RX to the SN65HVD230 board, CAN H / L / GND to the ODrive CAN header (twisted pair).
