"""Minimal interactive CLI for Plate Resort flows.

Supports local execution (default) or remote Prefect Cloud submissions with
--remote.
Commands:
  connect                    Connect to motor
  activate <hotel>           Activate hotel (A/B/C/D)
  position                   Get current position
  stop                       Emergency stop
  disconnect                 Disconnect (releases torque)
  help                       Show help
  exit / quit                Exit CLI

Examples:
  plate-resort-interactive                    # local flows
  plate-resort-interactive --remote           # remote deployments

Environment (remote mode requires): PREFECT_API_URL, PREFECT_API_KEY
"""
from __future__ import annotations
import sys
from typing import Optional
from plate_resort.workflows import orchestrator
from plate_resort.workflows import flows  # local direct flows

HOTELS = {"A", "B", "C", "D"}


def _print_help():
    print("\nCommands:")
    print("  connect                    Connect to motor")
    print("  activate <hotel>           Activate hotel (A/B/C/D)")
    print("  position                   Get current position")
    print("  stop                       Emergency stop")
    print("  disconnect                 Disconnect from motor")
    print("  help                       Show this help")
    print("  exit | quit                Exit CLI")


def _run_local(cmd: str, args: list[str]):
    if cmd == "connect":
        flows.connect()
        print("Connected (local)")
    elif cmd == "activate":
        if not args:
            print("Specify hotel (A/B/C/D)")
            return
        hotel = args[0].upper()
        if hotel not in HOTELS:
            print("Invalid hotel")
            return
        flows.activate_hotel(hotel)
        print(f"Activated hotel {hotel} (local)")
    elif cmd == "position":
        pos = flows.get_current_position()
        print(f"Position: {pos}")
    elif cmd == "stop":
        flows.emergency_stop()
        print("Emergency stop issued (local)")
    elif cmd == "disconnect":
        flows.disconnect()
        print("Disconnected (local)")
    else:
        print("Unknown command; type 'help'")


def _run_remote(cmd: str, args: list[str]):
    if cmd == "connect":
        run = orchestrator.connect()
        state = orchestrator.wait(run)
        print(f"Connect state: {state.type}")
    elif cmd == "activate":
        if not args:
            print("Specify hotel (A/B/C/D)")
            return
        hotel = args[0].upper()
        if hotel not in HOTELS:
            print("Invalid hotel")
            return
        run = orchestrator.activate_hotel(hotel)
        state = orchestrator.wait(run)
        print(f"Activate {hotel} state: {state.type}")
    elif cmd == "position":
        run = orchestrator.get_position()
        state = orchestrator.wait(run)
        if hasattr(state, "data") and state.data is not None:
            print(f"Position: {state.data}")
        else:
            print(f"Position flow state: {state.type}")
    elif cmd == "stop":
        run = orchestrator.emergency_stop()
        state = orchestrator.wait(run)
        print(f"Emergency stop state: {state.type}")
    elif cmd == "disconnect":
        run = orchestrator.disconnect()
        state = orchestrator.wait(run)
        print(f"Disconnect state: {state.type}")
    else:
        print("Unknown command; type 'help'")


def main(argv: Optional[list[str]] = None):
    argv = argv or sys.argv[1:]
    remote = False
    if "--remote" in argv:
        remote = True
        argv.remove("--remote")
    print("Plate Resort Interactive CLI (remote=" + str(remote) + ")")
    _print_help()
    while True:
        try:
            raw = input("› ").strip()
        except (EOFError, KeyboardInterrupt):
            print()  # newline
            break
        if not raw:
            continue
        if raw.lower() in {"exit", "quit"}:
            break
        if raw.lower() == "help":
            _print_help()
            continue
        parts = raw.split()
        cmd, args = parts[0].lower(), parts[1:]
        if remote:
            _run_remote(cmd, args)
        else:
            _run_local(cmd, args)
    print("Bye.")


if __name__ == "__main__":  # pragma: no cover
    main()
