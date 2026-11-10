<h1>Plate Resort</h1>

<!-- TODO: replace with a photo or a short GIF of the carousel indexing between towers, linked to a full video -->
<table>
  <tr>
    <td align="center" width="50%"><sub>photo: assembled resort with four towers</sub></td>
    <td align="center" width="50%"><sub>video: rotating to a tower for robot pickup</sub></td>
  </tr>
</table>

**Plate Resort** is an open-source, motorized plate carousel for **self-driving labs and high-throughput experiments**. It holds **80 well plates** on four rotating towers in a small footprint. A Raspberry Pi turns the selected tower to a single fixed pickup position, so a robot arm can reach every plate without moving its own base.

### Why build this

Automated labs run out of plate storage before they run out of instruments. A typical collaborative robot arm can reach a few plates on the bench around it. Commercial plate hotels and carousels solve this, but they cost thousands of dollars, use proprietary controllers, and can be hard to integrate with in-house scheduling software.

Plate Resort takes the opposite approach:

- **Off-the-shelf parts.** It uses McMaster-Carr hardware, DIN rail, 25 mm aluminum extrusion and 3D-printed trays. The mechanical parts cost about **US$300**, plus the electronics. You need nothing machined.
- **Modular storage.** Each tower is a [plate hotel](hardware/plate-hotel/), a simple rack that can also stand on its own. You can change the height and tray count to fit your robot's reach.
- **One pickup point.** The carousel does the indexing, so the robot needs only one taught position per tray height instead of one per plate.
- **Open control.** It uses a commodity stepper driver (Pololu Tic) and a Raspberry Pi. You can drive it over a plain HTTP API or as a **SiLA 2** device, so lab orchestrators can discover it on the network.

| 1. Build the hotels | 2. Build the resort | 3. Connect it |
| --- | --- | --- |
| Print the trays and assemble four [plate hotel](hardware/plate-hotel/) towers on DIN rail, 20 trays each. The same design also works as a standalone 11-plate hotel. | Assemble the printed base, the bearing and the stepper drive, then wire up the Tic controller, encoder and home switch. See [hardware/plate-resort](hardware/plate-resort/). | Run the server on the Pi. Then move to a tower from a script with `curl` or the CLI, or add it as a SiLA 2 instrument in your orchestrator. See [software](software/). |

---

## Builds

| Build | Capacity | Drive | Files | Status |
| --- | --- | --- | --- | --- |
| [Plate Resort](hardware/plate-resort/) | 4 towers × 20 plates | NEMA 17 stepper, 100:1 gearbox, Tic T825 | BOM, wiring. CAD to come. | Rev A built. Rev B (stepper drive) at the bench stage. |
| [Plate Hotel](hardware/plate-hotel/) | 11 plates (standalone) or 20 (resort tower) | none | STEP, Fusion 360, STL/3MF, BOM, assembly guide | Rev A released |

---

## Control options

All interfaces sit on top of a single service on the Pi that owns the motor. That service handles homing, position tracking and stop, whichever interface is used.

| Interface | Use it when | Status |
| --- | --- | --- |
| **REST API + CLI** (FastAPI) | You want the simplest option: scripts, notebooks, or any language that speaks HTTP | Planned |
| **SiLA 2 server** | You want the resort to appear as a standard lab instrument to an orchestrator or scheduler | Planned |
| **Bench tool** (`software/scripts/bench_stepper.py`) | You're commissioning hardware: reading the encoder and switch and making small, bounded jogs | Available |

Planned REST commands:

| Endpoint | Description |
| --- | --- |
| `GET /status` | State (`unhomed`, `homing`, `ready`, `moving` or `fault`), current tower, and whether the carousel is homed |
| `POST /home` | Run the bounded homing sequence using the home switch |
| `POST /move` `{"station": "B"}` | Rotate tower B to the pickup position |
| `POST /stop` | Stop immediately, including in the middle of a move |

---

## Repository layout

| Folder | Contents |
| --- | --- |
| [`hardware/plate-resort/`](hardware/plate-resort/) | Carousel BOM, electronics and wiring, CAD and print files |
| [`hardware/plate-hotel/`](hardware/plate-hotel/) | Tray design, hotel configurations, and the standalone hotel build |
| [`software/`](software/) | Raspberry Pi control software |
| [`docs/`](docs/) | Design notes: position model, homing and the bench-test procedure |

## License

Hardware is released under [CERN-OHL-P-2.0](LICENSE-HARDWARE) and software under [MIT](LICENSE). Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).

Developed at the [Acceleration Consortium](https://acceleration.utoronto.ca/), University of Toronto.
