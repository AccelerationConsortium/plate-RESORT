#!/usr/bin/env python3
"""
Test script for the closed-loop control method (mode 5 + integral gain).

Usage:
  python test_closed_loop.py --selftest         # no hardware: angle math checks
  python test_closed_loop.py B                  # verified move to hotel B
  python test_closed_loop.py --angle 109        # verified move to an angle
  python test_closed_loop.py --cycle            # A->B->C->D->A with a report
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plate_resort.core import PlateResort


def selftest():
    """Pure-math checks that run without hardware."""
    wrap = PlateResort._wrap_deg
    cases = [
        (0.0, 0.0),
        (90.0, 90.0),
        (-90.0, -90.0),
        (180.0, 180.0),
        (-180.0, 180.0),
        (190.0, -170.0),
        (-190.0, 170.0),
        (359.6, -0.4),
        (-359.6, 0.4),
        (720.0, 0.0),
    ]
    for delta, expected in cases:
        got = wrap(delta)
        assert abs(got - expected) < 1e-9, f"wrap({delta}) = {got}, want {expected}"

    # Shortest path across the 0/360 seam: at 350°, target 10° -> +20°
    assert abs(wrap(10.0 - 350.0) - 20.0) < 1e-9
    # And the reverse: at 10°, target 350° -> -20°
    assert abs(wrap(350.0 - 10.0) - (-20.0)) < 1e-9

    assert PlateResort._to_signed32(4294967293) == -3
    assert PlateResort._to_signed32(2048) == 2048
    assert PlateResort._to_signed16(65535) == -1
    assert PlateResort._to_signed16(1193) == 1193

    # Hotel angles normalize into [0, 360) for either rotation direction
    resort = PlateResort(rotation_direction=-1)
    for hotel, angle in resort.hotel_angles.items():
        assert 0.0 <= angle < 360.0, f"hotel {hotel} angle {angle} not normalized"

    print("✅ Selftest passed (wrap math, signed conversion, angle normalization)")


def report(result):
    print("\n📊 Move result:")
    print(f"   ✅ Success: {result['success']}")
    print(f"   📝 Reason: {result['reason']}")
    if result.get("final_angle") is not None:
        print(f"   📍 Final position: {result['final_angle']:.3f}°")
        print(f"   📏 Final error: {result['final_error']:.3f}°")
    print(f"   ⏱️ Elapsed: {result['elapsed_s']:.2f}s")
    if result.get("peak_current_ma") is not None:
        print(f"   ⚡ Peak current: {result['peak_current_ma']:.0f}mA")
    if result.get("hardware_error"):
        faults = ", ".join(
            PlateResort._decode_hardware_error(result["hardware_error"])
        ) or "unknown"
        print(
            f"   🚨 Hardware error: 0x{result['hardware_error']:02X} ({faults})"
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hotel", nargs="?", help="Hotel to activate (A/B/C/D)")
    parser.add_argument("--angle", type=float, help="Move to a specific angle")
    parser.add_argument("--cycle", action="store_true", help="Cycle all hotels")
    parser.add_argument("--selftest", action="store_true", help="No-hardware checks")
    args = parser.parse_args()

    if args.selftest:
        selftest()
        return

    resort = PlateResort()
    try:
        print("🔌 Connecting to hardware...")
        resort.connect()
        print(f"ℹ️ Motor: {resort.get_motor_info()}")
        resort.show_control_params()
        print(f"📍 Current position: {resort.get_current_position():.2f}°")

        if args.cycle:
            hotels = resort.hotels + [resort.hotels[0]]
            for hotel in hotels:
                result = resort.goto_hotel(hotel)
                report(result)
                if not result["success"]:
                    print(f"❌ Aborting cycle at hotel {hotel}")
                    break
        elif args.angle is not None:
            result = resort.move(args.angle)
            report(result)
        elif args.hotel:
            result = resort.goto_hotel(args.hotel.upper())
            report(result)
        else:
            print("Nothing to do: pass a hotel, --angle, --cycle, or --selftest")

        resort.print_motor_health()
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if resort.port:
            resort.disconnect()
            print("🔌 Disconnected from hardware")


if __name__ == "__main__":
    main()
