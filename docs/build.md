# Build instructions (printed variant)

Read `SAFETY.md` first. Order matters: some parts cannot be reached once others are in. Part names below match the files in
`print/`, `cad/step/` and the FreeCAD assembly (open `cad/freecad/printed/V44_printed_assembly.FCStd` alongside this page).

## 0. Before you start

1. Print the fit coupons (`print/fit-coupons/`) in your material and tune the insert and clearance holes (`printing.md`).
2. Print every part in `print/` (see `print/README.md` for material, orientation and the inserts each part takes).
3. Buy the parts in `bom/BOM.md`; cut nothing metal (the printed variant only drills the two aluminium flat bars).

## 1. Heat-set inserts

Press every brass insert (Ruthex RX, M2.5 / M3 / M4 x 4 mm) into its pocket with a soldering iron and an insert tip, square
to the face. `print/README.md` lists the inserts per part; the assembly shows each insert inside its part.

## 2. Base: bottom plate and flat bars

1. Drill the two 1 x 1/4 in aluminium flat bars (front and rear) at the countersunk holes of `S17_V44_AL_flat_bar_*`; countersink.
2. Join the two printed bottom-plate halves (`S01_V44_PRINT_bottom_plate_left` / `_right`, split at X 75) and screw the
   bars on from below: M4 x 10 countersunk into the plate inserts (14 joints, `bar_*` in the table below).

## 3. Drivetrain (motor end to gear end)

1. Motor face plate and gussets to the base; motor to the face plate (M5 into the motor, spacers per the model).
2. The two 6001 bearing cartridges (`V43_PRINT_6001_cartridge_*`) with their bearings, onto the base. **Bearing blocks go on
   before the drum.**
3. Drum assembly: drum, goBILDA hubs with their screws into the drum inserts, rope anchor. **The drum shaft slides in from the
   ODrive end** through both bearings and the drum hubs; coupling to the motor shaft.
4. Drum 60T gear and hub on the shaft end; encoder magnet in the shaft end.

## 4. Fairlead module

The fairlead (sheave, worm-wheel carrier, worm, shaft 2 and the exit swivel) is a module on the square back plate:
1. 6809 bearing into the back plate; the printed carrier's journal into it; sheave and rope-turn roller on their axles.
2. Worm shaft (6 mm D) with the KHK worm and its 20T gear on two flanged bearings; shaft 2 (8 mm REX) with its 60T and 20T on the
   printed pedestals (printed into the right bottom plate on this variant).
3. Exit swivel: housing with two 6808 bearings, the oval ring carrier with the two U625ZZ pulleys, retainers and the
   countersunk hub screws; housing onto the back-plate face (4 x M3 into inserts).
4. Module onto the base (2 x M4 from below). Check that the 60T gears mesh at 48 mm centres and the carrier turns freely
   +-45 deg by hand (it stops at +-48.4 deg).

## 5. Electronics

1. **Shaft 2 and the ODrive go in before the battery.** ODrive Pro on its printed bracket (heat spreader on 4 x M4 x 16, nuts in
   the bracket pockets); fan and duct on the rear wall.
2. Front board plate with the regulator, Teensy and CAN perfboards. **Screw the Teensy perfboard down before plugging the
   Teensy into its sockets** (the two screws sit under it).
3. Main fuse holder: **fuse cradles before the holder** (printed in on this variant); WAGO on its junction bracket.
4. Battery packs into the saddles (they slide in from the front, 1 mm foam on top); BMS on the right cover ceiling;
   Raspberry Pi on the left cover ceiling.

## 6. Wiring

Follow `wiring.md`. Thread the harness through the wire loops under the cover tops before fitting the far connectors.

## 7. Rope

Wind 3 dead wraps by hand at the anchor end, then wind the rope on under light tension through the sheave, roller and exit.
Set the payout window before the first loaded pull (`firmware-setup.md`).

## 8. Covers

Covers and end caps stand on the bottom plate: M3 from below into the foot bosses, and M3 countersunk from the back into the
rear wall. Rear I/O panel last (2 tabs, M2.5).

## Fasteners by joint

Generated from the model (`fasteners-report.json`): every screw, the parts it passes through and what it engages.

| Joint | Screw | Through / into | Note |
|---|---|---|---|
| bar_0 | M4x10 csk | S17_V44_AL_flat_bar_front_1x0.25x12in -> S01_V44_PRINT_bottom_plate_left | Flat bar to the printed bottom plate: M4 countersunk up through the bar into a heat-set insert. |
| bar_1 | M4x10 csk | S17_V44_AL_flat_bar_rear_1x0.25x12in -> S01_V44_PRINT_bottom_plate_left | Flat bar to the printed bottom plate: M4 countersunk up through the bar into a heat-set insert. |
| bar_2 | M4x10 csk | S17_V44_AL_flat_bar_front_1x0.25x12in -> S01_V44_PRINT_bottom_plate_left | Flat bar to the printed bottom plate: M4 countersunk up through the bar into a heat-set insert. |
| bar_3 | M4x10 csk | S17_V44_AL_flat_bar_rear_1x0.25x12in -> S01_V44_PRINT_bottom_plate_left | Flat bar to the printed bottom plate: M4 countersunk up through the bar into a heat-set insert. |
| bar_4 | M4x10 csk | S17_V44_AL_flat_bar_front_1x0.25x12in -> S01_V44_PRINT_bottom_plate_left | Flat bar to the printed bottom plate: M4 countersunk up through the bar into a heat-set insert. |
| bar_5 | M4x10 csk | S17_V44_AL_flat_bar_rear_1x0.25x12in -> S01_V44_PRINT_bottom_plate_left | Flat bar to the printed bottom plate: M4 countersunk up through the bar into a heat-set insert. |
| bar_6 | M4x10 csk | S17_V44_AL_flat_bar_front_1x0.25x12in -> S01_V44_PRINT_bottom_plate_left -> S01_V44_PRINT_bottom_plate_right | Flat bar to the printed bottom plate: M4 countersunk up through the bar into a heat-set insert. |
| bar_7 | M4x10 csk | S17_V44_AL_flat_bar_rear_1x0.25x12in -> S01_V44_PRINT_bottom_plate_left -> S01_V44_PRINT_bottom_plate_right | Flat bar to the printed bottom plate: M4 countersunk up through the bar into a heat-set insert. |
| bar_8 | M4x10 csk | S17_V44_AL_flat_bar_front_1x0.25x12in -> S01_V44_PRINT_bottom_plate_left -> S01_V44_PRINT_bottom_plate_right | Flat bar to the printed bottom plate: M4 countersunk up through the bar into a heat-set insert. |
| bar_9 | M4x10 csk | S17_V44_AL_flat_bar_rear_1x0.25x12in -> S01_V44_PRINT_bottom_plate_left -> S01_V44_PRINT_bottom_plate_right | Flat bar to the printed bottom plate: M4 countersunk up through the bar into a heat-set insert. |
| bar_10 | M4x10 csk | S17_V44_AL_flat_bar_front_1x0.25x12in -> S01_V44_PRINT_bottom_plate_right | Flat bar to the printed bottom plate: M4 countersunk up through the bar into a heat-set insert. |
| bar_11 | M4x10 csk | S17_V44_AL_flat_bar_rear_1x0.25x12in -> S01_V44_PRINT_bottom_plate_right | Flat bar to the printed bottom plate: M4 countersunk up through the bar into a heat-set insert. |
| bar_12 | M4x10 csk | S17_V44_AL_flat_bar_front_1x0.25x12in -> S01_V44_PRINT_bottom_plate_right | Flat bar to the printed bottom plate: M4 countersunk up through the bar into a heat-set insert. |
| bar_13 | M4x10 csk | S17_V44_AL_flat_bar_rear_1x0.25x12in -> S01_V44_PRINT_bottom_plate_right | Flat bar to the printed bottom plate: M4 countersunk up through the bar into a heat-set insert. |
| odrive_foot_0 | M4x16 csk | S17_V44_AL_flat_bar_front_1x0.25x12in -> S01_V44_PRINT_bottom_plate_right -> MOUNT_ODrive_Pro_bracket_printed_PA-CF_base-mounted | ODrive bracket foot: M4 up through bar and plate slot into its insert. |
| odrive_foot_1 | M4x16 csk | S17_V44_AL_flat_bar_rear_1x0.25x12in -> S01_V44_PRINT_bottom_plate_right -> MOUNT_ODrive_Pro_bracket_printed_PA-CF_base-mounted | ODrive bracket foot: M4 up through bar and plate slot into its insert. |
| exit_plate_0 | M4x10 csk | S01_V44_PRINT_bottom_plate_right -> FM10_Square_back_plate_4-screw_enclosure_mount | Square back plate (fairlead) to the bottom plate: M4 up into its insert. |
| exit_plate_1 | M4x10 csk | S01_V44_PRINT_bottom_plate_right -> FM10_Square_back_plate_4-screw_enclosure_mount | Square back plate (fairlead) to the bottom plate: M4 up into its insert. |
| board_plate_0 | M3x6 socket | S01_V44_PRINT_bottom_plate_left -> MOUNT_front_board_plate_printed | Front board plate foot: M3 up through the plate (head in a counterbore) into its insert. |
| board_plate_1 | M3x6 socket | S01_V44_PRINT_bottom_plate_left -> MOUNT_front_board_plate_printed | Front board plate foot: M3 up through the plate (head in a counterbore) into its insert. |
| cover_back_0 | M3x10 csk | S01_V44_PRINT_bottom_plate_left -> V44_PRINT_cover_left_screen | Cover to the rear plate: M3 countersunk from the back (flush, D6) into the cover boss insert. |
| cover_back_1 | M3x10 csk | S01_V44_PRINT_bottom_plate_left -> V44_PRINT_cover_left_screen | Cover to the rear plate: M3 countersunk from the back (flush, D6) into the cover boss insert. |
| cover_back_2 | M3x10 csk | S01_V44_PRINT_bottom_plate_left -> S01_V44_PRINT_bottom_plate_right -> V44_PRINT_cover_left_screen | Cover to the rear plate: M3 countersunk from the back (flush, D6) into the cover boss insert. |
| cover_back_3 | M3x10 csk | S01_V44_PRINT_bottom_plate_right -> V44_PRINT_cover_right_grille | Cover to the rear plate: M3 countersunk from the back (flush, D6) into the cover boss insert. |
| cover_back_4 | M3x10 csk | S01_V44_PRINT_bottom_plate_right -> V44_PRINT_cover_right_grille | Cover to the rear plate: M3 countersunk from the back (flush, D6) into the cover boss insert. |
| cover_foot_0 | M3x8 csk | S01_V44_PRINT_bottom_plate_left -> V44_PRINT_cover_left_screen | Cover / cap foot boss: M3 up through the plate into its insert. |
| cover_foot_1 | M3x8 csk | S01_V44_PRINT_bottom_plate_left -> S01_V44_PRINT_bottom_plate_right -> V44_PRINT_cover_left_screen | Cover / cap foot boss: M3 up through the plate into its insert. |
| cover_foot_2 | M3x8 csk | S01_V44_PRINT_bottom_plate_right -> V44_PRINT_cover_right_grille | Cover / cap foot boss: M3 up through the plate into its insert. |
| cover_foot_3 | M3x8 csk | S01_V44_PRINT_bottom_plate_right -> V44_PRINT_cover_right_grille | Cover / cap foot boss: M3 up through the plate into its insert. |
| cover_foot_4 | M3x8 csk | S01_V44_PRINT_bottom_plate_right -> V44_PRINT_cover_right_grille | Cover / cap foot boss: M3 up through the plate into its insert. |
| cover_foot_5 | M3x8 csk | S01_V44_PRINT_bottom_plate_right -> V44_PRINT_cover_right_grille | Cover / cap foot boss: M3 up through the plate into its insert. |
| cover_foot_6 | M3x8 csk | S01_V44_PRINT_bottom_plate_right -> V44_PRINT_cover_right_grille | Cover / cap foot boss: M3 up through the plate into its insert. |
| cover_foot_7 | M3x8 csk | S01_V44_PRINT_bottom_plate_right -> V44_PRINT_cover_right_grille -> V44_PRINT_end_cap_battery | Cover / cap foot boss: M3 up through the plate into its insert. |
| cover_foot_8 | M3x8 csk | S01_V44_PRINT_bottom_plate_left -> V44_PRINT_end_cap_motor | Cover / cap foot boss: M3 up through the plate into its insert. |
| cover_foot_9 | M3x16 csk | S17_V44_AL_flat_bar_rear_1x0.25x12in -> S01_V44_PRINT_bottom_plate_left -> V44_PRINT_end_cap_motor | Cover / cap foot boss: M3 up through the bar and plate into its insert. |
| cover_foot_10 | M3x8 csk | S01_V44_PRINT_bottom_plate_right -> V44_PRINT_end_cap_battery | Cover / cap foot boss: M3 up through the plate into its insert. |
| fan_0 | M3x25 csk | S01_V44_PRINT_bottom_plate_right -> MOUNT_fan_duct_mount_frame_printed -> TRIAL_driver_fan | ODrive fan: M3 countersunk from the back (flush, D6) through the rear plate and duct, self-tapping into the fan corner holes. |
| fan_1 | M3x25 csk | S01_V44_PRINT_bottom_plate_right -> MOUNT_fan_duct_mount_frame_printed -> TRIAL_driver_fan | ODrive fan: M3 countersunk from the back (flush, D6) through the rear plate and duct, self-tapping into the fan corner holes. |
| fan_2 | M3x25 csk | S01_V44_PRINT_bottom_plate_right -> MOUNT_fan_duct_mount_frame_printed -> TRIAL_driver_fan | ODrive fan: M3 countersunk from the back (flush, D6) through the rear plate and duct, self-tapping into the fan corner holes. |
| fan_3 | M3x25 csk | S01_V44_PRINT_bottom_plate_right -> MOUNT_fan_duct_mount_frame_printed -> TRIAL_driver_fan | ODrive fan: M3 countersunk from the back (flush, D6) through the rear plate and duct, self-tapping into the fan corner holes. |
| wago_bracket_0 | M3x8 socket | MOUNT_power_junction_bracket_printed -> S01_V44_PRINT_bottom_plate_right | WAGO bracket: M3 into a rear-plate insert. |
| wago_bracket_1 | M3x8 socket | MOUNT_power_junction_bracket_printed -> S01_V44_PRINT_bottom_plate_right | WAGO bracket: M3 into a rear-plate insert. |
| screen_leg_0 | M3x8 csk | V44_PRINT_cover_left_screen -> MOUNT_screen_rear_retaining_frame_printed | Screen frame leg: M3 countersunk from the front (flush under the bezel edge) into the leg insert. |
| screen_leg_1 | M3x8 csk | V44_PRINT_cover_left_screen -> MOUNT_screen_rear_retaining_frame_printed | Screen frame leg: M3 countersunk from the front (flush under the bezel edge) into the leg insert. |
| pi_top_0 | M2.5x5 csk | V44_PRINT_cover_left_screen -> MOUNT_Pi_ceiling_standoffs_M2.5 | Pi standoff to the cover top: M2.5 countersunk from above. |
| pi_board_0 | M2.5x6 socket | TRIAL_Pi4_upright -> MOUNT_Pi_ceiling_standoffs_M2.5 | Pi to its standoff: M2.5 from below through the board. |
| pi_top_1 | M2.5x5 csk | V44_PRINT_cover_left_screen -> MOUNT_Pi_ceiling_standoffs_M2.5 | Pi standoff to the cover top: M2.5 countersunk from above. |
| pi_board_1 | M2.5x4 socket | TRIAL_Pi4_upright -> MOUNT_Pi_ceiling_standoffs_M2.5 | Pi to its standoff: M2.5 from below through the board. |
| pi_top_2 | M2.5x5 csk | V44_PRINT_cover_left_screen -> MOUNT_Pi_ceiling_standoffs_M2.5 | Pi standoff to the cover top: M2.5 countersunk from above. |
| pi_board_2 | M2.5x4 socket | TRIAL_Pi4_upright -> MOUNT_Pi_ceiling_standoffs_M2.5 | Pi to its standoff: M2.5 from below through the board. |
| pi_top_3 | M2.5x5 csk | V44_PRINT_cover_left_screen -> MOUNT_Pi_ceiling_standoffs_M2.5 | Pi standoff to the cover top: M2.5 countersunk from above. |
| pi_board_3 | M2.5x4 socket | TRIAL_Pi4_upright -> MOUNT_Pi_ceiling_standoffs_M2.5 | Pi to its standoff: M2.5 from below through the board. |
| bms_4 | M3x12 csk | V44_PRINT_cover_right_grille -> MOUNT_BMS_ceiling_standoffs_M3 -> JBD_SP17S005_BMS_mock_from_spec | BMS to the cover top: M3 countersunk from above through the spacer and board, nut under the board. |
| bms_5 | M3x12 csk | V44_PRINT_cover_right_grille -> MOUNT_BMS_ceiling_standoffs_M3 -> JBD_SP17S005_BMS_mock_from_spec | BMS to the cover top: M3 countersunk from above through the spacer and board, nut under the board. |
| bms_6 | M3x12 csk | V44_PRINT_cover_right_grille -> MOUNT_BMS_ceiling_standoffs_M3 -> JBD_SP17S005_BMS_mock_from_spec | BMS to the cover top: M3 countersunk from above through the spacer and board, nut under the board. |
| bms_7 | M3x12 csk | V44_PRINT_cover_right_grille -> MOUNT_BMS_ceiling_standoffs_M3 -> JBD_SP17S005_BMS_mock_from_spec | BMS to the cover top: M3 countersunk from above through the spacer and board, nut under the board. |
| xt60_0 | M2.5x5 csk | AMASS_XT60E-F_charge_port -> V44_PRINT_rear_IO_panel_flush | XT60E-F flange: M2.5 countersunk (countersink the flange holes) self-tapping into the backing frame. |
| xt60_1 | M2.5x5 csk | AMASS_XT60E-F_charge_port -> V44_PRINT_rear_IO_panel_flush | XT60E-F flange: M2.5 countersunk (countersink the flange holes) self-tapping into the backing frame. |
| io_tab_0 | M2.5x5 socket | V44_PRINT_rear_IO_panel_flush -> V44_PRINT_cover_right_grille | Rear I/O panel tab: M2.5 self-tapping into the step wall. |
| io_tab_1 | M2.5x5 socket | V44_PRINT_rear_IO_panel_flush -> V44_PRINT_cover_right_grille | Rear I/O panel tab: M2.5 self-tapping into the step wall. |
| odrive_spreader_0 | M4x12 socket | V3_ODrive_heat_spreader_SUPPLIER_CAD -> MOUNT_ODrive_Pro_bracket_printed_PA-CF_base-mounted | ODrive heat spreader to the bracket post: M4 from the board side, nut in the hex pocket on the far face. |
| odrive_spreader_1 | M4x12 socket | V3_ODrive_heat_spreader_SUPPLIER_CAD -> MOUNT_ODrive_Pro_bracket_printed_PA-CF_base-mounted | ODrive heat spreader to the bracket post: M4 from the board side, nut in the hex pocket on the far face. |
| odrive_spreader_2 | M4x12 socket | V3_ODrive_heat_spreader_SUPPLIER_CAD -> MOUNT_ODrive_Pro_bracket_printed_PA-CF_base-mounted | ODrive heat spreader to the bracket post: M4 from the board side, nut in the hex pocket on the far face. |
| odrive_spreader_3 | M4x12 socket | V3_ODrive_heat_spreader_SUPPLIER_CAD -> MOUNT_ODrive_Pro_bracket_printed_PA-CF_base-mounted | ODrive heat spreader to the bracket post: M4 from the board side, nut in the hex pocket on the far face. |
| standoff_Teensy_0 | M2.5x12 socket | TRIAL_Teensy -> MOUNT_Teensy_perfboard_standoffs -> MOUNT_front_board_plate_printed | Board standoff: M2.5 through the board and the standoff into a front-plate insert. |
| standoff_Teensy_1 | M2.5x12 socket | TRIAL_Teensy -> MOUNT_Teensy_perfboard_standoffs -> MOUNT_front_board_plate_printed | Board standoff: M2.5 through the board and the standoff into a front-plate insert. |
| standoff_CAN_0 | M2.5x10 socket | TRIAL_CAN_headers -> MOUNT_CAN_board_perfboard_standoffs -> MOUNT_front_board_plate_printed | Board standoff: M2.5 through the board and the standoff into a front-plate insert. |
| standoff_CAN_1 | M2.5x10 socket | TRIAL_CAN_headers -> MOUNT_CAN_board_perfboard_standoffs -> MOUNT_front_board_plate_printed | Board standoff: M2.5 through the board and the standoff into a front-plate insert. |
| standoff_CAN_2 | M2.5x10 socket | TRIAL_CAN_headers -> MOUNT_CAN_board_perfboard_standoffs -> MOUNT_front_board_plate_printed | Board standoff: M2.5 through the board and the standoff into a front-plate insert. |
| standoff_CAN_3 | M2.5x10 socket | TRIAL_CAN_headers -> MOUNT_CAN_board_perfboard_standoffs -> MOUNT_front_board_plate_printed | Board standoff: M2.5 through the board and the standoff into a front-plate insert. |
| standoff_regulator_0 | M2.5x12 socket | TRIAL_Pololu5571 -> MOUNT_regulator_perfboard_standoffs -> MOUNT_front_board_plate_printed | Board standoff: M2.5 through the board and the standoff into a front-plate insert. |
| standoff_regulator_1 | M2.5x12 socket | TRIAL_Pololu5571 -> MOUNT_regulator_perfboard_standoffs -> MOUNT_front_board_plate_printed | Board standoff: M2.5 through the board and the standoff into a front-plate insert. |
| standoff_regulator_2 | M2.5x12 socket | TRIAL_Pololu5571 -> MOUNT_regulator_perfboard_standoffs -> MOUNT_front_board_plate_printed | Board standoff: M2.5 through the board and the standoff into a front-plate insert. |
| standoff_regulator_3 | M2.5x12 socket | TRIAL_Pololu5571 -> MOUNT_regulator_perfboard_standoffs -> MOUNT_front_board_plate_printed | Board standoff: M2.5 through the board and the standoff into a front-plate insert. |
