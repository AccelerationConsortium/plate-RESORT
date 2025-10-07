# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-10-07

### Major Architecture Change
- **BREAKING**: Migrated from GUI-based to server-client architecture
- **NEW**: FastAPI REST API server with 9 endpoints
- **NEW**: Python client library with CLI interface
- **NEW**: Network-based control from any machine

### Added
- FastAPI server with automatic API documentation
- Thread-safe motor control wrapper
- API key authentication
- Python client library (`client/client.py`)
- Smart installer for fresh and existing Pi installations
- Update script for easy maintenance

### Removed
- Web GUI interface (archived)
- Docker dependencies and configuration
- Desktop integration files
- Old setup scripts (archived)

### Changed
- One-line installer now handles existing installations
- Core motor control unchanged (backward compatible)
- Configuration file format unchanged
- Test scripts preserved for hardware validation

### Migration Guide
- Replace GUI usage with client commands
- Server API available at `http://PI_IP:8000/docs`
- Use `./server/run_server.sh` instead of web GUI
- Install client with `pip install requests`

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
