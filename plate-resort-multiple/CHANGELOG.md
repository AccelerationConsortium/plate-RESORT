# Changelog

All notable changes to this project will be documented in this file.

## [2.0.5] - 2025-10-16
## [2.0.6] - 2025-10-16
## [2.0.11] - 2025-10-21

### Fixed
- Removed unsupported `entrypoint` argument from `Flow.deploy` calls (Prefect 3.4.23 API does not accept it).

### Notes
- Run `plate-resort-deploy` again to register flows without error.

## [2.0.10] - 2025-10-21

### Fixed
- `deploy.py` now handles Prefect Flow objects correctly (uses `flow.fn` instead of passing Flow object to `inspect.getsourcefile`), preventing TypeError during deployment.

### Notes
- Re-run `plate-resort-deploy` after upgrading to register deployments successfully.

## [2.0.9] - 2025-10-21

### Changed
- `PlateResort.connect` now accepts optional overrides: `device`, `baudrate`, `motor_id` for flow parameter pass-through.

### Removed
- Console script entries for deleted artifacts (`plate-resort-demo`, `plate-resort-update`).

### Notes
- Function-based Prefect flows can now supply connection parameters safely without signature mismatch crashes.

## [2.0.8] - 2025-10-21

### Removed
- Legacy artifacts: `plate_resort/utils/keygen.py`, `plate_resort/utils/update.py`, `plate_resort/client/demo.py`, temporary `test_counter` Prefect flow method, duplicate `is_connected`.
- Legacy config search path entry for `resort_config.yaml`.

### Changed
- `.gitignore` now ignores `archived/`, `archived_gui/`, and `verify_prefect.py` (archives retained locally).
- Clarified hotel angle computation comment in `defaults.yaml`.
- Consolidated single `is_connected` method.

### Notes
- Archives preserved for reference but excluded from change tracking; consider moving to separate branch in future.

## [2.0.7] - 2025-10-16

### Fixed
- Deployment failures due to Prefect attempting to read a non-existent script path (`/home/pi/plate_resort/core.py`). Added explicit module entrypoints in `deploy.py` so flows are resolved from `plate_resort.workflows.flows:<function>` rather than inferred file paths.

### Added
- Deployment output now prints each flow's entrypoint string along with s  Stored in directory: /tmp/pip-ephem-wheel-cache-8mgnby2f/wheels/0b/aa/c0/11eecf10bed573525c496e7254c0e4a38ec0a80e991cc2e583
Successfully built plate-resort
Installing collected packages: pyserial, websockets, uvloop, urllib3, typing-extensions, sniffio, pyyaml, python-dotenv, idna, httptools, h11, dynamixel-sdk, click, charset_normalizer, certifi, annotated-types, uvicorn, typing-inspection, requests, pydantic-core, anyio, watchfiles, starlette, pydantic, fastapi, plate-resort
Successfully installed annotated-types-0.7.0 anyio-4.11.0 certifi-2025.10.5 charset_normalizer-3.4.4 click-8.3.0 dynamixel-sdk-3.8.4 fastapi-0.119.1 h11-0.16.0 httptools-0.7.1 idna-3.11 plate-resort-2.0.0 pydantic-2.12.3 pydantic-core-2.41.4 pyserial-3.5 python-dotenv-1.1.1 pyyaml-6.0.3 requests-2.32.5 sniffio-1.3.1 starlette-0.48.0 typing-extensions-4.15.0 typing-inspection-0.4.2 urllib3-2.5.0 uvicorn-0.38.0 uvloop-0.22.1 watchfiles-1.1.1 websockets-15.0.1
-bash: plate-resort-deploy: command not found
-bash: prefect: command not found
-bash: prefect: command not foundource file.

### Notes
- If stale `deploy.py` persists, fully uninstall (`pip uninstall -y plate-resort`), remove any `plate_resort*` directories in the venv `site-packages`, then reinstall with `--force-refresh`.


### Added
- `install.sh` flags: `--force-refresh` (delete venv + no pip cache), `--ref <git-ref>` (override branch/tag/commit for install).

### Changed
- Installer now prints the git ref used for clarity.
- Force refresh bypasses wheel and HTTP caches to ensure latest remote commit is fetched.

### Notes
- Use `--force-refresh` when suspecting stale artifacts or cached wheels.
- `--ref` enables pinning to a release tag or commit SHA for reproducible setups.


### Added
- Debug instrumentation in `plate_resort.workflows.deploy` to print source file path for each flow function during deployment.

### Fixed
- Began addressing Prefect deployment import path mismatch (`FileNotFoundError: /home/pi/plate_resort/core.py`). The package installs under `site-packages/plate_resort/` but Prefect attempted to load a filesystem path as if it were a loose script. Debug output will help confirm correct `site-packages` path on the Raspberry Pi.

### Notes
- If Prefect still resolves `/home/pi/plate_resort/core.py`, ensure the virtual environment has the package installed (not just a partial copy) and that `plate_resort` is not shadowed by a directory named `plate_resort` in `$HOME`. Remove/rename any stray `$HOME/plate_resort/` directory to avoid import shadowing.

## [2.0.4] - 2025-10-16

### Removed
- Orphaned `plate-resort-keygen` console script entry from `pyproject.toml` (legacy REST/key generation utility fully retired).

### Changed
- Updated `README.md` to reflect Prefect-only architecture and environment variable based authentication (removed residual keygen / REST references).
 - Simplified `install.sh`; now auto-deploys flows and starts worker when Prefect env vars are present.
 - Bumped package version to 2.0.4.

### Notes
- Key generation is no longer part of the workflow; use Prefect Cloud API credentials via environment variables.

## [2.0.3] - 2025-10-16

### Added
- `bootstrap_pi.sh` script for end-to-end fresh Raspberry Pi setup (clone, venv, deploy Prefect flows, start worker).
- `verify_prefect.py` diagnostic script to confirm Prefect Cloud connectivity, work pool presence, deployments, and recent flow runs.

### Changed
- Pinned Prefect dependency to `prefect==3.4.23` for stable flow deployment behavior.

### Notes
- Future Prefect upgrades should edit pin deliberately; run `verify_prefect.py` after any upgrade.

## [2.0.1] - 2025-10-15

### Fixed
- Resolved Prefect Cloud flow crash (SignatureMismatchError) by removing extraneous parameters from remote `connect` deployment submission.
- Updated `orchestrator.connect()` to call `run_deployment(name="connect/connect")` without a parameter dict (method flow expects only `self`).

### Notes
- Other flows (activate-hotel, move-to-angle, etc.) retain parameters matching their method signatures.
- No breaking API changes; remote client now successfully submits `connect` without crashing.

## [2.1.0] - 2025-01-XX

## [2.0.2] - 2025-10-15

### Changed
- Removed `@flow` decorators from `PlateResort` class methods to eliminate signature mismatches.
- Deployments now source only function-based flows in `plate_resort/workflows/flows.py`.
- `deploy.py` refactored to use explicit function list (`FUNCTION_FLOWS`).
- `orchestrator.connect` restored to accept device/baud/motor parameters for the function flow.

### Fixed
- Resolved repeated CRASHED flow runs caused by method-based deployments passing unexpected parameters.

### Notes
- Class still usable locally; Prefect orchestration isolated to stateless function flows.


### Added
- Prefect v3 integration for workflow orchestration
- `prefect_flows/device.py` - Prefect flows for device control
- `prefect_flows/orchestrator.py` - Remote flow execution functions
- `prefect_flows/README.md` - Setup and usage documentation

### Changed
- Added Prefect>=3.0.0 to dependencies
- REST API remains available but Prefect is now the recommended approach

### Notes
- Prefect provides better observability, retry logic, and async execution
- No breaking changes - REST API still functional for backward compatibility

## [2.0.0] - 2025-10-07

### 🎉 Major Release: Pip Package + Automatic Setup

**BREAKING CHANGES:**
- Complete transformation to pip-installable package
- Simplified installation and usage
- Archived all legacy installers

### 🆕 New Package Structure
- **pip installable**: `pip install git+https://github.com/...`
- **Command line tools**: `plate-resort-server`, `plate-resort-client`, `plate-resort-setup`
- **Professional package**: `plate_resort` Python package
- **Automatic setup**: System dependencies, USB permissions, API keys

### ✨ New Features
- One-line installation with automatic setup
- Command-line tools for server and client
- Automatic USB permissions and system configuration
- Professional Python package structure
- pip-based dependency management

### 🗂️ Archived Components
- Legacy bash installers (install.sh, update.sh)
- Standalone server/ and client/ directories
- Manual setup scripts and GUI components
- All deprecated files moved to archived/

### 🔧 Installation Methods
- **Recommended**: `curl ... | bash` (pip + auto-setup)
- **Manual**: `pip install ...` + `plate-resort-setup`
- **Development**: `pip install -e .` for local development

### 📦 Package Contents
- `plate_resort.core` - Motor control logic
- `plate_resort.server` - FastAPI REST API
- `plate_resort.client` - Client library and CLI
- `plate_resort.setup` - System setup automation
- `plate_resort.keygen` - API key management

### 🎯 Usage Simplification
- **Server**: `plate-resort-server` (instead of bash scripts)
- **Client**: `plate-resort-client --host IP` (consistent CLI)
- **Setup**: `plate-resort-setup` (automated system config)
- **Keys**: `plate-resort-keygen` (secure key generation)

### 🚀 Deployment Ready
- Works on any Python 3.8+ system
- Automatic Raspberry Pi detection and setup
- Professional dependency management
- Clean separation of server/client concerns

## [1.4.0] - 2025-10-07 (Archived)

### Removed
- Docker references and configuration
- Raspberry Pi specific deployment scripts

### Changed
- Simplified deployment approach
- Direct Python execution without containers

### Added
- CHANGELOG.md for tracking version history
- .gitignore file to prevent cache/temp files in repo

### Removed
- Redundant GUI implementations (gui.py, touchscreen_app.py, app.py)
- Redundant launcher scripts and duplicate implementations
- Duplicate test file from root directory (dxl_keyboard_test.py)
- Python cache directories (__pycache__)

### Changed
- Updated README.md to reflect cleaned project structure
- Simplified file organization following copilot-instructions

## [1.2.0] - 2025-09-10

### Added
- Disconnect and reconnect functionality to web API endpoints
- Connection control buttons in web interface (Disconnect/Reconnect)
- `is_connected()` method to PlateResort class for connection status checking
- Enhanced error handling for connection states
- Active hotel display logic improvements

### Fixed
- Emergency stop recovery - system no longer freezes after emergency stop
- Active hotel display now correctly shows current hotel (A, B, C, D, Home, Moving)
- Connection state management and status reporting

## [1.1.0] - 2025-09-10

### Added
- Professional web-based GUI with Bootstrap styling
- Fullscreen support optimized for 7" touchscreen (800x480)
- Live motor health monitoring with real-time updates
- Debug panel with live data logging
- Simplified deployment with automated dependency management
- Automated startup scripts and desktop integration
- Clean repo structure with organized test files

### Changed
- Migrated from Tkinter to Flask web-based GUI
- Moved all test files to `test_scripts/` directory
- Simplified deployment to single web GUI service
- Updated documentation for new architecture

### Removed
- Legacy GUI implementations (gui.py, touchscreen_app.py)
- Duplicate launcher scripts
- Emoji usage for professional lab environment

## [1.0.0] - 2025-09-10

### Added
- Initial PlateResort class with YAML configuration
- Dynamixel motor control with health monitoring
- Hotel position management (A, B, C, D)
- Emergency stop functionality
- Basic motor health reporting
- Raspberry Pi deployment scripts
- Raspberry Pi deployment scripts
