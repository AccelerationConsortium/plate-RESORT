# Changelog

All notable changes to this project will be documented in this file.

## [2.0.5] - 2025-10-16
## [2.0.6] - 2025-10-16
## [2.0.7] - 2025-10-16
## [2.0.9] - 2025-10-16

### Fixed
- `deploy.py` now inspects the underlying wrapped function (`flow.fn`) for source path printing to avoid `TypeError` when `inspect` is used directly on Prefect Flow objects.
- Updated sentinel to `DEPLOY_SCRIPT_VERSION=2.0.9` for remote verification.

### Notes
- If sentinel version <2.0.9 appears on target system after reinstall, stale artifact persistence is still occurring; force a refresh reinstall.

## [2.0.8] - 2025-10-16

### Added
- Sentinel comment `DEPLOY_SCRIPT_VERSION=2.0.8` to `workflows/deploy.py` to verify correct file fetched on remote systems.

### Fixed
- Addressed persistent stale deployment script issue by adding explicit marker and instructions for manual overwrite when legacy `flow.from_source` pattern appears.

### Notes
- If deployment prints `Deploying 9 flows...` immediately upon import or still references `/home/pi/plate_resort/core.py`, the old script is in use. Manually overwrite site-packages `deploy.py` or reinstall with commit hash containing the sentinel.


### Fixed
- Deployment failures due to Prefect attempting to read a non-existent script path (`/home/pi/plate_resort/core.py`). Added explicit module entrypoints in `deploy.py` so flows are resolved from `plate_resort.workflows.flows:<function>` rather than inferred file paths.

### Added
- Deployment output now prints each flow's entrypoint string along with source file.

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
