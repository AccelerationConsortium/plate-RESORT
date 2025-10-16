# Changelog

All notable changes to this project will be documented in this file.

## [2.0.1] - 2025-10-15

### Fixed
- Resolved Prefect Cloud flow crash (SignatureMismatchError) by removing extraneous parameters from remote `connect` deployment submission.
- Updated `orchestrator.connect()` to call `run_deployment(name="connect/connect")` without a parameter dict (method flow expects only `self`).

### Notes
- Other flows (activate-hotel, move-to-angle, etc.) retain parameters matching their method signatures.
- No breaking API changes; remote client now successfully submits `connect` without crashing.

## [2.1.0] - 2025-01-XX

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
