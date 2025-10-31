#!/usr/bin/env python3
"""
PlateResort class for controlling Dynamixel-based plate storage system
"""
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
                # Legacy file resort_config.yaml removed from search
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

        # Calculate hotel angles automatically
        delta_angle = 360.0 / len(self.hotels) * self.rotation_direction
        self.hotel_angles = {}
        for i, hotel in enumerate(self.hotels):
            self.hotel_angles[hotel] = self.offset_angle + (i * delta_angle)

        self.current_hotel = None
        self.port = None
        self.packet_handler = None

        # Call counter for testing instance persistence
        self._call_counter = 0

        # Dynamixel constants
        self.ADDR_TORQUE_ENABLE = 64
        self.ADDR_GOAL_POSITION = 116
        self.ADDR_PRESENT_POSITION = 132
        self.ADDR_GOAL_TORQUE = 102
        # Corrected address mapping (XM430 Protocol 2.0)
        self.ADDR_VELOCITY_LIMIT = 32  # currently unused (velocity ceiling)
        self.ADDR_CURRENT_LIMIT = 38   # actual current/torque limit register
        self.ADDR_PRESENT_TEMPERATURE = 146
        self.ADDR_PRESENT_CURRENT = 144
        self.ADDR_PRESENT_VOLTAGE = 144
        self.ADDR_HARDWARE_ERROR = 70
        self.MAX_POSITION = 4095
        self.MAX_ANGLE = 360.0

    def _load_config(self, config_file):
        """Load configuration from YAML file"""
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        return config["resort"]

    def connect(self, device=None, baudrate=None, motor_id=None):
        """Connect to Dynamixel motor.

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

        # Set position control mode and enable torque
        self.packet_handler.write1ByteTxRx(
            self.port, self.motor_id, self.ADDR_TORQUE_ENABLE, 0
        )
        self.packet_handler.write1ByteTxRx(
            self.port, self.motor_id, 11, 3
        )  # Position control mode

        # Set torque settings
        # Apply current limit if provided (guard absent key)
        if "current_limit" in self.config:
            self.packet_handler.write2ByteTxRx(
                self.port,
                self.motor_id,
                self.ADDR_CURRENT_LIMIT,
                self.config["current_limit"],
            )
    # Goal current only meaningful in current / current-based
    # position modes (0 or 5). Retained for optional future use;
    # harmless in mode 3.
        if "goal_torque" in self.config:
            self.packet_handler.write2ByteTxRx(
                self.port,
                self.motor_id,
                self.ADDR_GOAL_TORQUE,
                self.config["goal_torque"],
            )

        self.packet_handler.write1ByteTxRx(
            self.port, self.motor_id, self.ADDR_TORQUE_ENABLE, 1
        )

        # Set profile velocity (speed)
        self.packet_handler.write4ByteTxRx(
            self.port,
            self.motor_id,
            112,
            self.speed,
        )
        # Optional acceleration application
        accel = self.config.get("profile_acceleration", 0)
        if accel and accel > 0:
            self.packet_handler.write4ByteTxRx(
                self.port,
                self.motor_id,
                108,
                int(accel),
            )

    def activate_hotel(self, hotel, tolerance=None, timeout=None):
        """
        Rotate resort to activate specified hotel

        Args:
            hotel: Hotel identifier (e.g., from hotels list)
            tolerance: Position tolerance (degrees, config default if None)
            timeout: Maximum wait time in seconds (uses config default if None)

        Returns:
            bool: True if position reached within tolerance, False if timeout
        """
        if tolerance is None:
            tolerance = self.config["position_tolerance"]
        if timeout is None:
            timeout = self.config["movement_timeout"]
        if hotel not in self.hotels:
            raise ValueError(
                f"Hotel {hotel} not found. Available: {self.hotels}"
            )

        if self.port is None:
            raise Exception("Not connected. Call connect() first.")

        target_angle = self.hotel_angles[hotel]
        goal_pos = int(target_angle * self.MAX_POSITION / self.MAX_ANGLE)

        # Issue command and optimistically mark hotel active without
        # verifying position (legacy blind behavior).
        self.packet_handler.write4ByteTxRx(
            self.port,
            self.motor_id,
            self.ADDR_GOAL_POSITION,
            goal_pos,
        )
        print(
            f"(Blind) Moving to hotel {hotel} at {target_angle}° "
            f"(position {goal_pos})"
        )
        self.current_hotel = hotel
        return True

    def activate_hotel_precise(self, hotel, **overrides):
        """Precise activation using two-stage strategy (coarse -> PWM pulses).

        Args:
            hotel (str): Hotel identifier.
            **overrides: Optional per-call overrides for configuration keys.

        Returns:
            dict: Result details {success: bool, reason: str, pulses: int,
                  final_angle: float, final_error: float}
        """
        if hotel not in self.hotels:
            raise ValueError(
                f"Hotel {hotel} not found. Available: {self.hotels}"
            )
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")

        cfg = self._precise_cfg(overrides)
        target_angle = self.hotel_angles[hotel]
        result = self._two_stage_move(target_angle, cfg)
        if result["success"]:
            self.current_hotel = hotel
        return result

    def go_home(self):
        """Go to home position (0 degrees)"""
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")

        print("Moving to home position (0°)")
        self.packet_handler.write4ByteTxRx(
            self.port, self.motor_id, self.ADDR_GOAL_POSITION, 0
        )

        # Wait for position to be reached
        import time

        start_time = time.time()
        timeout = self.config.get("movement_timeout", 20)
        tolerance = self.config.get("position_tolerance", 0.5)

        while time.time() - start_time < timeout:
            current_pos = self.get_current_position()
            error = abs(current_pos)

            if error <= tolerance:
                self.current_hotel = None
                print(f"✓ Home position reached! Position: {current_pos:.1f}°")
                return True

            time.sleep(0.1)

        print(
            "✗ Timeout waiting for home position. Current: "
            f"{self.get_current_position():.1f}°"
        )
        return False

    def move_to_angle(self, angle):
        """Move to specific angle in degrees"""
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")

        # Convert angle to motor position
        goal_pos = int(angle * self.MAX_POSITION / self.MAX_ANGLE)

        print(f"Moving to {angle}°")
        self.packet_handler.write4ByteTxRx(
            self.port, self.motor_id, self.ADDR_GOAL_POSITION, goal_pos
        )

        # Wait for position to be reached
        import time

        start_time = time.time()
        timeout = self.config.get("movement_timeout", 20)
        tolerance = self.config.get("position_tolerance", 0.5)

        while time.time() - start_time < timeout:
            current_pos = self.get_current_position()
            error = abs(current_pos - angle)

            if error <= tolerance:
                print(
                    "✓ Target position reached! Position: "
                    f"{current_pos:.1f}°"
                )
                return True

            time.sleep(0.1)

        print(
            "✗ Timeout waiting for target position. Current: "
            f"{self.get_current_position():.1f}°"
        )
        return False

    def move_to_angle_precise(self, angle, **overrides):
        """Precise move to angle using two-stage strategy.

        Args:
            angle (float): Target angle in degrees.
            **overrides: Per-call override of precise movement parameters.

        Returns:
            dict: See `activate_hotel_precise` for shape.
        """
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")
        cfg = self._precise_cfg(overrides)
        return self._two_stage_move(angle, cfg)

    def emergency_stop(self):
        """Emergency stop - disable torque immediately"""
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")

        print("🛑 EMERGENCY STOP - Disabling torque")
        self.packet_handler.write1ByteTxRx(
            self.port, self.motor_id, self.ADDR_TORQUE_ENABLE, 0
        )
        return True

    def get_active_hotel(self):
        """
        Get the currently active hotel based on motor position

        Returns:
            str: Hotel identifier or None if position doesn't match any hotel
        """
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")

        current_pos = self.get_current_position()

        # Find closest hotel within tolerance
        min_error = float("inf")
        active_hotel = None

        for hotel, angle in self.hotel_angles.items():
            error = abs(current_pos - angle)
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

        health = {}

        # Temperature (1 byte)
        temp, result, error = self.packet_handler.read1ByteTxRx(
            self.port, self.motor_id, self.ADDR_PRESENT_TEMPERATURE
        )
        health["temperature"] = temp if result == 0 else None

        # Current (2 bytes, signed)
        current, result, error = self.packet_handler.read2ByteTxRx(
            self.port, self.motor_id, self.ADDR_PRESENT_CURRENT
        )
        if result == 0:
            # Convert to signed and mA
            if current > 32767:
                current = current - 65536
            health["current"] = current * 2.69  # Convert to mA
        else:
            health["current"] = None

        # Voltage (2 bytes)
        voltage, result, error = self.packet_handler.read2ByteTxRx(
            self.port, self.motor_id, self.ADDR_PRESENT_VOLTAGE
        )
        # Convert to volts if read succeeded
        health["voltage"] = voltage * 0.1 if result == 0 else None

        # Hardware error status
        hw_error, result, error = self.packet_handler.read1ByteTxRx(
            self.port, self.motor_id, self.ADDR_HARDWARE_ERROR
        )
        health["hardware_error"] = hw_error if result == 0 else None

        # Position feedback with graceful fallback
        try:
            health["position"] = self.get_current_position()
        except Exception as e:  # noqa: BLE001
            health["position"] = None
            health.setdefault("warnings", []).append(
                f"Position read failed: {e}".rstrip()
            )

        # Health warnings
        health["warnings"] = []
        if (
            health["temperature"]
            and health["temperature"] > self.config["temperature_limit"]
        ):
            health["warnings"].append(
                f"High temperature: {health['temperature']}°C"
            )
        if (
            health["current"]
            and abs(health["current"]) > self.config["current_limit"]
        ):
            health["warnings"].append(
                f"High current: {health['current']:.0f}mA"
            )
        if health["voltage"]:
            if health["voltage"] < self.config["voltage_min"]:
                health["warnings"].append(
                    f"Low voltage: {health['voltage']:.1f}V"
                )
            elif health["voltage"] > self.config["voltage_max"]:
                health["warnings"].append(
                    f"High voltage: {health['voltage']:.1f}V"
                )
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

    def set_speed(self, speed):
        """Set motor speed (profile velocity)"""
        self.speed = speed
        if self.port:
            self.packet_handler.write4ByteTxRx(
                self.port,
                self.motor_id,
                112,
                speed,
            )

    def get_current_position(self):
        """Get current motor position in degrees"""
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")

        pos, result, error = self.packet_handler.read4ByteTxRx(
            self.port, self.motor_id, self.ADDR_PRESENT_POSITION
        )
        if result == 0 and error == 0:
            angle = pos * self.MAX_ANGLE / self.MAX_POSITION
            return angle
        else:
            raise Exception("Failed to read position")

    def is_connected(self):  # consolidated; removed legacy test_counter flow
        return self.port is not None and getattr(self.port, "is_open", False)

    def disconnect(self):
        """Disconnect from motor"""
        if self.port:
            self.packet_handler.write1ByteTxRx(
                self.port, self.motor_id, self.ADDR_TORQUE_ENABLE, 0
            )
            self.port.closePort()
            self.port = None

    # Removed duplicate is_connected (runtime artifact)

    # -------------------- Internal precise movement helpers -----------------
    def _precise_cfg(self, overrides):
        """Assemble config for precise move with overrides."""
        base = {
            "tolerance": self.config.get("position_tolerance", 0.5),
            # Safer, conservative defaults if keys absent:
            "switch_error": self.config.get("switch_error", 4.0),
            "stage1_timeout": self.config.get("stage1_timeout", 10.0),
            "poll_interval": self.config.get("poll_interval", 0.35),
            # Pulse stage
            "pulse_pwm_start": self.config.get("pulse_pwm_start", 140),
            "pwm_step": self.config.get("pwm_step", 20),
            "pwm_max": self.config.get("pwm_max", 480),
            "pulse_duration": self.config.get("pulse_duration", 0.25),
            "pulse_rest": self.config.get("pulse_rest", 0.25),
            "pulse_max": self.config.get("pulse_max", 30),
            "motion_threshold": self.config.get("motion_threshold", 0.10),
            "stall_pulses": self.config.get("stall_pulses", 6),
            # Backoff
            "enable_backoff": self.config.get("enable_backoff", True),
            "max_step_factor": self.config.get("max_step_factor", 1.4),
            "pwm_backoff_step": self.config.get("pwm_backoff_step", 50),
            "precise_log": self.config.get("precise_log", True),
        }
        for k, v in overrides.items():
            base[k] = v
        return base

    def show_precise_params(self):
        """Print current precise movement parameters (resolved)."""
        cfg = self._precise_cfg({})
        print("\n[Precise Params]")
        for k in sorted(cfg.keys()):
            print(f"  {k}: {cfg[k]}")
        return cfg

    def tune_precise(self, **updates):
        """Runtime update of YAML-backed config keys for precise move.

        Example:
            resort.tune_precise(pulse_pwm_start=160, pwm_step=30)
        These persist only for this process (do not write back to file).
        """
        for k, v in updates.items():
            self.config[k] = v
        # Show summary after update
        if updates:
            print("[TUNE] Updated keys:")
            for k, v in updates.items():
                print(f"  {k} -> {v}")
        return self.show_precise_params()

    def _deg_to_raw(self, deg):  # small helper for clarity
        return int(deg * self.MAX_POSITION / self.MAX_ANGLE)

    def _read_deg(self):
        pos, res, err = self.packet_handler.read4ByteTxRx(
            self.port, self.motor_id, self.ADDR_PRESENT_POSITION
        )
        if res == 0 and err == 0:
            return pos * self.MAX_ANGLE / self.MAX_POSITION
        raise RuntimeError("position read failed")

    def _set_mode(self, mode):
        # Disable torque, set mode, enable torque (Operating Mode addr=11)
        self.packet_handler.write1ByteTxRx(
            self.port, self.motor_id, self.ADDR_TORQUE_ENABLE, 0
        )
        self.packet_handler.write1ByteTxRx(self.port, self.motor_id, 11, mode)
        self.packet_handler.write1ByteTxRx(
            self.port, self.motor_id, self.ADDR_TORQUE_ENABLE, 1
        )
        # Reapply profile velocity & acceleration after mode switch
        self.packet_handler.write4ByteTxRx(
            self.port,
            self.motor_id,
            112,
            self.speed,
        )
        accel = self.config.get("profile_acceleration", 0)
        if accel and accel > 0:
            self.packet_handler.write4ByteTxRx(
                self.port,
                self.motor_id,
                108,
                int(accel),
            )

    def _two_stage_move(self, target_angle, cfg):
        """Coarse position then PWM pulses toward target angle."""
        # Stage 1: coarse position mode (3)
        self._set_mode(3)
        goal_pos = self._deg_to_raw(target_angle)
        self.packet_handler.write4ByteTxRx(
            self.port, self.motor_id, self.ADDR_GOAL_POSITION, goal_pos
        )
        import time

        start = time.time()
        while True:
            try:
                present = self._read_deg()
            except Exception:
                return {
                    "success": False,
                    "reason": "read_fail_stage1",
                    "pulses": 0,
                    "final_angle": None,
                    "final_error": None,
                }
            err = abs(target_angle - present)
            if cfg["precise_log"]:
                print(f"pos={present:.2f}° err={err:.2f}°")
            if err <= cfg["tolerance"]:
                return {
                    "success": True,
                    "reason": "coarse_success",
                    "pulses": 0,
                    "final_angle": present,
                    "final_error": err,
                }
            if err <= cfg["switch_error"]:
                if cfg["precise_log"]:
                    print(
                        f"[SWITCH] residual {err:.2f}° <= "
                        f"{cfg['switch_error']:.2f}° -> pulses"
                    )
                break
            if (
                cfg["stage1_timeout"] is not None
                and time.time() - start > cfg["stage1_timeout"]
            ):
                if cfg["precise_log"]:
                    print("[TIMEOUT] stage1 -> pulses")
                break
            time.sleep(cfg["poll_interval"])

        # Stage 2: PWM pulses (mode 16)
        self._set_mode(16)
        pulses = 0
        pwm_value = int(cfg["pulse_pwm_start"])
        stall_count = 0
        last_angle = self._read_deg()
        while pulses < cfg["pulse_max"]:
            present = last_angle
            err_signed = target_angle - present
            abs_err = abs(err_signed)
            if cfg["precise_log"]:
                print(
                    f"pulse={pulses} pos={present:.2f}° err={abs_err:.2f}° "
                    f"pwm={pwm_value}"
                )
            if abs_err <= cfg["tolerance"]:
                return {
                    "success": True,
                    "reason": "pulses_success",
                    "pulses": pulses,
                    "final_angle": present,
                    "final_error": abs_err,
                }
            direction = 1 if err_signed > 0 else -1
            applied_pwm = direction * pwm_value
            # Write PWM (addr 100), mask to 2 bytes
            self.packet_handler.write2ByteTxRx(
                self.port, self.motor_id, 100, applied_pwm & 0xFFFF
            )
            time.sleep(cfg["pulse_duration"])
            self.packet_handler.write2ByteTxRx(
                self.port, self.motor_id, 100, 0
            )
            time.sleep(cfg["pulse_rest"])
            try:
                new_angle = self._read_deg()
            except Exception:
                return {
                    "success": False,
                    "reason": "read_fail_pulse",
                    "pulses": pulses,
                    "final_angle": None,
                    "final_error": None,
                }
            delta = abs(new_angle - present)
            last_angle = new_angle
            # Backoff
            if (
                cfg["enable_backoff"]
                and abs_err < cfg["switch_error"]
                and delta > cfg["tolerance"] * cfg["max_step_factor"]
            ):
                new_pwm = max(
                    int(cfg["pulse_pwm_start"]),
                    pwm_value - cfg["pwm_backoff_step"],
                )
                if cfg["precise_log"]:
                    limit = cfg["tolerance"] * cfg["max_step_factor"]
                    print(
                        f"[BACKOFF] delta={delta:.2f}° > {limit:.2f}° "
                        f"pwm {pwm_value}->{new_pwm}"
                    )
                pwm_value = new_pwm
            # Escalate
            if delta < cfg["motion_threshold"] and abs_err > cfg["tolerance"]:
                pwm_value = min(pwm_value + cfg["pwm_step"], cfg["pwm_max"])
            # Stall tracking
            if delta < cfg["motion_threshold"]:
                stall_count += 1
            else:
                stall_count = 0
            if stall_count >= cfg["stall_pulses"]:
                if cfg["precise_log"]:
                    print(
                        f"[STALL] <{cfg['motion_threshold']}° for "
                        f"{stall_count} pulses; stopping"
                    )
                return {
                    "success": False,
                    "reason": "stall",
                    "pulses": pulses,
                    "final_angle": new_angle,
                    "final_error": abs_err,
                }
            pulses += 1
        return {
            "success": False,
            "reason": "max_pulses",
            "pulses": pulses,
            "final_angle": last_angle,
            "final_error": abs(target_angle - last_angle),
        }
