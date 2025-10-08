from prefect.deployments import run_deployment

run_deployment(name="connect/connect")

run_deployment(name="status/status")

run_deployment(name="activate-hotel/activate-hotel", parameters={"hotel": "A"})

run_deployment(name="get-position/get-position")

run_deployment(name="go-home/go-home")
