# Project roadmap

> **Status, October 27, 2026:** the builds moved to an off-the-shelf motor. The main build (220 lb) and the budget build
> (180 lb) are drawn in CAD; the wall build (300 lb) is in design. Next come bench tests of the motor and the controllers and
> the aluminum prototype of the main build. Everything published so far is a draft until a prototype has been built and
> load-tested.

## Where things stand

| Stage | Status |
|---|---|
| CAD design, main build: the bolted aluminum frame, the drivetrain, the level-wind, the exit and the rack side, on the MP8085 | done, draft |
| CAD design, budget build: its own hacksaw-cut frame on wall power, on the MP8085 | done, draft |
| CAD design, wall build: 300 lb, bolted to wall studs or concrete | in design |
| Printed fit test of the whole assembly | done, on an earlier revision |
| Bench tests: the MP8085's torque against current, the ODrive Pro and ODESC currents through a set, motor heat | next |
| Aluminum prototype build (main build: MP8085, 10S battery) | next |
| Load testing: static load in steps, then powered tests and thermal checks | after the build |
| Verified release: CAD, build files and software | after load testing |
| Metal kits made by Trent, the project's maker | after the verified release |

## The verified release

Nothing is released before the design is proven on real hardware, so nobody builds from an untested revision. When the
prototype passes its tests, one release will publish a matching set of:

- **CAD:** STEP models of every part and the assembly, DXF profiles of the plates, print files with the fit coupons, and
  editable CAD;
- **build files:** the confirmed parts list and hardware counts, the build instructions with photos and measured fit notes,
  and the wiring;
- **software:** the Raspberry Pi touchscreen app and its setup, the Teensy control firmware and its configuration, and the
  phone app (Bluetooth settings, workouts and history);
- **a validation report:** what was tested, how, and the results.

Each later release names one compatible set of CAD, parts list, wiring and software versions, and marks untested changes as
untested.

## After the release

- **Metal kits:** the laser-cut and countersunk 6061 plates, the milled bearing holders, corner gussets and rack side, and
  the drum parts, made by Trent. Printed-part sets and complete machines may follow. Nothing is for sale before testing; the website
  has a kit waitlist.
- **Contributions** open with the verified release. Until then there is no tested design to contribute to. After it, useful
  contributions are build reports (revision, materials, settings, measurements and photos), CAD changes with what they
  affect, alternative batteries and motors with their test results, and documentation fixes.

## Licenses

For the verified release:

- hardware (CAD, drawings, print files): CERN-OHL-S-2.0;
- documentation and images: CC BY-SA 4.0;
- software: GPL-3.0.

Anyone will be able to build the design, change it and share their changes under these licenses. The KINETIQ and Kinetiq
Gym names and logo are not licensed: only the project's maker sells kits and machines under them. Supplier CAD and the
ODrive firmware keep their own terms.

## Supporting the project

Support is a voluntary contribution, not an order or a kit pre-sale. It goes into building, testing and improving the
prototype (parts, aluminum stock and the revisions that come out of load testing) and into build support: clear
instructions and videos, fit coupons and test jigs. The website's support section has the link once a donation provider is
set up.
