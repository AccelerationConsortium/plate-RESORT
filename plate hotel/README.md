# Plate Hotel Build Guide
This document provides the steps required to assemble the plate hotel. Please review all instructions and notes before starting the build.

## Bill of Materials
### Purchased Parts

| #   | McMaster Part # | Part Description                                       | Quantity |
|-----|-----------------|--------------------------------------------------------|----------|
| A1  | 92125A234       | M6 FH screw, 10mm L, SS                                | 22       |
| A2  | 93590A106       | M6 Coupling Nut, 18mm L, SS                            | 22       |
| A3  | 94639A569       | M6 Spacer, 1/4in L, Nylon                              | 3        |
| A4  | 92095A224       | M6 PH Screw, 10mm L, SS                                | 22       |
| A5  | 8961K96         | DIN 3 Rail, 600mm L, S                                 | 1        |
| A6  | 4844N111        | single closed gusset for 25mm rail (with fasteners)    | 3        |
| A7  | 92095A128       | M6 PH Screw, 15mm L, SS                                | 3        |
| A8  | 4633N79         | extrusion, square, 25mm, 2ft L                         | 1        |
| A9  | 94180A371       | M6 heat set insert                                     | 3        |
| A10 | 3136N534        | cap, 25mm rail                                         | 1        |
| A11 | 91458A115       | threadlocker, Loctite 243 (medium)                     | N/A      |

<small>Note: I like stainless steel screws, this is not necessary. The lengths are listed in the part description.</small>
---

### 3D Printed Parts

| #   | Filament Qty (g) | Part Name         | Part Qty |
|-----|------------------|-------------------|----------|
| B1  | 48.9             | well plate tray   | 11       |
| B2  | 50               | plate hotel base  | 1        |

<small>Note: The well plate trays are intended to print in vertical orientation. See *4xB1 well_plate_trays.3mf* file.</small>
---

## Tools Required

- **Soldering iron/heat set tool**
- **Allen keys**

---

## Assembly Notes

- **BOM References:**  
  Numbers in square brackets indicate the required quantities and the corresponding part numbers from the Bill of Materials (BOM).

- **Build Configuration:**  
  This build is designed for a 2ft long rail accommodating 10 well plate slots spaced 50mm apart. Adjust the lengths and spacing for custom configurations if needed.

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
   - Secure 22 coupling nuts [22x A2] to the DIN rail using 22 M6x10mm L pan head screws [22x A4] and threadlocker [A11].  The DIN rail has 24 slots, leave the first and last slot empty (the 
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
   - Insert the 10 well plate trays [11x B1] into the coupling nuts along the rail.
   - Each tray is secured by 2 M6x10mm L flat head screws [22x A1].
<p align="center">
  <img src="https://github.com/user-attachments/assets/c01c202f-ba65-443a-8bdf-577b822e6212" alt="image">
</p>

7. **Final Step – Cap Cover Installation:**  
   - Press the cap cover [1x A10] onto the top of the extrusion.
  
<p align="center">
  <img src="https://github.com/user-attachments/assets/fa49c195-c32d-4c48-9f26-2c2c0baec829" alt="image">
</p>
