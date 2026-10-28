# Plate Resort stepper migration and bench test

Keep the existing application on its Dynamixel backend until the new hardware passes bench checks. The initial implementation is `scripts/bench_stepper.py`: read the AS5600 and home switch, inspect the Tic, and make a bounded jog. It does not home, index hotels, or claim closed-loop positioning.

## Hardware and position model

The controller remains a Raspberry Pi. Use USB to the Tic T825 and Pi I2C bus 1 for the Adafruit AS5600. The switch must be actuated once per **carousel/output revolution**, not once per motor revolution.

The example motor, STEPPERONLINE 17HS19-1684S-MG100, is rated 1.68 A/phase with a 100:1 gearbox. Its published no-load backlash is at most 45 arcminutes (0.75 degrees), with 5 Nm maximum permissible torque and 10 Nm momentary permissible torque. Confirm the actual motor label before adopting these values. The listing specifies a single shaft: check that your actual motor exposes the rear rotor shaft for the magnet mount; do not assume the example has an accessible rear shaft.

An AS5600 on the motor measures one rotor turn, not absolute carousel position. At exactly 100:1:

- One carousel revolution requires 100 motor revolutions.
- A 90-degree carousel move requires 25 motor revolutions. All four equally spaced stations can therefore have the same raw encoder angle.
- One encoder count corresponds nominally to 360 / 4096 / 100 = 0.000879 output degrees. This is resolution, not mechanical accuracy.
- Home establishes an output reference. Continuous encoder unwrapping estimates travel thereafter. Power loss, restart, missed sampling, or unexplained movement invalidates that estimate and requires homing again.
- Rotor feedback cannot detect gearbox backlash, a loose output coupling, or downstream slip. A consistent final approach direction can improve repeatability; an output-side encoder is needed to measure actual output position directly.

For a verified 200-full-step motor with 1/8 microstepping, use 160,000 commanded microsteps/output revolution and 40,000 per 90 degrees. Confirm the actual full-step angle and actual gearbox ratio. Do not reuse the old 4096 servo counts/revolution as the motor command scale.

## Wiring for this bench script

Disconnect motor power and USB before wiring. Never connect or disconnect motor windings while powered. Use a regulated motor supply appropriate to the assembly; 12 V is a reasonable initial bench choice for this driver/motor class. The T825 supports 8.5–45 V; motor phase current is set by the driver, not inferred from supply voltage. Power the Pi separately through its normal power input.

| Connection | Destination |
| --- | --- |
| Motor supply positive | Tic VIN |
| Motor supply negative | Tic power GND |
| First motor coil pair | Tic A1 and A2 |
| Second motor coil pair | Tic B1 and B2 |
| Pi USB port | Tic USB connector, data cable |
| Pi physical pin 1, 3.3 V | Adafruit AS5600 VIN |
| Pi physical pin 6, GND | AS5600 GND |
| Pi physical pin 3, GPIO2/SDA1 | AS5600 SDA |
| Pi physical pin 5, GPIO3/SCL1 | AS5600 SCL |
| Switch COM | Pi physical pin 9, GND |
| Switch NC | Pi physical pin 11, GPIO17 |

The example motor lists Black/Green as one winding and Red/Blue as the other. Verify pairs with a meter and the actual motor datasheet; wire colors are not universal. Swapping the two wires of one coil reverses direction.

The Adafruit board pulls its I2C lines up to VIN, so use **3.3 V VIN with the Pi**. Leave OUT and programming pins unconnected for I2C operation. Keep the board's default direction configuration; verify the measured sign during jogging. Do not connect Tic 5V to the Pi 3.3V supply or its GPIO pins. USB supplies the communication ground connection; motor current returns through the motor supply wiring, never through Pi GPIO wiring.

Use a dry-contact NC switch: released = contact closed = GPIO low; pressed or disconnected wire = GPIO high. The script enables the Pi input pull-up. It stops a jog on any high reading, without debouncing that first edge. This is a host-polled home input, not a hardware emergency stop. Do not connect the same contact simultaneously to a Tic input that has a 5 V pull-up and a Pi GPIO.

Center a diametrically magnetized magnet over the AS5600 sensing axis, fixed securely to the rotating motor shaft, with the sensor fixed to the frame. Adjust spacing until magnet detected is true and weak/strong are both false across a full turn. Check again with motor energized for mounting or magnetic interference issues. Do not burn the sensor's OTP settings.

## Initial setup and commands

1. Stop the existing REST/Prefect services and close any other program controlling this motor. Clear the carousel and start unloaded if practical. Keep motor power within reach.
2. Install the official Pololu Tic software for the Pi's OS/architecture and ensure `ticcmd --list` works. Record the T825 serial number. Windows can configure the Tic first if needed.
3. In Tic Control Center select Serial / I2C / USB control. Set 1/8 microstepping, starting speed zero, conservative nonzero acceleration/deceleration, and a modest current limit (for example 500 mA for an unloaded initial check). Increase only after checking the actual motor rating, load, and temperature. The T825's approximately 1.5 A/phase continuous capability without extra cooling is below the example motor's 1.68 A rating; do not blindly enter 1.68 A or copy the old servo's 2000 mA setting.
4. Keep safe start enabled and command timeout enabled at 1000 ms. Disable automatic homing for this bench setup. Save settings, then close Tic Control Center: it sends timeout keepalives and would interfere with testing the script's watchdog behavior.
5. Enable I2C using `sudo raspi-config`. On Raspberry Pi OS install `python3-venv`, `python3-gpiozero`, and `python3-lgpio` with apt. Create a separate environment from the repository root:

```bash
python3 -m venv --system-site-packages .venv-stepper
source .venv-stepper/bin/activate
python -m pip install smbus2
python scripts/bench_stepper.py watch --seconds 30
```

Expected: magnet detected true; weak/strong false. Press/release the switch and verify `home_active_or_wire_open` changes false/true/false. Disconnecting one switch wire should also produce true. The displayed angle is **motor shaft degrees**, never output degrees. Watch mode does not command the Tic and does not stop motion initiated by another controller.

```bash
ticcmd --list
python scripts/bench_stepper.py status --serial YOUR_SERIAL
python scripts/bench_stepper.py jog --serial YOUR_SERIAL --steps 100 --allow-motion
python scripts/bench_stepper.py jog --serial YOUR_SERIAL --steps -100 --allow-motion
python scripts/bench_stepper.py stop --serial YOUR_SERIAL
```

Jog uses a temporary bench zero, caps speed at 100 microsteps/second, and accepts at most 200 microsteps either way. With 200 full steps/revolution and 1/8 mode, 100 microsteps is 22.5 motor degrees and 0.225 output degrees. Compare initial/final raw angle modulo 360; backlash may absorb output travel. The script does not change current limit, microstep mode, or acceleration settings. A five-second jog window may end before arrival if configured acceleration is very low; inspect status and encoder readings rather than interpreting exit code zero as a positioning pass.

Jog rejects an initially active switch and cannot back away from it. Move the test switch/cam clear with motor power off before retrying. During jogging, missing/weak/strong magnet, switch activation, or I2C failure aborts. Ctrl+C, completion, and exceptions attempt halt then de-energize; holding torque is released. USB failure can prevent these commands, so the independently configured Tic command timeout is required. This bench program is not a safety-rated stop or continuous encoder supervisor.

## Major overhaul plan

### 1. Separate hardware from carousel behavior

`plate_resort/core.py` currently mixes Dynamixel register access, servo PID/current configuration, motion, hotel geometry, and health reporting. Introduce a backend interface and retain the existing Dynamixel implementation during migration. Add separate Tic transport, AS5600 reader, and home-switch input modules. Keep `activate_hotel`, `move_to_angle`, `go_home`, and status as application operations.

Use explicit configuration for backend, Tic serial, full steps/revolution, microstep divisor, exact gear ratio, home direction, home offset, switch polarity, motor/encoder direction, speed in output degrees/second, acceleration, deadlines, and encoder discrepancy limits. Remove servo register units from the new backend. Preserve configurable station names and evenly spaced positions, with optional explicit calibrated angles. Do not carry forward the existing 19-degree offset without calibration.

### 2. One persistent hardware service

`interfaces/prefect/flows.py` creates a new `PlateResort` instance for each flow. Change flows and REST handlers to call one local hardware service that owns the Tic, encoder stream, homed state, and command queue. Enforce exclusive ownership across processes; an in-process lock is insufficient. Avoid automatic retries of motion after an uncertain result; use command IDs and explicit recovery.

The REST wrapper currently holds the same lock for moves and emergency stop. Provide a cancellation/stop path that can interrupt an active move rather than wait for its lock. Report disconnected, unhomed, homing, ready, moving, and fault states. Fault/restart/de-energization invalidates position until verified recovery or homing.

### 3. Implement bounded homing

First verify that the switch cam identifies one output reference and that unlimited rotation is mechanically permitted. If initially active, back off within a distance/time bound; seek the switch slowly within at most a configured output revolution plus margin; stop; back off until released; reapproach at crawl speed; debounce at rest; establish zero and apply calibrated station offset. Every phase needs timeout and travel bounds, cancellation, and sensor checks. Missing, stuck, or bouncing switches must fail explicitly.

Evaluate moving the switch to a dedicated Tic limit input for controller-local response and its built-in homing facility. That requires different wiring and software from this Pi-GPIO bench setup. A cyclic home cam is not an end-of-travel stop: permanently assigning a directional limit may block normal passage through zero, so validate this behavior before choosing that architecture. Do not enable startup homing automatically on a loaded machine.

### 4. Motion and encoder supervision

Convert output targets to microsteps, with explicit wrap/travel policy and one consistent final approach direction where mechanically possible. Continuously unwrap AS5600 rotor angles and compare encoder displacement to commanded motion with calibrated sign and tolerances. Fault on stale samples, magnetic faults, excessive following error, or inconsistent home reference. Do not repeatedly retry a stall by increasing current.

Use actual timestamps and a maximum allowed motor speed to bound unwrapping: motor travel between valid samples must stay below half a turn, with substantial margin. At the old approximate 23 output degrees/second and 100:1, the motor runs about 383 rpm; half a turn takes only about 78 ms. Ordinary Pi scheduling or a subprocess can miss that deadline. The bench script intentionally does not unwrap or certify position. Use a persistent native USB transport and a dedicated sampling loop in production; if measured worst-case delays are inadequate, move encoder tracking to a microcontroller or use an output-side sensor. Never infer missed full turns from the same step command used to detect stalls.

### 5. Acceptance and deployment

Add offline tests for unit conversion, wrap boundaries, variable station counts, encoder alias/staleness, home switch stuck/missing, disconnect during motion, concurrent commands, stop preemption, and restart requiring rehome. Test hardware home repeatability, all station approaches, full travel, cable clearance, disconnects, stall detection, and motor/driver temperature under representative load.

Measure carousel accuracy independently at the output. The existing 0.5-degree tolerance is not guaranteed by motor-side sensing and a gearbox specified at up to 0.75-degree backlash. Agree on measured positioning acceptance before enabling plate transfers. Deploy the new backend behind configuration only after these tests; keep rollback available. Report unavailable servo telemetry (such as measured winding current or internal servo temperature) as unavailable, not fabricated equivalents.

## References

- [Pololu Tic manual and setup](https://www.pololu.com/docs/0J71)
- [Pololu limit switches and homing](https://www.pololu.com/docs/0J71/4.14)
- [Adafruit AS5600 pinouts](https://learn.adafruit.com/adafruit-as5600-magnetic-angle-sensor/pinouts)
- [AS5600 manufacturer datasheet hosted by Adafruit](https://cdn-learn.adafruit.com/assets/assets/000/138/130/original/Magnetic_Rotary_Position_Sensor_AS5600_Datasheet.pdf)
- [Example motor specifications](https://www.omc-stepperonline.com/nema-17-stepper-motor-bipolar-l-48mm-w-gear-ratio-100-1-mg-series-planetary-gearbox-17hs19-1684s-mg100)
