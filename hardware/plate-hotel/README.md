# Plate Hotel

A plate hotel is a vertical rack of well-plate trays on a DIN rail and 25 mm extrusion. It is the storage unit that the [Plate Resort](../plate-resort/) carousel rotates. It can also be built as a standalone, fixed hotel that bolts to an M6 optical breadboard.

## Configurations

Trays clip onto pairs of M6 coupling nuts on the DIN rail. The rail slots are 25 mm apart and each tray uses two slots, so trays are spaced 50 mm apart. To change capacity, change the rail and extrusion length.

| Configuration | DIN rail | Extrusion | Trays | Used in |
| --- | --- | --- | --- | --- |
| Standalone hotel (documented below) | 600 mm (8961K96) | 25 mm square, 2 ft (4633N79) | 11 | Fixed hotel on a breadboard |
| Resort tower | 1 m (8961K15) | see resort build | 20 | [Plate Resort](../plate-resort/), 4 towers |
| Custom | any length | rail length | (rail slots − 2) / 2, leaving the end slots free | |

For each tray you need 2 coupling nuts (A2), 2 pan-head screws (A4) and 2 flat-head screws (A1).

## Files

| Folder | Contents |
| --- | --- |
| [`cad/`](cad/) | STEP files for the tray, the base and the full assembly, plus the Fusion 360 (`.f3z`) assembly |
| [`print/`](print/) | STL files for the tray (B1) and base (B2). `B1-well-plate-tray-x4.3mf` is a plate of four trays oriented vertically for printing. |
| [`bom.csv`](bom.csv) | Bill of materials with McMaster-Carr part numbers and unit costs |

## Bill of materials (standalone hotel)

The full list, with costs, is in [`bom.csv`](bom.csv).

| # | McMaster # | Part | Qty |
|---|---|---|---|
| A1 | 92125A234 | M6 FH screw, 10 mm, SS | 22 |
| A2 | 93590A106 | M6 coupling nut, 18 mm, SS | 22 |
| A3 | 94639A569 | M6 spacer, 1/4 in, nylon | 3 |
| A4 | 92095A224 | M6 PH screw, 10 mm, SS | 22 |
| A5 | 8961K96 | DIN 3 rail, 600 mm | 1 |
| A6 | 4844N123 | Single closed gusset for 25 mm rail (with fasteners) | 3 |
| A7 | 92095A128 | M6 PH screw, 15 mm, SS | 3 |
| A8 | 4633N79 | Extrusion, square, 25 mm, 2 ft | 1 |
| A9 | 94180A371 | M6 heat-set insert | 3 |
| A10 | 3136N534 | Cap, 25 mm rail | 1 |
| A11 | 91458A115 | Threadlocker, Loctite 243 (medium) | — |
| B1 | printed, 48.9 g | Well plate tray | 11 |
| B2 | printed, 50 g | Plate hotel base | 1 |

<sub>Stainless steel screws are optional. Print the trays vertically.</sub>

## Tools Required

- **Soldering iron/heat set tool**
- **Allen keys**

---

## Assembly Notes

- **BOM References:**  
  Numbers in square brackets indicate the required quantities and the corresponding part numbers from the Bill of Materials (BOM).

- **Build Configuration:**  
  This build is designed for a 2ft long rail accommodating 11 well plate slots spaced 50mm apart. Adjust the lengths, spacing, and quantities for custom configurations if needed.

- **Base Plate:**  
  The base plate is intended to be screwed into a breadboard with M6 threads and 25mm spacing.

---

## Assembly Instructions

1. **Install Heat Set Inserts:**  
   - Insert 3 heat set inserts [3x A9] into the plate hotel base [1x B2].
<p align="center">
  <img src="https://github.com/user-attachments/assets/3fc72c26-c34f-4ca5-bfcd-d9cfe42e25e2" alt="image">
</p>

2. **Attach Coupling Nuts to the DIN Rail:**  
   - Secure 22 coupling nuts [22x A2] to the DIN rail using 22 M6x10mm L pan head screws [22x A4] and threadlocker [A11].  The DIN rail has 24 slots, leave the first and last slot empty.
   - **Note:** Ensure the screws and nuts are aligned on the right side of the DIN rail slot (the image provided shows the right side as the bottom of the rail).
<p align="center">
  <img src="https://github.com/user-attachments/assets/da46f050-f562-44f0-b350-769fb6c2611d" alt="image">
</p>

3. **Prepare Components for Attaching the DIN Rail:**  
   Gather the following parts:
   - 3 M6 15mm L screws [3x A7]
   - 3 M6 spacers [3x A3]
   - 3 track nuts (from the gusset associated with part A6; use 3 out of the 6 provided)

4. **Assemble the DIN Rail to the Extrusion:**  
   - Fasten the DIN rail to the square extrusion rail by placing the screws, spacers, and track nuts at approximately the top, middle, and bottom positions.  
   - **Tip:** Align one edge of the rail with the extrusion; this aligned edge will serve as the bottom that contacts the base.  This can be done this after step 5 once the base is assembled.

<p align="center">
  <img src="https://github.com/user-attachments/assets/87c2e969-3b11-4472-a61e-a1f92b465d69" alt="image">
</p>
<p align="center">
  <img src="https://github.com/user-attachments/assets/6a47f600-ee72-447c-a47f-fd71f04df5e5" alt="image">
</p>

5. **Attach the Rail/Extrusion Assembly to the Hotel Base:**  
   - Use gussets [3x A6] (screws and nuts included with gusset) to secure the assembly.
     - Fasten a nut along three of the extrusion tracks to attach the gusset to the extrusion.
     - Thread the remaining screw into the heat set insert [A9] to secure the gusset to the base.
   - **Ensure:** The edge of the DIN rail touches the base after installation.

<p align="center">
  <img src="https://github.com/user-attachments/assets/f062ce9c-93af-4056-a731-3d6fe0445be6" alt="image">
</p>

6. **Install the Well Plate Trays:**  
   - Insert the 11 well plate trays [11x B1] into the coupling nuts along the rail.
   - Each tray is secured by 2 M6x10mm L flat head screws [22x A1].
<p align="center">
  <img src="https://github.com/user-attachments/assets/c01c202f-ba65-443a-8bdf-577b822e6212" alt="image">
</p>

7. **Final Step – Cap Cover Installation:**  
   - Press the cap cover [1x A10] onto the top of the extrusion.
  
<p align="center">
  <img src="https://github.com/user-attachments/assets/fa49c195-c32d-4c48-9f26-2c2c0baec829" alt="image">
</p>
