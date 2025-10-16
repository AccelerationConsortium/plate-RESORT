#!/usr/bin/env python3
"""
Plate Resort Demo Script - Prefect Workflows
Demonstrates all available workflow operations
"""

import os
import sys
import time
from plate_resort.core import PlateResort


def demo_local_flows():
    """Demonstrate local Prefect flow execution"""
    print("🚀 Plate Resort Demo - Local Flows")
    print("═" * 50)

    try:
        # Initialize PlateResort (with @flow decorators)
        print("📦 Initializing PlateResort...")
        resort = PlateResort()
        print("✅ PlateResort initialized with Prefect flows")

        print("\n🔍 Testing flow decorators...")
        for method_name in [
            "connect",
            "activate_hotel",
            "go_home",
            "move_to_angle",
            "get_current_position",
        ]:
            method = getattr(resort, method_name)
            if hasattr(method, "__wrapped__"):
                print(f"✅ {method_name} is a Prefect flow")
            else:
                print(f"❌ {method_name} is NOT a flow")

        print("\n🏠 Demo 1: Connection Flow")
        print("-" * 30)
        try:
            result = resort.connect()
            print(f"✅ Connect flow completed: {result}")
        except Exception as e:
            print(f"ℹ️  Connect flow: {e} (expected without hardware)")

        print("\n📍 Demo 2: Position Flow")
        print("-" * 30)
        try:
            position = resort.get_current_position()
            print(f"✅ Position flow completed: {position}°")
        except Exception as e:
            print(f"ℹ️  Position flow: {e} (expected without hardware)")

        print("\n🏨 Demo 3: Hotel Activation Flow")
        print("-" * 30)
        try:
            result = resort.activate_hotel("A")
            print(f"✅ Activate hotel flow completed: {result}")
        except Exception as e:
            print(f"ℹ️  Activate hotel flow: {e} (expected without hardware)")

        print("\n🎯 Demo 4: Angle Movement Flow")
        print("-" * 30)
        try:
            result = resort.move_to_angle(45.0)
            print(f"✅ Move to angle flow completed: {result}")
        except Exception as e:
            print(f"ℹ️  Move to angle flow: {e} (expected without hardware)")

        print("\n🏠 Demo 5: Home Position Flow")
        print("-" * 30)
        try:
            result = resort.go_home()
            print(f"✅ Go home flow completed: {result}")
        except Exception as e:
            print(f"ℹ️  Go home flow: {e} (expected without hardware)")

        print("\n🩺 Demo 6: Health Check Flow")
        print("-" * 30)
        try:
            health = resort.get_motor_health()
            print(f"✅ Health check flow completed: {health}")
        except Exception as e:
            print(f"ℹ️  Health check flow: {e} (expected without hardware)")

        print("\n🔌 Demo 7: Disconnect Flow")
        print("-" * 30)
        try:
            result = resort.disconnect()
            print(f"✅ Disconnect flow completed: {result}")
        except Exception as e:
            print(f"ℹ️  Disconnect flow: {e} (expected without hardware)")

        print("\n" + "═" * 50)
        print("✅ All Prefect flows demonstrated successfully!")
        print("💡 Each method call above was executed as a Prefect flow")
        print("🔗 For remote orchestration, use the workflows.orchestrator module")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

    return True


def demo_remote_flows():
    """Demonstrate remote Prefect flow orchestration"""
    print("🚀 Plate Resort Demo - Remote Flows")
    print("═" * 50)

    try:
        from plate_resort.workflows import orchestrator

        print("📡 Testing remote flow orchestration...")
        print("⚠️  Note: Requires Prefect server and worker running")

        print("\n🔌 Demo 1: Remote Connect")
        print("-" * 30)
        try:
            result = orchestrator.connect()
            print(f"📡 Remote connect flow submitted: {result}")
        except Exception as e:
            print(f"❌ Remote flow error: {e}")

        print("\n📍 Demo 2: Remote Position Check")
        print("-" * 30)
        try:
            result = orchestrator.get_position()
            print(f"📡 Remote position flow submitted: {result}")
        except Exception as e:
            print(f"❌ Remote flow error: {e}")

        print("\n🏨 Demo 3: Remote Hotel Activation")
        print("-" * 30)
        try:
            result = orchestrator.activate_hotel("B")
            print(f"📡 Remote activate hotel flow submitted: {result}")
        except Exception as e:
            print(f"❌ Remote flow error: {e}")

        print("\n" + "═" * 50)
        print("✅ Remote flow orchestration demonstrated!")
        print("💡 Flows were submitted to Prefect work pool for execution")

    except ImportError as e:
        print(f"❌ Remote orchestration not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Remote demo failed: {e}")
        return False

    return True


def main():
    """Main demo function"""
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--help", "-h"]:
            print("Usage: python demo.py [--remote/-r]")
            print("  --remote/-r: Demonstrate remote orchestration")
            print("  Default: Demonstrate local flows")
            return

    use_remote = "--remote" in sys.argv or "-r" in sys.argv

    if use_remote:
        success = demo_remote_flows()
    else:
        success = demo_local_flows()

    if not success:
        sys.exit(1)

    print("\n🎉 Demo completed successfully!")


if __name__ == "__main__":
    main()
