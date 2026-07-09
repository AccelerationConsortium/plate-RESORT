#!/usr/bin/env python3
"""
PlateResort class for controlling Dynamixel-based plate storage system

Control approach: single-stage closed-loop moves executed by the servo's
internal (kHz-rate) controller in Current-based Position Control mode (5)
with a non-zero Position I Gain. The integral term removes the
load-proportional steady-state error (undershoot) that a P-only controller
exhibits under a heavy carousel; Goal Current caps output torque. The host
only issues the goal and verifies settle — it is not part of the servo loop.
"""
import time

from dynamixel_sdk import PortHandler, PacketHandler
import yaml
import os

try:
    from prefect import flow

    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False

    def flow(*args, **kwargs):
        """Dummy decorator when Prefect is not installed"""

        def decorator(func):
            return func

        if len(args) == 1 and callable(args[0]):
            # Direct decoration: @flow
            return args[0]
        else:
            # Parameterized decoration: @flow(name="...")
            return decorator


class PlateResort:
    # ---- Dynamixel X-series control table (Protocol 2.0) ----
    ADDR_OPERATING_MODE = 11
    ADDR_CURRENT_LIMIT = 38  # EEPROM, unit 2.69 mA (write with torque off)
    ADDR_TORQUE_ENABLE = 64
    ADDR_HARDWARE_ERROR = 70
    ADDR_POSITION_D_GAIN = 80
    ADDR_POSITION_I_GAIN = 82
    ADDR_POSITION_P_GAIN = 84
    ADDR_FEEDFORWARD_2ND_GAIN = 88
    ADDR_FEEDFORWARD_1ST_GAIN = 90
    ADDR_GOAL_CURRENT = 102  # torque cap in mode 5, unit 2.69 mA
    ADDR_PROFILE_ACCELERATION = 108
    ADDR_PROFILE_VELOCITY = 112
    ADDR_GOAL_POSITION = 116
    ADDR_MOVING_STATUS = 123
    ADDR_PRESENT_CURRENT = 126  # signed, unit 2.69 mA
    ADDR_PRESENT_POSITION = 132  # signed, 4096 counts/rev
    ADDR_PRESENT_VOLTAGE = 144  # unit 0.1 V
    ADDR_PRESENT_TEMPERATURE = 146

    OPERATING_MODE_POSITION = 3  # single turn, goal 0-4095
    OPERATING_MODE_EXTENDED_POSITION = 4  # multi-turn
    OPERATING_MODE_CURRENT_POSITION = 5  # multi-turn + Goal Current torque cap

    COUNTS_PER_REV = 4096
    CURRENT_UNIT_MA = 2.69
    MAX_ANGLE = 360.0
    # Highest Goal Position raw value in single-turn position mode
    MAX_POSITION = 4095
    # Current Limit register ceiling (XM430-W210: 1193 = ~3.21 A). Used as a
    # conservative clamp for all X-series models we may encounter.
    CURRENT_LIMIT_MAX_UNITS = 1193

    def __init__(self, config_file=None, **overrides):
        """
        Initialize plate resort system from YAML config

        Args:
            config_file: Path to YAML configuration file (default: auto-detect)
            **overrides: Override top-level config values (e.g., speed=30,
                offset_angle=15)
        """
        # Auto-detect config file if not specified
        if config_file is None:
            # Get the directory where this file is located
            package_dir = os.path.dirname(os.path.abspath(__file__))
            home_dir = os.path.expanduser("~")

            # Try user config first, then package defaults
            possible_paths = [
                os.path.join(
                    home_dir, "plate-resort-config", "defaults.yaml"
                ),  # User override
                os.path.join(
                    package_dir, "config", "defaults.yaml"
                ),  # Package defaults
                "config/defaults.yaml",  # Relative fallback
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    config_file = path
                    break
            else:
                # Use package defaults location (final fallback)
                config_file = os.path.join(
                    package_dir,
                    "config",
                    "defaults.yaml",
                )

        # Load configuration
        self.config = self._load_config(config_file)

        # Apply any overrides
        for key, value in overrides.items():
            if key in self.config:
                self.config[key] = value

        # Set attributes from config
        self.device = self.config["device"]
        self.baud = self.config["baudrate"]
        self.motor_id = self.config["motor_id"]
        self.hotels = self.config["hotels"]
        self.rooms = self.config["rooms_per_hotel"]
        self.speed = self.config["default_speed"]
        self.offset_angle = self.config["offset_angle"]
        self.rotation_direction = self.config["rotation_direction"]

        # Calculate hotel angles automatically, normalized into [0, 360)
        delta_angle = 360.0 / len(self.hotels) * self.rotation_direction
        self.hotel_angles = {}
        for i, hotel in enumerate(self.hotels):
            self.hotel_angles[hotel] = (
                self.offset_angle + (i * delta_angle)
            ) % 360.0

        self.current_hotel = None
        self.port = None
        self.packet_handler = None
        # Alert bit seen on the last position read (latched hardware fault)
        self._alert = False

        # Motor detection and capabilities
        self._motor_model = None
        self._supports_current_control = True
        self._max_current = int(self.CURRENT_LIMIT_MAX_UNITS * self.CURRENT_UNIT_MA)
        self._operating_mode = None

        # Call counter for testing instance persistence
        self._call_counter = 0

    def _load_config(self, config_file):
        """Load configuration from YAML file"""
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        return config["resort"]

    # -------------------- Checked packet transactions --------------------
    def _check(self, op, result, error, critical=True):
        """Validate a packet transaction result; raise or warn on failure."""
        if result != 0:
            msg = f"{op}: {self.packet_handler.getTxRxResult(result)}"
        elif error != 0:
            msg = f"{op}: {self.packet_handler.getRxPacketError(error)}"
        else:
            return True
        if critical:
            raise RuntimeError(f"Dynamixel write failed ({msg})")
        print(f"[WARN] {msg}")
        return False

    def _write1(self, addr, value, op, critical=True):
        result, error = self.packet_handler.write1ByteTxRx(
            self.port, self.motor_id, addr, int(value) & 0xFF
        )
        return self._check(op, result, error, critical)

    def _write2(self, addr, value, op, critical=True):
        result, error = self.packet_handler.write2ByteTxRx(
            self.port, self.motor_id, addr, int(value) & 0xFFFF
        )
        return self._check(op, result, error, critical)

    def _write4(self, addr, value, op, critical=True):
        result, error = self.packet_handler.write4ByteTxRx(
            self.port, self.motor_id, addr, int(value) & 0xFFFFFFFF
        )
        return self._check(op, result, error, critical)

    @staticmethod
    def _to_signed16(value):
        return value - 0x10000 if value > 0x7FFF else value

    @staticmethod
    def _to_signed32(value):
        return value - 0x100000000 if value > 0x7FFFFFFF else value

    @staticmethod
    def _wrap_deg(delta):
        """Map an angle difference onto (-180, 180]."""
        return -((180.0 - delta) % 360.0 - 180.0)

    # -------------------- Connection / configuration --------------------
    def connect(self, device=None, baudrate=None, motor_id=None):
        """Connect to Dynamixel motor and apply the control configuration.

        Optional overrides allow flows / callers to specify connection
        parameters without reconstructing the instance.

        Args:
            device (str | None): Serial device path override.
            baudrate (int | None): Baud rate override.
            motor_id (int | None): Motor ID override.
        """
        if device is not None:
            self.device = device
        if baudrate is not None:
            self.baud = baudrate
        if motor_id is not None:
            self.motor_id = motor_id

        self.port = PortHandler(self.device)
        self.packet_handler = PacketHandler(2.0)

        if not self.port.openPort():
            raise Exception(f"Failed to open port {self.device}")
        if not self.port.setBaudRate(self.baud):
            raise Exception(f"Failed to set baudrate {self.baud}")

        self._recover_hardware_error()
        self._apply_motor_config()

    # Hardware Error Status (addr 70) bit meanings, X-series Protocol 2.0
    HARDWARE_ERROR_BITS = {
        0: "input voltage",
        2: "overheating",
        3: "motor encoder",
        4: "electrical shock",
        5: "overload",
    }

    @classmethod
    def _decode_hardware_error(cls, value):
        """Names of the fault bits set in a Hardware Error Status byte."""
        return [
            name
            for bit, name in cls.HARDWARE_ERROR_BITS.items()
            if value & (1 << bit)
        ]

    def _recover_hardware_error(self):
        """Clear a latched hardware fault (e.g. overload shutdown) by reboot.

        A latched fault sets the alert bit on every status packet, so the
        checked writes in _apply_motor_config would raise before reboot()
        could ever be reached. Recover here, before any configuration.
        """
        value = self._read_hardware_error()
        if not value:
            return
        faults = self._decode_hardware_error(value) or [f"0x{value:02X}"]
        print(
            f"[RECOVER] hardware error latched ({', '.join(faults)}, "
            f"0x{value:02X}); rebooting servo"
        )
        self.packet_handler.reboot(self.port, self.motor_id)
        time.sleep(1.0)
        value = self._read_hardware_error()
        if value:
            faults = self._decode_hardware_error(value) or [f"0x{value:02X}"]
            raise RuntimeError(
                f"Hardware error persists after reboot "
                f"({', '.join(faults)}); power-cycle the motor and "
                f"check the load/wiring before retrying"
            )
        print("[RECOVER] fault cleared")

    def _apply_motor_config(self):
        """Configure operating mode, gains, limits and profile, then enable
        torque. Used by connect() and reboot(); always leaves the servo in a
        known state regardless of what mode previous code left it in."""
        cfg = self.config

        # Torque off for operating-mode / EEPROM writes
        self._write1(self.ADDR_TORQUE_ENABLE, 0, "torque disable")

        self._detect_motor_model()

        # Operating mode: current-based position control by default. The
        # position PID output becomes a desired current capped by Goal
        # Current, and goals are multi-turn so wrap-aware shortest-path
        # moves are possible.
        mode = int(cfg.get("operating_mode", self.OPERATING_MODE_CURRENT_POSITION))
        if (
            mode == self.OPERATING_MODE_CURRENT_POSITION
            and not self._supports_current_control
        ):
            print(
                f"[WARN] {self._motor_model} lacks current control; "
                "falling back to position mode (3)"
            )
            mode = self.OPERATING_MODE_POSITION
        self._write1(self.ADDR_OPERATING_MODE, mode, "operating mode")
        self._operating_mode = mode

        # Optional explicit current limit (EEPROM). Value is in mA and is
        # converted to register units (2.69 mA/LSB) and clamped to the
        # model's ceiling. Unset -> keep the factory limit.
        limit_ma = cfg.get("current_limit_register_ma")
        if limit_ma:
            units = min(
                int(round(float(limit_ma) / self.CURRENT_UNIT_MA)),
                self.CURRENT_LIMIT_MAX_UNITS,
            )
            self._write2(self.ADDR_CURRENT_LIMIT, units, "current limit")

        # Position PID. Firmware default is P=800, I=0, D=0; with I=0 a
        # constant load torque leaves a permanent position error (the servo
        # parks where P output balances friction), which is the undershoot
        # this configuration exists to remove. Firmware anti-windup is
        # built in and not user-tunable.
        self._write2(
            self.ADDR_POSITION_P_GAIN,
            int(cfg.get("position_p_gain", 800)),
            "position P gain",
        )
        self._write2(
            self.ADDR_POSITION_I_GAIN,
            int(cfg.get("position_i_gain", 300)),
            "position I gain",
        )
        self._write2(
            self.ADDR_POSITION_D_GAIN,
            int(cfg.get("position_d_gain", 0)),
            "position D gain",
        )
        self._write2(
            self.ADDR_FEEDFORWARD_1ST_GAIN,
            int(cfg.get("feedforward_1st_gain", 0)),
            "feedforward 1st gain",
            critical=False,
        )
        self._write2(
            self.ADDR_FEEDFORWARD_2ND_GAIN,
            int(cfg.get("feedforward_2nd_gain", 0)),
            "feedforward 2nd gain",
            critical=False,
        )

        # Trajectory shaping. Profile velocity/acceleration only shape the
        # goal trajectory — they do not limit torque.
        self._write4(
            self.ADDR_PROFILE_VELOCITY,
            self._validated_speed(self.speed),
            "profile velocity",
        )
        self._write4(
            self.ADDR_PROFILE_ACCELERATION,
            int(cfg.get("profile_acceleration", 10)),
            "profile acceleration",
        )

        # Torque cap for current-based position mode. Must stay at or below
        # the Current Limit register or the write is rejected.
        if mode == self.OPERATING_MODE_CURRENT_POSITION:
            goal_ma = float(cfg.get("goal_current_ma", 2000))
            units = min(
                int(round(goal_ma / self.CURRENT_UNIT_MA)),
                self.CURRENT_LIMIT_MAX_UNITS,
            )
            self._write2(self.ADDR_GOAL_CURRENT, units, "goal current")

        # Enable torque; firmware snaps Goal Position to Present Position on
        # the 0->1 transition, so enabling holds the current pose.
        self._write1(self.ADDR_TORQUE_ENABLE, 1, "torque enable")

    def _detect_motor_model(self):
        """Detect motor model and set capabilities"""
        try:
            # Read model number (address 0)
            model_number, result, error = self.packet_handler.read2ByteTxRx(
                self.port, self.motor_id, 0
            )

            if result == 0 and error == 0:
                if model_number == 1030:  # XM430-W210
                    self._motor_model = "XM430-W210"
                    self._supports_current_control = True
                    self._max_current = 3209  # mA (1193 units * 2.69)
                elif model_number == 1020:  # XM430-W350
                    self._motor_model = "XM430-W350"
                    self._supports_current_control = True
                    self._max_current = 3209  # mA
                elif model_number == 1060:  # XL430-W250
                    self._motor_model = "XL430-W250"
                    self._supports_current_control = False
                    self._max_current = 1400  # mA
                else:
                    self._motor_model = f"Unknown ({model_number})"
                    self._supports_current_control = True  # Assume full features
                print(f"Detected motor: {self._motor_model}")
            else:
                self._motor_model = "Detection Failed"
                print(f"Motor detection failed: result={result}, error={error}")

        except Exception as e:
            print(f"Motor detection error: {e}")
            self._motor_model = "Unknown"

    def get_motor_info(self):
        """Get motor model and capabilities"""
        return {
            "model": self._motor_model,
            "supports_current_control": self._supports_current_control,
            "max_current_ma": self._max_current,
            "operating_mode": self._operating_mode,
        }

    def set_current_limit_safe(self, current_limit_ma):
        """Set the Current Limit register from a value in mA.

        Converts mA to register units (2.69 mA/LSB), clamps to the model
        ceiling, and performs the required torque-off EEPROM write with the
        result checked. Torque is re-enabled afterwards.
        """
        if not self._supports_current_control:
            print(f"Current control not supported on {self._motor_model}")
            return False

        if current_limit_ma > self._max_current:
            print(
                f"Current limit {current_limit_ma}mA exceeds max for "
                f"{self._motor_model} ({self._max_current}mA)"
            )
            current_limit_ma = self._max_current

        units = min(
            int(round(current_limit_ma / self.CURRENT_UNIT_MA)),
            self.CURRENT_LIMIT_MAX_UNITS,
        )
        try:
            self._write1(self.ADDR_TORQUE_ENABLE, 0, "torque disable")
            self._write2(self.ADDR_CURRENT_LIMIT, units, "current limit")
            self._write1(self.ADDR_TORQUE_ENABLE, 1, "torque enable")
            print(f"Set current limit to {units * self.CURRENT_UNIT_MA:.0f}mA")
            return True
        except RuntimeError as e:
            print(f"Failed to set current limit: {e}")
            return False

    # -------------------- Movement --------------------
    def move(self, angle, tolerance=None, timeout=None):
        """Closed-loop verified move to an angle on the carousel circle.

        Writes the goal once and lets the servo's internal controller do
        the work; the host polls until the wrapped error stays within
        tolerance for several consecutive polls (settle), or times out.
        In multi-turn modes the goal is chosen shortest-path from the
        present position.

        Args:
            angle (float): Target angle in degrees (any value; wrapped).
            tolerance (float | None): Settle tolerance in degrees.
            timeout (float | None): Max seconds to wait for settle.

        Returns:
            dict: {success, reason, final_angle, final_error, elapsed_s,
                   peak_current_ma, pulses, hardware_error}
        """
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")

        if tolerance is None:
            tolerance = float(self.config.get("position_tolerance", 0.5))
        if timeout is None:
            timeout = float(self.config.get("movement_timeout", 20))
        settle_polls = int(self.config.get("settle_polls", 3))
        poll_interval = float(self.config.get("settle_poll_interval", 0.05))

        target = angle % 360.0

        def result(success, reason, pos, err, start, peak, hw_error=None):
            return {
                "success": success,
                "reason": reason,
                "final_angle": pos % 360.0 if pos is not None else None,
                "final_error": abs(err) if err is not None else None,
                "elapsed_s": round(time.time() - start, 3),
                "peak_current_ma": round(peak, 0) if peak is not None else None,
                # Legacy field kept for API compatibility (pulse stage gone)
                "pulses": 0,
                "hardware_error": hw_error,
            }

        start = time.time()
        try:
            present = self._read_position_deg()
        except RuntimeError:
            return result(False, "read_fail", None, None, start, None)

        if self._operating_mode in (
            self.OPERATING_MODE_EXTENDED_POSITION,
            self.OPERATING_MODE_CURRENT_POSITION,
        ):
            # Multi-turn: go shortest-path from wherever we are
            goal_deg = present + self._wrap_deg(target - (present % 360.0))
            goal_raw = int(round(goal_deg * self.COUNTS_PER_REV / self.MAX_ANGLE))
        else:
            # Single-turn position mode: absolute goal within one turn
            goal_raw = min(
                int(round(target * self.COUNTS_PER_REV / self.MAX_ANGLE)),
                self.MAX_POSITION,
            )
        self._write4(self.ADDR_GOAL_POSITION, goal_raw, "goal position")

        ok_polls = 0
        peak_ma = 0.0
        pos = present
        while True:
            try:
                pos = self._read_position_deg()
            except RuntimeError:
                return result(False, "read_fail", None, None, start, peak_ma)
            err = self._wrap_deg(target - (pos % 360.0))

            current_ma = self._read_current_ma()
            if current_ma is not None:
                peak_ma = max(peak_ma, abs(current_ma))

            if self._alert:
                hw = self._read_hardware_error()
                if hw:
                    faults = ", ".join(self._decode_hardware_error(hw)) or (
                        f"0x{hw:02X}"
                    )
                    print(f"[FAULT] hardware error mid-move: {faults}")
                    return result(
                        False, "hardware_fault", pos, err, start, peak_ma, hw
                    )
                self._alert = False

            if abs(err) <= tolerance:
                ok_polls += 1
                if ok_polls >= settle_polls:
                    self._maybe_clear_multi_turn()
                    return result(True, "reached", pos, err, start, peak_ma)
            else:
                ok_polls = 0

            if time.time() - start > timeout:
                hw = self._read_hardware_error()
                return result(False, "timeout", pos, err, start, peak_ma, hw)

            time.sleep(poll_interval)

    def goto_hotel(self, hotel, tolerance=None, timeout=None):
        """Move to a hotel's angle with verification.

        Args:
            hotel: Hotel identifier (e.g., from hotels list).
            tolerance: Position tolerance (degrees, config default if None).
            timeout: Maximum wait time in seconds (config default if None).

        Returns:
            dict: See move() for shape; plus "hotel".
        """
        if hotel not in self.hotels:
            raise ValueError(f"Hotel {hotel} not found. Available: {self.hotels}")

        target_angle = self.hotel_angles[hotel]
        print(f"Moving to hotel {hotel} at {target_angle:.1f}°")
        res = self.move(target_angle, tolerance=tolerance, timeout=timeout)
        res["hotel"] = hotel
        if res["success"]:
            self.current_hotel = hotel
            print(
                f"✓ Hotel {hotel} reached: {res['final_angle']:.2f}° "
                f"(error {res['final_error']:.2f}°, "
                f"peak {res['peak_current_ma']:.0f}mA)"
            )
        else:
            print(
                f"✗ Hotel {hotel} move failed ({res['reason']}); "
                f"position {res['final_angle']}°"
            )
        return res

    def activate_hotel(self, hotel, tolerance=None, timeout=None):
        """
        Rotate resort to activate specified hotel (verified move).

        Args:
            hotel: Hotel identifier (e.g., from hotels list)
            tolerance: Position tolerance (degrees, config default if None)
            timeout: Maximum wait time in seconds (uses config default if None)

        Returns:
            bool: True if position reached within tolerance, False if timeout
        """
        return self.goto_hotel(hotel, tolerance=tolerance, timeout=timeout)[
            "success"
        ]

    def activate_hotel_precise(self, hotel, **overrides):
        """Deprecated: use goto_hotel(). Kept for API compatibility.

        The two-stage coarse+PWM strategy has been replaced by a single
        closed-loop move (mode 5 + integral gain), which converges under
        load without host-side pulsing. Legacy pulse-stage overrides are
        ignored; tolerance/timeout are honored.
        """
        extra = {
            k: v for k, v in overrides.items() if k not in ("tolerance", "timeout")
        }
        if extra:
            print(f"[DEPRECATED] ignoring pulse-stage overrides: {sorted(extra)}")
        return self.goto_hotel(
            hotel,
            tolerance=overrides.get("tolerance"),
            timeout=overrides.get("timeout"),
        )

    def move_to_angle(self, angle, tolerance=None, timeout=None):
        """Move to specific angle in degrees (verified).

        Returns:
            bool: True if position reached within tolerance.
        """
        print(f"Moving to {angle}°")
        res = self.move(angle, tolerance=tolerance, timeout=timeout)
        if res["success"]:
            print(f"✓ Target position reached! Position: {res['final_angle']:.1f}°")
        else:
            print(
                f"✗ Move failed ({res['reason']}). "
                f"Current: {res['final_angle']}°"
            )
        return res["success"]

    def move_to_angle_precise(self, angle, **overrides):
        """Deprecated: use move(). Kept for API compatibility."""
        extra = {
            k: v for k, v in overrides.items() if k not in ("tolerance", "timeout")
        }
        if extra:
            print(f"[DEPRECATED] ignoring pulse-stage overrides: {sorted(extra)}")
        return self.move(
            angle,
            tolerance=overrides.get("tolerance"),
            timeout=overrides.get("timeout"),
        )

    def go_home(self):
        """Go to home position (0 degrees)"""
        print("Moving to home position (0°)")
        res = self.move(0.0)
        if res["success"]:
            self.current_hotel = None
            print(f"✓ Home position reached! Position: {res['final_angle']:.1f}°")
            return True
        print(
            f"✗ Timeout waiting for home position. Current: {res['final_angle']}°"
        )
        return False

    def _maybe_clear_multi_turn(self):
        """Housekeeping: keep the multi-turn counter bounded.

        Repeated same-direction indexing accumulates whole revolutions in
        Present Position. Once it exceeds the configured number of turns,
        reset the counter (servo must be stopped; torque toggled around the
        Clear instruction, which re-snaps the goal to the present pose).
        """
        if self._operating_mode not in (
            self.OPERATING_MODE_EXTENDED_POSITION,
            self.OPERATING_MODE_CURRENT_POSITION,
        ):
            return
        clear_revs = float(self.config.get("multi_turn_clear_revs", 2.0))
        try:
            if abs(self._read_position_deg()) < clear_revs * 360.0:
                return
            self._write1(
                self.ADDR_TORQUE_ENABLE, 0, "torque off (clear)", critical=False
            )
            result, error = self.packet_handler.clearMultiTurn(
                self.port, self.motor_id
            )
            self._check("clear multi-turn", result, error, critical=False)
            self._write1(
                self.ADDR_TORQUE_ENABLE, 1, "torque on (clear)", critical=False
            )
        except RuntimeError as e:
            print(f"[WARN] multi-turn housekeeping skipped: {e}")

    def emergency_stop(self):
        """Emergency stop - disable torque immediately"""
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")

        print("🛑 EMERGENCY STOP - Disabling torque")
        ok = self._write1(
            self.ADDR_TORQUE_ENABLE, 0, "emergency torque disable", critical=False
        )
        if not ok:  # one retry, then report honestly
            ok = self._write1(
                self.ADDR_TORQUE_ENABLE, 0, "emergency torque disable", critical=False
            )
        return ok

    def reboot(self, wait: float = 0.8, reapply: bool = True):
        """Soft reboot the Dynamixel and optionally reapply settings.

        Args:
            wait (float): Seconds to wait after issuing reboot before writes.
            reapply (bool): When True, reapply the full control configuration
                (mode, gains, limits, profile) as on connect.

        Returns:
            dict: {status: 'ok', reapply: bool, wait: float}
        """
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")

        # Disable torque for safety before reboot
        self._write1(self.ADDR_TORQUE_ENABLE, 0, "torque disable", critical=False)
        print("[REBOOT] issuing reboot")
        self.packet_handler.reboot(self.port, self.motor_id)
        time.sleep(wait)
        if reapply:
            self._apply_motor_config()
        print("[REBOOT] complete")
        return {"status": "ok", "reapply": reapply, "wait": wait}

    # -------------------- Telemetry --------------------
    def get_active_hotel(self):
        """
        Get the currently active hotel based on motor position

        Returns:
            str: Hotel identifier or None if position doesn't match any hotel
        """
        current_pos = self.get_current_position()

        # Find closest hotel within tolerance (wrap-aware)
        min_error = float("inf")
        active_hotel = None

        for hotel, angle in self.hotel_angles.items():
            error = abs(self._wrap_deg(angle - current_pos))
            if error < min_error:
                min_error = error
                active_hotel = hotel

        # Return hotel if within reasonable tolerance (5 degrees)
        if min_error <= 5.0:
            return active_hotel
        else:
            return None

    def get_motor_health(self):
        """
        Get comprehensive motor health status

        Returns:
            dict: Motor health data (temperature, current, voltage, errors)
        """
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")

        health = {"warnings": []}

        # Temperature (1 byte)
        temp, result, error = self.packet_handler.read1ByteTxRx(
            self.port, self.motor_id, self.ADDR_PRESENT_TEMPERATURE
        )
        health["temperature"] = temp if result == 0 else None

        # Present current (2 bytes, signed, 2.69 mA/LSB)
        health["current"] = self._read_current_ma()

        # Voltage (2 bytes, 0.1 V/LSB)
        voltage, result, error = self.packet_handler.read2ByteTxRx(
            self.port, self.motor_id, self.ADDR_PRESENT_VOLTAGE
        )
        health["voltage"] = voltage * 0.1 if result == 0 else None

        # Hardware error status
        hw_error = self._read_hardware_error()
        health["hardware_error"] = hw_error

        # Position feedback with graceful fallback
        try:
            health["position"] = self.get_current_position()
        except Exception as e:  # noqa: BLE001
            health["position"] = None
            health["warnings"].append(f"Position read failed: {e}".rstrip())

        # Health warnings
        if (
            health["temperature"]
            and health["temperature"] > self.config["temperature_limit"]
        ):
            health["warnings"].append(f"High temperature: {health['temperature']}°C")
        if health["current"] and abs(health["current"]) > self.config["current_limit"]:
            health["warnings"].append(f"High current: {health['current']:.0f}mA")
        if health["voltage"]:
            if health["voltage"] < self.config["voltage_min"]:
                health["warnings"].append(f"Low voltage: {health['voltage']:.1f}V")
            elif health["voltage"] > self.config["voltage_max"]:
                health["warnings"].append(f"High voltage: {health['voltage']:.1f}V")
        if health["hardware_error"] and health["hardware_error"] > 0:
            health["warnings"].append(
                f"Hardware error: 0x{health['hardware_error']:02X}"
            )

        return health

    def print_motor_health(self):
        """Print formatted motor health status"""
        health = self.get_motor_health()

        print("\n=== Motor Health Status ===")
        print(
            f"Temperature: {health['temperature']}°C"
            if health["temperature"]
            else "Temperature: N/A"
        )
        print(
            f"Current: {health['current']:.0f}mA"
            if health["current"]
            else "Current: N/A"
        )
        print(
            f"Voltage: {health['voltage']:.1f}V"
            if health["voltage"]
            else "Voltage: N/A"
        )
        print(f"Position: {health['position']:.2f}°")
        print(
            f"Hardware Error: 0x{health['hardware_error']:02X}"
            if health["hardware_error"]
            else "Hardware Error: None"
        )

        if health["warnings"]:
            print("\n⚠️  WARNINGS:")
            for warning in health["warnings"]:
                print(f"  • {warning}")
        else:
            print("✓ All parameters within normal range")

    def _validated_speed(self, speed):
        """Validate a Profile Velocity value against config bounds.

        Profile Velocity 0 means "no velocity profile" on Dynamixel — the
        servo would move at whatever speed the torque cap and supply
        voltage allow — so 0 is rejected, not treated as slow/stopped.
        """
        speed = int(speed)
        max_speed = int(self.config.get("max_speed", 100))
        if speed < 1:
            raise ValueError(
                "speed must be >= 1 (Profile Velocity 0 disables the "
                "velocity profile: unlimited-speed move)"
            )
        if speed > max_speed:
            raise ValueError(
                f"speed {speed} exceeds max_speed cap ({max_speed}); "
                "raise max_speed in config if intentional"
            )
        return speed

    def set_speed(self, speed):
        """Set motor speed (Profile Velocity, 0.229 rpm per unit).

        Raises:
            ValueError: If speed < 1 or above the max_speed config cap.
        """
        speed = self._validated_speed(speed)
        self.speed = speed
        if self.port:
            self._write4(
                self.ADDR_PROFILE_VELOCITY, speed, "profile velocity", critical=False
            )

    def _read_position_deg(self):
        """Present position in degrees (signed; multi-turn aware).

        A latched hardware fault sets the alert bit in the error byte of
        every status packet without invalidating the returned value; it is
        recorded in self._alert so move() can abort with the decoded fault
        instead of misreporting a read failure.
        """
        pos, result, error = self.packet_handler.read4ByteTxRx(
            self.port, self.motor_id, self.ADDR_PRESENT_POSITION
        )
        if result != 0:
            raise RuntimeError("Failed to read position")
        self._alert = bool(error)
        return self._to_signed32(pos) * self.MAX_ANGLE / self.COUNTS_PER_REV

    def _read_current_ma(self):
        """Present current in mA (signed), or None if the read fails."""
        value, result, _error = self.packet_handler.read2ByteTxRx(
            self.port, self.motor_id, self.ADDR_PRESENT_CURRENT
        )
        if result == 0:
            return self._to_signed16(value) * self.CURRENT_UNIT_MA
        return None

    def _read_hardware_error(self):
        """Hardware Error Status byte, or None if the read fails.

        Only the comm result is checked: when a fault is latched the servo
        sets the alert bit in the error byte of every status packet, which
        is precisely the condition this read exists to diagnose.
        """
        value, result, _error = self.packet_handler.read1ByteTxRx(
            self.port, self.motor_id, self.ADDR_HARDWARE_ERROR
        )
        return value if result == 0 else None

    def get_current_position(self):
        """Get current motor position in degrees, normalized to [0, 360)"""
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")
        return self._read_position_deg() % 360.0

    def is_connected(self):
        return self.port is not None and getattr(self.port, "is_open", False)

    def disconnect(self):
        """Disconnect from motor"""
        if self.port:
            self._write1(self.ADDR_TORQUE_ENABLE, 0, "torque disable", critical=False)
            self.port.closePort()
            self.port = None

    # -------------------- Runtime tuning helpers --------------------
    CONTROL_KEYS = (
        "operating_mode",
        "position_p_gain",
        "position_i_gain",
        "position_d_gain",
        "feedforward_1st_gain",
        "feedforward_2nd_gain",
        "goal_current_ma",
        "default_speed",
        "max_speed",
        "profile_acceleration",
        "position_tolerance",
        "movement_timeout",
        "settle_polls",
        "settle_poll_interval",
        "multi_turn_clear_revs",
    )

    def show_control_params(self):
        """Print current control parameters (resolved)."""
        print("\n[Control Params]")
        resolved = {}
        for k in self.CONTROL_KEYS:
            resolved[k] = self.config.get(k)
            print(f"  {k}: {resolved[k]}")
        return resolved

    def tune_control(self, **updates):
        """Runtime update of control config keys, applied to the servo.

        Example:
            resort.tune_control(position_i_gain=500, goal_current_ma=2200)
        These persist only for this process (do not write back to file).
        """
        for k, v in updates.items():
            self.config[k] = v
        if "default_speed" in updates:
            self.speed = updates["default_speed"]
        if updates:
            print("[TUNE] Updated keys:")
            for k, v in updates.items():
                print(f"  {k} -> {v}")
            if self.port is not None:
                self._apply_motor_config()
        return self.show_control_params()

    # Deprecated aliases (pulse-stage era)
    def show_precise_params(self):
        """Deprecated: use show_control_params()."""
        return self.show_control_params()

    def tune_precise(self, **updates):
        """Deprecated: use tune_control()."""
        return self.tune_control(**updates)
