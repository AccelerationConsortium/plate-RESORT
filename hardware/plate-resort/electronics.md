# Plate Resort electronics

The carousel is driven by a geared NEMA 17 stepper through a Pololu Tic T825, controlled over USB by a Raspberry Pi. An AS5600 magnetic encoder on the motor shaft and a normally-closed home switch on the carousel provide feedback.

> Status: bench stage. Parts, wiring, and settings below match the bench test in [docs/stepper-design-notes.md](../../docs/stepper-design-notes.md). Confirm motor ratings on your actual part before powering up.

## Parts

| Ref | Part | Notes |
| --- | --- | --- |
| E1 | Raspberry Pi (4/5 or Zero 2 W) | Runs the control server. Powered from its own supply. |
| E2 | Pololu Tic T825 stepper controller | USB to the Pi. Serial/I2C/USB control mode. |
| E3 | STEPPERONLINE 17HS19-1684S-MG100 (NEMA 17, 100:1 planetary) | Example motor. 1.68 A/phase; T825 is ~1.5 A/phase continuous without cooling. |
| E4 | Adafruit AS5600 breakout | I2C bus 1, powered from Pi 3.3 V. Needs a diametrically magnetized magnet on the motor shaft. |
| E5 | Dry-contact NC microswitch + cam | Actuated once per carousel revolution. |
| E6 | 12 V regulated supply | Motor power to Tic VIN (T825 accepts 8.5–45 V). |

## Wiring

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

