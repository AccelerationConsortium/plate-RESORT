"""Prefect client example: activate hotel A then hotel D.

Submits hotel A activation, waits for completion, then submits hotel D.
Requires PREFECT_API_URL and PREFECT_API_KEY exported.
"""

from plate_resort.workflows import orchestrator

print("Activating hotel A then hotel D (waiting for each to complete):")

# Hotel A
run_a = orchestrator.activate_hotel("A")
print(f"Hotel A submitted: {run_a.id} (waiting for completion)", flush=True)
state_a = orchestrator.wait(run_a)
print(f"  -> final state: {state_a.type}")
if state_a.is_failed():
    print("Sequence halted due to failure at hotel A.")
else:
    # Hotel D
    run_d = orchestrator.activate_hotel("D")
    print(
        f"Hotel D submitted: {run_d.id} (waiting for completion)",
        flush=True,
    )
    state_d = orchestrator.wait(run_d)
    print(f"  -> final state: {state_d.type}")
    if state_d.is_failed():
        print("Sequence halted due to failure at hotel D.")
    else:
        print("Sequence A -> D completed successfully.")
