# Project roadmap

KINETIQ is a prototype design. The repository contains an earlier development snapshot. Updated CAD, confirmed build instructions and parts list, app code and control programs are upcoming.

| Area | Available now | Next milestone |
|---|---|---|
| Hardware | Printed and CNC assemblies; FreeCAD feature histories, STEP, DXF and STL | Reconcile every export and manifest against one revision; prototype fit and load testing |
| Build guide | Draft references and an illustrated CNC animation preview on the website | Confirmed assembly steps, build photos and measured fit notes |
| Adaptation | Motor interface guide and battery-envelope sketch | Fully constrained sketch-based parts and a self-contained CAD generation pipeline |
| Raspberry Pi | Screen concept in the product film | Touchscreen application, reproducible image and installation guide |
| Teensy | Proposed control architecture and setup reference | Firmware, configuration schema, limits and bench test procedure |
| Companion | Phone app concept screens in the film and website | Bluetooth protocol, connection flow, mode settings and workout history |

## How releases should work

Keep one repository for the hardware, website, documentation and control software while the project is small. Each future release should identify a single compatible set of CAD, BOM, wiring and software versions. Do not mix a new part with an older assembly without recording the change.

For a hardware release, publish the editable FreeCAD sources and neutral STEP alongside STL/DXF exports, an itemized BOM, a changelog and a validation report. Label untested changes explicitly. Large production animations and build recordings belong in release assets or external media storage rather than repeated Git history.

For the Pi and Teensy, add actual source, dependency versions, build commands, configuration defaults and test instructions before advertising a software download. The current film is a UI concept, not evidence of working controls.

## Useful contributions

- Build reports: revision, manufacturing method, material, measured fit, photos and unresolved issues.
- CAD changes: source file, exported geometry, affected hardware and assembly steps.
- Alternative batteries or motors: interface dimensions, electrical compatibility assumptions and test results.
- Sourcing: exact part, region, quantity, price, currency, date and supplier link.
- Documentation: one reproducible step or correction with the affected revision.

See [CONTRIBUTING.md](../CONTRIBUTING.md) and [the license map](../LICENSE.md). Supplier CAD and controller firmware retain their own terms.

## Prototype funding

Project support is intended for a CNC machine, fabrication and prototype test equipment. The website support section explains these goals. A payment link appears only when the owner has configured the chosen donation provider; contributions are not orders for a finished product. No funding total or equipment price is implied by the concept film.
