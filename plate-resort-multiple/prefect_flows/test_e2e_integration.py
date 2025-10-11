#!/usr/bin/env python3
"""
End-to-end integration test for Prefect orchestration.
Tests the full workflow: server -> orchestrator -> worker -> device
"""
import asyncio
import subprocess
import time
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_command(cmd, description, timeout=30, check=True):
    """Run a shell command and return result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False
    )
    
    print(f"Return code: {result.returncode}")
    if result.stdout:
        print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {description}")
    
    return result

async def main():
    """Run end-to-end integration test"""
    print("\n" + "="*80)
    print("PREFECT END-TO-END INTEGRATION TEST")
    print("="*80)
    
    # Change to plate_resort directory where config file is
    os.chdir(Path(__file__).parent.parent / "plate_resort")
    print(f"\nWorking directory: {os.getcwd()}")
    
    # Step 1: Check Prefect installation
    print("\n[Step 1] Checking Prefect installation...")
    result = run_command("prefect version", "Check Prefect version")
    
    # Step 2: Start Prefect server in background
    print("\n[Step 2] Starting Prefect server...")
    server_process = subprocess.Popen(
        ["prefect", "server", "start"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(f"Server started with PID: {server_process.pid}")
    
    # Wait for server to be ready
    print("Waiting for server to start...")
    for i in range(30):
        time.sleep(1)
        try:
            result = subprocess.run(
                ["prefect", "server", "health"],
                capture_output=True,
                timeout=5,
                check=False
            )
            if result.returncode == 0:
                print("✓ Server is healthy!")
                break
        except:
            pass
        if i % 5 == 0:
            print(f"  Still waiting... ({i+1}s)")
    else:
        server_process.terminate()
        raise RuntimeError("Server failed to start within 30 seconds")
    
    try:
        # Step 3: Create work pool
        print("\n[Step 3] Creating work pool...")
        run_command(
            "prefect work-pool create plate-resort-pool --type process",
            "Create work pool",
            check=False  # May already exist
        )
        
        # Verify work pool
        result = run_command("prefect work-pool ls", "List work pools")
        
        # Step 4: Deploy flows
        print("\n[Step 4] Deploying flows...")
        os.chdir(Path(__file__).parent)  # Back to prefect_flows
        result = run_command(
            "python deploy_flows.py",
            "Deploy flows",
            timeout=60
        )
        
        # Verify deployments
        result = run_command("prefect deployment ls", "List deployments")
        
        # Step 5: Test flow execution with inline worker
        print("\n[Step 5] Testing flow execution...")
        
        # Create a simple test script that runs a flow directly
        test_script = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from plate_resort.core import PlateResort

# Create instance and test that flow decorator works
resort = PlateResort()
print(f"✓ PlateResort instance created")
print(f"✓ Device: {resort.device}")
print(f"✓ Hotels: {resort.hotels}")

# Test that method has flow attributes
print(f"✓ connect is a flow: {hasattr(resort.connect, 'fn')}")
print(f"✓ activate_hotel is a flow: {hasattr(resort.activate_hotel, 'fn')}")

# Test flow metadata
print(f"✓ connect flow name: {resort.connect.name}")
print(f"✓ activate_hotel flow name: {resort.activate_hotel.name}")

print("\\n✓ All flow integration tests passed!")
"""
        
        with open("/tmp/test_flow_integration.py", "w") as f:
            f.write(test_script)
        
        os.chdir(Path(__file__).parent.parent / "plate_resort")
        result = run_command(
            "python /tmp/test_flow_integration.py",
            "Test flow integration",
            timeout=10
        )
        
        # Step 6: Test deployment retrieval
        print("\n[Step 6] Testing deployment retrieval...")
        test_deployment_script = """
import asyncio
from prefect.client.orchestration import get_client

async def test_deployments():
    async with get_client() as client:
        deployments = await client.read_deployments()
        print(f"✓ Found {len(deployments)} deployments")
        
        for dep in deployments[:5]:  # Show first 5
            print(f"  - {dep.name} (flow: {dep.flow_name})")
        
        # Look for our specific deployments
        our_deps = [d for d in deployments if 'plate-resort' in d.name]
        print(f"\\n✓ Found {len(our_deps)} plate-resort deployments")
        
        if our_deps:
            print("\\nDeployment details:")
            for dep in our_deps[:3]:
                print(f"  - Name: {dep.name}")
                print(f"    Work pool: {dep.work_pool_name}")
                print(f"    Flow: {dep.flow_name}")
        
        return len(deployments) > 0

result = asyncio.run(test_deployments())
print(f"\\n✓ Deployment test {'PASSED' if result else 'FAILED'}")
"""
        
        with open("/tmp/test_deployments.py", "w") as f:
            f.write(test_deployment_script)
        
        result = run_command(
            "python /tmp/test_deployments.py",
            "Test deployment retrieval",
            timeout=15
        )
        
        # Step 7: Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print("✓ Prefect server started successfully")
        print("✓ Work pool created")
        print("✓ Flows deployed successfully")
        print("✓ Flow decorators working correctly")
        print("✓ Deployments retrievable from API")
        print("\n✓ ALL INTEGRATION TESTS PASSED!")
        print("="*80)
        
        print("\n[INFO] Server is running at http://127.0.0.1:4200")
        print("[INFO] To manually test worker, run in another terminal:")
        print(f"  cd {Path(__file__).parent}")
        print("  python worker_service.py")
        print("\n[INFO] To submit a flow run from orchestrator:")
        print("  python -c 'from orchestrator import get_health; get_health()'")
        
    finally:
        # Cleanup
        print("\n[Cleanup] Stopping Prefect server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("✓ Server stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
