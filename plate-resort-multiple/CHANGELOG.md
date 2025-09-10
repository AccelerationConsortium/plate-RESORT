# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2025-09-10

### Added
- CHANGELOG.md for tracking version history
- .gitignore file to prevent cache/temp files in repo

### Removed
- Redundant GUI implementations (gui.py, touchscreen_app.py, app.py)
- Redundant launcher scripts (docker-launch.sh, launch.sh, start-gui-docker.sh)
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
- Docker-first deployment with docker-compose
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
- Docker containerization
- Raspberry Pi deployment scripts
