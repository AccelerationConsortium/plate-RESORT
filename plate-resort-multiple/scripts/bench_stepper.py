#!/usr/bin/env python3
"""Isolated Pi bench checks. See docs/stepper-overhaul.md before moving hardware."""
import argparse
from contextlib import ExitStack
import json
import math
import subprocess
import sys
import time


def read_sensor(bus):
    # Read STATUS and RAW ANGLE together; never write configuration or OTP.
    status, high, low = bus.read_i2c_block_data(0x36, 0x0B, 3)
    raw = ((high & 0x0F) << 8) | low
    return dict(raw=raw, motor_degrees=raw * 360 / 4096,
                magnet_detected=bool(status & 0x20),
                magnet_weak=bool(status & 0x10), magnet_strong=bool(status & 0x08))


def magnet_ok(sample):
    return (sample['magnet_detected'] and not sample['magnet_weak']
            and not sample['magnet_strong'])


def tic(args, *options):
    result = subprocess.run(
        [args.ticcmd, '--serial', args.serial, *map(str, options)],
        check=True, capture_output=True, text=True, timeout=2)
    return result.stdout


def stop(args):
    # Try both even if the first USB command fails. Hardware timeout is the fallback.
    errors = []
    for command in ('--halt-and-hold', '--deenergize'):
        try:
            tic(args, command)
        except Exception as exc:
            errors.append(str(exc))
    if errors:
        print('STOP communication failed; remove motor power if needed: '
              + '; '.join(errors), file=sys.stderr)
    return not errors


def run(args):
    if args.mode == 'status':
        print(tic(args, '--status', '--full'))
        return
    if args.mode == 'stop':
        if not stop(args):
            raise RuntimeError('Could not confirm stop commands')
        return
    with ExitStack() as stack:
        from smbus2 import SMBus
        from gpiozero import DigitalInputDevice
        bus = stack.enter_context(SMBus(args.bus))
        # NC contact grounds pin at rest; open contact (pressed/broken wire) is high.
        switch = DigitalInputDevice(args.switch_gpio, pull_up=True)
        stack.callback(switch.close)

        def sample():
            value = read_sensor(bus)
            value['home_active_or_wire_open'] = bool(switch.pin.state)
            return value

        if args.mode == 'watch':
            end = time.monotonic() + args.seconds
            while time.monotonic() < end:
                print(json.dumps(sample()), flush=True)
                time.sleep(0.05)
            return

        # All motion cleanup starts before any motor-changing command.
        try:
            initial = sample()
            if not magnet_ok(initial):
                raise RuntimeError('Magnet missing or outside usable field range')
            if initial['home_active_or_wire_open']:
                raise RuntimeError('Release home switch / check NC wiring before jog')
            print(tic(args, '--status', '--full'))
            # Bench-local zero only: this is NOT a carousel homing operation.
            tic(args, '--halt-and-set-position', 0)
            tic(args, '--max-speed', 1000000)  # 100 microsteps/s
            tic(args, '--energize')
            tic(args, '--exit-safe-start', '--position', args.steps)
            end = time.monotonic() + args.seconds
            while time.monotonic() < end:
                value = sample()
                print(json.dumps(value), flush=True)
                if not magnet_ok(value):
                    raise RuntimeError('Encoder magnetic field fault during jog')
                if value['home_active_or_wire_open']:
                    raise RuntimeError('Home switch activated or wire opened during jog')
                tic(args, '--reset-command-timeout')
                time.sleep(0.05)
            print(tic(args, '--status', '--full'))
            print('Jog window ended. Inspect encoder change and Tic status; '
                  'this script does not certify position or motion completion.')
        finally:
            if not stop(args):
                raise RuntimeError('Stop communication failed')


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['watch', 'status', 'jog', 'stop'])
    p.add_argument('--serial', help='Tic serial number from ticcmd --list')
    p.add_argument('--ticcmd', default='ticcmd')
    p.add_argument('--bus', type=int, default=1)
    p.add_argument('--switch-gpio', type=int, default=17, help='BCM number, default 17')
    p.add_argument('--seconds', type=float, default=5)
    p.add_argument('--steps', type=int, default=100, help='Signed microsteps, max magnitude 200')
    p.add_argument('--allow-motion', action='store_true')
    return p


def main():
    p = parser()
    args = p.parse_args()
    if not math.isfinite(args.seconds) or not 0 < args.seconds <= 60:
        p.error('--seconds must be finite and in (0, 60]')
    if args.mode != 'watch' and not args.serial:
        p.error('--serial is required for Tic commands')
    if args.mode == 'jog':
        if not args.allow_motion:
            p.error('jog requires --allow-motion after completing the wiring checklist')
        if not 0 < abs(args.steps) <= 200:
            p.error('jog requires 1..200 microsteps in either direction')
    try:
        run(args)
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
