# Plate Resort hardware

The Plate Resort is a motorized turntable that carries four [plate hotel](../plate-hotel/) towers of 20 trays each, so it holds 80 well plates. A Raspberry Pi drives a geared stepper motor that rotates the selected tower to a fixed pickup position for a robot arm.

> **Status:** Rev B is in progress. Rev A used a Dynamixel servo, and the drive is being changed to a stepper with a Tic T825 controller. The mechanical parts carry over from Rev A. The motor mount and hub need redesigning (E7 in the BOM).

## Contents

| File | Contents |
| --- | --- |
| [`bom.csv`](bom.csv) | Bill of materials: purchased parts (`A`), electronics (`E`) and printed parts (`B`) |
| [`electronics.md`](electronics.md) | Electronics parts, wiring, and the encoder/home-switch setup |
| [`cad/`](cad/) | STEP and Fusion 360 source files. **TODO: add.** |
| [`print/`](print/) | STL/3MF files for the housing, rail adapters, regrip plates and top bearing. **TODO: add.** |

## Build overview

1. Print the parts. The three bottom-housing parts are printed at 100% infill. See `bom.csv` for weights and layer heights.
2. Build four hotel towers on 1 m DIN rails, with 20 trays each. Follow the [plate hotel guide](../plate-hotel/), using the resort-tower configuration.
3. Assemble the bottom housing, the bearing and the motor mount. **TODO: write the step-by-step guide and add photos.**
4. Wire the electronics as described in [`electronics.md`](electronics.md).
5. Run the bench checks in [`docs/stepper-design-notes.md`](../../docs/stepper-design-notes.md) before attaching the towers.
