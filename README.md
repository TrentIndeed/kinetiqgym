<p align="center"><a href="https://kinetiqgym.com"><img src="site/media/launch/hero-poster.webp" alt="The Kinetiq Gym unit on a rack upright" width="100%"></a></p>

<h1 align="center">Kinetiq Gym</h1>
<p align="center"><b>A programmable smart gym, built as open hardware.</b><br>
<a href="https://kinetiqgym.com">kinetiqgym.com</a> · <a href="https://kinetiqgym.com/build">The build</a> · <a href="https://kinetiqgym.com/build#parts">Parts &amp; cost</a> · <a href="https://kinetiqgym.com/build#software">App</a> · <a href="https://kinetiqgym.com/#support">Support</a> · <a href="docs/roadmap.md">Roadmap</a> · <a href="https://kinetiqgym.com/#join">Follow the build &amp; kit waitlist</a></p>

A direct-drive motor turns a rope drum, a geared level-wind lays the rope, and the controller sets the resistance in software.
It mounts on a rack upright. The design is built to be trained with, built, modified and programmed.

> **Status: open hardware in development.** The design is complete in CAD and the printed fit test is done. The aluminum
> prototype is being built now. **The CAD, build files and software are released after the prototype has been built and
> load-tested**, so what you download is something that has actually worked. Until then, this repository holds the website,
> the documentation and the renders.

<p align="center"><img src="site/media/launch/inside.webp" alt="Render with the covers shown see-through: the motor, the cable drum, the lead screw and the electronics" width="100%"></p>

| | |
|---|---|
| ![The drum's gear driving the level-wind](site/media/launch/gears.webp) | ![The unit on the rack](site/media/launch/rack.webp) |
| ![The touchscreen](site/media/launch/screen.webp) | ![The planned metal kit](site/media/launch/kit.webp) |

<sub>Renders of an earlier revision of the main build (Blender). The display content is illustrative.</sub>

## What it does

- **Programmable resistance:** a motor and a cable drum stand in for the weight stack, so the load is set in software.
- **Adjustable position:** it hangs on a rack upright at the height you want, and the cable exit swivels to follow the pull.
- **Training modes in software:** eccentric, chain-style and band-style resistance are designed as modes, not attachments.
- **Customizable hardware:** two builds on the same stock motor, battery or wall power, and documented interfaces for your own.
- **Local and hackable:** its own controller and a Raspberry Pi, with no account or cloud service in the loop.

## The builds

Both builds use an off-the-shelf motor, the Freerchobby MP8085 50 Kv, and the drive is direct: no belt or gear between the motor and
the drum. Nothing is welded or turned on a lathe, and every load-bearing joint is a bolt and a nut. Current parts lists and prices are
on the [build preview](https://kinetiqgym.com/build#parts).

| Build | Max rope force, held through a set | Controller | Power | Frame |
|---|---|---|---|---|
| Main build | 220 lb | ODrive Pro | 10S battery (2 x 5S LiPo) | bolted 6061 plate frame (CNC or laser cut), touchscreen, about 515 mm long |
| Budget build | 180 lb | ODESC V4.2 | 48 V wall supply in a floor box | plate and angle bought near size, cut with a hacksaw; knob and phone app |
| Wall build | 300 lb | Flipsky 75200 (VESC), Hobbywing XRotor V11130 motor | 1,000 W wall supply | in design: bolts to wall studs or concrete; parts list once the CAD is done |

Every rating is a design target held through a 20-30 s set, not yet verified: the motor's torque against current and the
controllers' currents are still to be bench-tested, and nothing is load-tested yet. The 10 lb minimum is designed to feel like
10 lb: the drums are kept small and light and the firmware cancels part of the motor's inertia.

## In this repository

| Path | What |
|---|---|
| `site/` | kinetiqgym.com: the front page, the build preview, the parts data (`site/data/`) and the reference docs (`site/docs/`) |
| `src/worker.js` | the Cloudflare Worker behind the site: the build list and the project form |
| `docs/` | build order, wiring, printing, modifying, setup and roadmap (drafts until testing) |
| `bom/BOM.md` | the bill of materials |
| `SAFETY.md` | read before building or powering anything |
| `LICENSE.md`, `LICENSES/` | the licences, and the reserved name and logo |

**Not here yet:** CAD (STEP, DXF, editable source), print files, and the Pi, Teensy and phone software. They are released
together after testing.

## Kits

Metal kits (the laser-cut and machined 6061 parts, the drum and the rack side, ready to bolt together) are planned once the
prototype passes load testing. Nothing is for sale yet. [Join the kit waitlist](https://kinetiqgym.com/#join).

## Support and contributions

The CNC machine is already in the workshop; support now goes to prototype iterations and build support
([support the project](https://kinetiqgym.com/#support)). **Contributions are closed until the verified release**: see
[CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

For the verified release: hardware under CERN-OHL-S-2.0, documentation under CC BY-SA 4.0, software under GPL-3.0. The
**KINETIQ** and **Kinetiq Gym** names and logo are not licensed: only the maker sells kits and machines under them. Details in
[LICENSE.md](LICENSE.md).

**This is an untested prototype, not a finished exercise product.** Read [SAFETY.md](SAFETY.md).
