# Software

Control software for the Plate Resort. It runs on the Raspberry Pi that is connected to the Tic stepper controller.

> **Status:** rewrite in progress. The earlier Dynamixel/Prefect software has been removed. So far this folder has only the hardware bench tool.

## Available now

- `scripts/bench_stepper.py`: reads the encoder and home switch, checks Tic status, and makes a bounded jog. See [docs/stepper-design-notes.md](../docs/stepper-design-notes.md).
- `tests/`: offline unit tests. Run them with `python -m unittest discover -s tests`.

## Planned

```
software/
├── pyproject.toml         # package `plate-resort`; extras [rest], [sila]
└── src/plate_resort/
    ├── drivers/           # tic.py (USB serial), as5600.py, home_switch.py
    ├── carousel.py        # stations, unit conversion, homing, moves, encoder supervision
    ├── config.py
    ├── service.py         # sole owner of the hardware; state machine; stop path that can interrupt a move
    ├── rest/              # FastAPI server + small CLI client
    ├── sila/              # SiLA 2 server (feature definitions + implementation)
    └── cli.py             # plate-resort serve --rest --sila | bench ...
```

The REST and SiLA servers are both thin layers over one `CarouselService`. Either one, or both, can run in the same process.
