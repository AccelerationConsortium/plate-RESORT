# Plate Hotel Build Guide
This document provides the steps required to assemble the plate hotel. Please review all instructions and notes before starting the build.

## Assembly Notes

- **BOM References:**  
  Numbers in square brackets indicate the required quantities and the corresponding part numbers from the Bill of Materials (BOM).

- **Build Configuration:**  
  This build is designed for a 2ft long rail accommodating 10 well plate slots spaced 50mm apart. Adjust the lengths and spacing for custom configurations if needed.

- **Base Plate:**  
  The base plate is intended to be screwed into a breadboard with M6 threads and 25mm spacing.

---

## Purchased Parts

| #   | McMaster Part # | Part Name                                              | Quantity |
|-----|-----------------|--------------------------------------------------------|----------|
| A1  | 92125A234       | M6 FH screw, 10mm L, SS                                | 20       |
| A2  | 93590A106       | M6 Coupling Nut, 18mm L, SS                            | 20       |
| A3  | 94639A569       | M6 Spacer, 1/4in L, Nylon                              | 3        |
| A4  | 92095A224       | M6 PH Screw, 10mm L, SS                                | 20       |
| A5  | 8961K96         | DIN 3 Rail, 600mm L, S                                 | 1        |
| A6  | 4844N111        | single closed gusset for 25mm rail (with fasteners)    | 3        |
| A7  | 92095A128       | M6 PH Screw, 15mm L, SS                                | 3        |
| A8  | 4633N79         | extrusion, square, 25mm, 2ft L                         | 1        |
| A9  | 92125A111       | M6 FH screw, 15mm L, SS                                | 1        |
| A10 | 94180A371       | M6 heat set insert                                     | 3        |
| A11 | 3136N534        | cap, 25mm rail                                         | 1        |
| A12 | 91458A115       | threadlocker, Loctite 243 (medium)                     | N/A      |

---

## 3D Printed Parts

| #   | Filament Qty (g) | Part Name         | Part Qty |
|-----|------------------|-------------------|----------|
| B1  | 48.9             | well plate tray   | 10       |
| B2  | 50               | plate hotel base  | 1        |

**Note**: The well plate trays are intended to print in vertical orientation.  See *4xB1 well_plate_trays.3mf* file.
---

## Tools Required

- **M6 tap** (optional for Step 2)
- **Soldering iron/heat set tool**
- **Allen keys**

---

## Assembly Steps

1. **Install Heat Set Inserts:**  
   - Insert 3 heat set inserts [3x A10] into the plate hotel base [1x B2].

2. **Prepare the Extrusion (Optional):**  
   - Tap one end of the extrusion with an M6 tap. This end will serve as the bottom of the plate hotel.

3. **Attach Coupling Nuts to the DIN Rail:**  
   - Secure 20 coupling nuts [20x A2] to the DIN rail using 20 M6x10mm L pan head screws [20x A4] and threadlocker [A12].  
   - **Note:** Ensure the screws and nuts are aligned on the right side of the DIN rail slot (the image provided shows the right side as the bottom of the rail).

4. **Prepare Components for Attaching the DIN Rail:**  
   Gather the following parts:
   - 3 M6 15mm L screws [3x A7]
   - 3 M6 spacers [3x A3]
   - 3 track nuts (from the gusset associated with part A6; use 3 out of the 6 provided)

5. **Assemble the DIN Rail to the Extrusion:**  
   - Fasten the DIN rail to the square extrusion rail by placing the screws, spacers, and track nuts at approximately the top, middle, and bottom positions.  
   - **Tip:** Align one edge of the rail with the extrusion; this aligned edge will serve as the bottom that contacts the base.

6. **Attach the Rail/Extrusion Assembly to the Hotel Base:**  
   - Use gussets [3x A6] (which include screws and nuts) to secure the assembly.
     - Fasten a nut along three of the extrusion tracks to attach the gusset to the extrusion.
     - Thread the remaining screw into the heat set insert to secure the gusset to the base.
   - **Ensure:** The edge of the DIN rail touches the base after installation.

7. **Secure the DIN Rail (Optional):**  
   - From the back of the hotel base, screw in the M5x15mm L flat head screw [1x A9] into the DIN rail.

8. **Install the Well Plate Trays:**  
   - Insert the 10 well plate trays [10x B1] into the coupling nuts along the rail.
   - Each tray is secured by 2 M6x10mm L flat head screws [20x A1].

9. **Final Step – Cap Cover Installation:**  
   - Press the cap cover [1x A11] onto the top of the extrusion.

---