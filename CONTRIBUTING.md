# Contributing

## Hardware

- Commit CAD sources (STEP, and the native `.f3z` where you have it) together with the printable exports (STL/3MF) generated from them.
- Name files `<BOM ref>-<part-name>-Rev<X>.<ext>`, for example `B1-well-plate-tray-RevA.stl`.
- Keep `bom.csv` in sync with the CAD. Mark unknown values `TODO` rather than guessing.
- Put images in an `images/` folder next to the README that uses them.

## Software

- Code in `software/` must pass `python -m unittest discover -s software/tests` with no hardware attached.
- Only code in `drivers/` may touch hardware. Everything else must be testable against fakes.
- Never commit virtual environments, API keys or `secrets.*` files.
