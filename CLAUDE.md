# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PV-Miner is a Home Assistant integration for sustainable Bitcoin mining using solar power. The project enables automated control of Antminer devices (S21+, S19j Pro, S19j Pro+) based on solar power availability and battery status.

## Architecture

This project is designed as a Home Assistant integration with the following key components:

### Communication Protocols
- **MQTT**: Primary communication for real-time solar/battery data
- **REST API**: Miner status and control endpoints
- **Home Assistant Integration**: Custom component for HA ecosystem

### Hardware Integration
- **Miners**: Antminer S21+, S19j Pro, S19j Pro+ via REST API
- **Solar System**: MPPT charge controllers (Victron, EPEver) via MQTT
- **Controllers**: Raspberry Pi, Home Assistant Yellow, ESP32

### Expected Data Flow
1. Solar panels → MPPT controller → MQTT topics (`solar/pv_power`, `solar/battery_soc`)
2. Miners → REST endpoints (`/api/status`) → Home Assistant sensors
3. Home Assistant automations → Miner control based on solar/battery status

## Development Setup

The Home Assistant custom component is fully implemented and **connection-tested** with the following structure:

```
custom_components/pv_miner/    # Home Assistant custom component
├── __init__.py                # Component initialization and coordinator
├── manifest.json             # HA component metadata
├── config_flow.py           # Configuration UI with multi-step setup
├── sensor.py                # Sensor entities (hashrate, temperature, power, efficiency)
├── switch.py                # Switch entities (miner control, hashboard control)
├── number.py                # Number entities (power limits, frequency, solar input)
├── select.py                # Select entities (power profiles, solar modes)
├── services.py              # Service definitions and handlers
├── luxos_api.py             # LuxOS API client implementation
├── const.py                 # Constants, profiles, and configuration
└── translations/            # Internationalization files
    ├── en.json              # English translations
    └── de.json              # German translations

__tests__/                   # Test suite
├── test_luxos_api.py        # API client tests
└── test_config_flow.py      # Configuration flow tests

debug_connection.py          # Full aiohttp-based connection debugging
simple_debug.py              # Dependency-free connection testing  
test_api_direct.py           # Direct LuxOS API testing
```

## Version History

### v1.0.9 (Current) - Complete Sensor Data Fix 🎯

- ✅ **CRITICAL**: Fixed all "Unknown" sensor values in Home Assistant
- ✅ **Power Consumption**: 1851W from dedicated power command
- ✅ **Temperature Sensors**: All working - main (49°C) + 3 hashboards (49°C, 48°C, 48°C)
- ✅ **Fan Speed**: 2490 RPM average from all 4 fans
- ✅ **Efficiency**: 19.6 J/TH calculated from real power/hashrate data
- ✅ **Data Sources**: Enhanced coordinator with power, temps, fans commands
- ✅ **Verified**: All sensor readings confirmed accurate on S21+

### v1.0.8 - Complete LuxOS Integration Fix 🎉

- ✅ **Main Miner Switch**: Fixed using curtail sleep/wakeup commands
- ✅ **Profile System**: Real LuxOS profiles (default 710MHz, 310MHz eco mode)
- ✅ **Hashboard Switches**: Individual board control (0, 1, 2) working
- ✅ **Session Management**: Proper LuxOS login with session_id authentication
- ✅ **All Switch Operations**: Complete ON/OFF functionality

### v1.0.7 - LuxOS Session Management Fix

- ✅ **Hashboard Commands**: Fixed enableboard/disableboard with session_id,board_id
- ✅ **Session Creation**: Automatic logon with username,password
- ✅ **Parameter Format**: Correct session handling for all board commands

### v1.0.6 - Complete LuxOS API Rewrite

- ✅ **Official LuxOS Implementation**: Based on official documentation
- ✅ **TCP API (Port 4028)**: Primary method with HTTP fallback
- ✅ **Connection Issues**: Resolved persistent "No valid API endpoint" errors

### v1.0.5 - Password Compatibility Fix

- ✅ **Authentication**: Changed default password to `root` for S21+ compatibility
- ✅ **Connection**: Resolved Home Assistant context issues

### v1.0.1-1.0.4 - HACS and Initial Fixes

- ✅ **HACS Compatibility**: Fixed validation issues
- ✅ **Initial Release**: Complete Home Assistant custom component

## Configuration

Based on the README, the integration expects:

### Home Assistant Configuration
- REST sensors for miner data (hashrate, temperature, power consumption)
- MQTT sensors for solar data (PV power, battery SOC)
- Automations for start/stop logic based on solar conditions

### MQTT Topics Expected
- `solar/pv_power` - Current solar panel output (W)
- `solar/battery_soc` - Battery state of charge (%)
- Additional topics for temperature, charge controller status

### Miner API Endpoints Expected
- `GET /api/status` - Current miner status (hashrate, temperature, power)
- `POST /api/start` - Start mining
- `POST /api/stop` - Stop mining

## Language and Documentation

This project uses German language for user-facing documentation and comments. Technical code should follow English conventions, but user interfaces and documentation should be in German to match the target audience.

## Features Implemented ✅ ALL WORKING

### Core Integration Features (v1.0.9)

- ✅ **Manual Configuration**: Step-by-step setup with IP, credentials, power limits, and update intervals
- ✅ **Complete Real-time Monitoring**: 
  - Hashrate: 94.2 TH/s (from stats.GHS_5s)
  - Power Consumption: 1851W (from power command)
  - Temperature: 49°C main + individual hashboards (49°C, 48°C, 48°C)
  - Fan Speed: 2490 RPM average (from fans command)
  - Efficiency: 19.6 J/TH (calculated from power/hashrate)
  - Uptime: Real seconds (from stats.Elapsed)
  - Mining Pool: NiceHash URL (from pools data)

### Control Features (v1.0.8)

- ✅ **Main Miner Switch**: ON/OFF via curtail sleep (25W) / wakeup commands
- ✅ **Individual Hashboard Control**: Enable/disable boards 0, 1, 2 independently
- ✅ **Real Profile System**: 
  - "default" profile: 710MHz, 238.9 TH/s, 5908W (performance mode)
  - "310MHz" profile: 310MHz, 104.3 TH/s, 2136W (eco mode)
  - Dynamic profile switching with real LuxOS profiles
- ✅ **Session Management**: Automatic LuxOS authentication with session_id handling
- ✅ **Pool Management**: Mining pool monitoring and status
- ✅ **Service Calls**: All service calls working with proper session authentication

### Advanced Features (Ready for Solar Integration)

- ✅ **Power-based Automation**: Real 1851W power consumption data for solar automation
- ✅ **Temperature-based Control**: Individual hashboard temperature monitoring
- ✅ **Performance Optimization**: Real efficiency tracking (19.6 J/TH)
- 🔄 **Solar Integration**: Ready for automatic power adjustment based on real consumption data
- 🔄 **Multi-miner Management**: Framework ready for multiple miner control

### API Integration

- **LuxOS Authentication**: Session-based login with error handling
- **Comprehensive Commands**: Stats, device info, temperature, pool management, frequency control
- **Error Handling**: Retry logic, connection timeouts, and notification system
- **Async Operations**: Full async/await support for Home Assistant compatibility

### User Interface

- **Multi-language Support**: English and German translations
- **Configuration Options**: Runtime configuration changes through HA options flow
- **Entity Organization**: Logical grouping of sensors, switches, numbers, and selects per miner
- **State Management**: Proper state updates and coordinator refresh handling

## Testing and Development

### Running Tests

```bash
# Install test dependencies (if needed)
pip install pytest pytest-asyncio

# Run tests
python -m pytest __tests__/

# Run with coverage (optional)
python -m pytest __tests__/ --cov=custom_components/pv_miner

# Run specific test files
python test_api_direct.py
python debug_connection.py <miner_ip>
python simple_debug.py <miner_ip>
```

### Development Environment
- Python 3.11+ (Home Assistant requirement)
- aiohttp>=3.8.0 (only external dependency from manifest.json)
- No additional build tools required - this is a pure Python Home Assistant integration

### Development Commands

- **Install Integration**: Copy `custom_components/pv_miner` to HA custom_components directory
- **Restart HA**: Required after code changes (Developer Tools → Restart)
- **Debug Logging**: Enable debug logging for `custom_components.pv_miner` domain in configuration.yaml
- **API Testing**: Use `test_connection()` method to verify miner connectivity
- **Reload Integration**: Developer Tools → YAML → All YAML configuration (for config changes)

### Code Linting and Type Checking
No specific linting configuration found. Standard Python tools can be used:
```bash
# Optional linting (not configured in project)
python -m flake8 custom_components/pv_miner/
python -m mypy custom_components/pv_miner/
python -m black custom_components/pv_miner/
```

### Git Workflow - IMPORTANT

**ALWAYS use proper versioning when committing to GitHub:**

```bash
# 1. Update version in manifest.json
# Edit custom_components/pv_miner/manifest.json - increment version field

# 2. Commit changes with conventional commits
git add .
git commit -m "fix: description of bug fix" 
# OR
git commit -m "feat: description of new feature"
# OR  
git commit -m "docs: update documentation"

# 3. Create version tag
git tag -a v1.0.X -m "Version 1.0.X release notes"

# 4. Push with versioning
git push origin main && git push origin v1.0.X

# 5. Create GitHub release (if gh CLI available)
gh release create v1.0.X --title "Version 1.0.X" --notes "Release notes" --latest
```

**Version Numbering:**
- **Patch (1.0.X)**: Bug fixes, minor improvements
- **Minor (1.X.0)**: New features, API additions
- **Major (X.0.0)**: Breaking changes, major rework

**Never push without proper versioning and release tags!**

## Integration Testing

### Connection Testing
The integration now uses **CGMiner API on port 4028** as the primary connection method:

```bash
# Test basic connectivity 
python3 simple_debug.py 192.168.1.212

# Test full API functionality
python3 test_api_direct.py

# Debug with external dependencies
python3 debug_connection.py 192.168.1.212
```

### Verified Working Configuration
**Tested on Antminer S21+ (192.168.1.212) with LuxOS 2025.7.10.152155:**
- ✅ **Complete Integration**: All functionality working perfectly
- ✅ **Real-time Sensors**: Power (1851W), Temperature (49°C), Fan Speed (2490 RPM)
- ✅ **Hashrate Monitoring**: 94.2 TH/s with efficiency 19.6 J/TH
- ✅ **Individual Hashboards**: All 3 boards (49°C, 48°C, 48°C) with independent control
- ✅ **Switch Operations**: Main switch (curtail sleep/wakeup) + hashboard switches working
- ✅ **Profile System**: Real profiles (default 710MHz, 310MHz eco) with switching
- ✅ **Pool Management**: NiceHash connection monitored and controllable
- ✅ **Session Management**: Automatic LuxOS authentication and session handling

### Authentication
- **Default Username**: `root`
- **Default Password**: `root` (changed from `rootz` in v1.0.2)
- **API Method**: Direct TCP connection to CGMiner API
- **Fallback**: Web API for advanced LuxOS features

### Testing Checklist
When testing features, verify:

- ✅ **Complete LuxOS API integration** via port 4028 (TCP) and HTTP fallback
- ✅ **All sensor data** (power, temperature, fan speed, efficiency, hashrate)
- ✅ **Switch operations** (main miner curtail + individual hashboard control)
- ✅ **Profile system** (default 710MHz, 310MHz eco mode switching)
- ✅ **Session management** (automatic LuxOS logon and authentication)
- ✅ **Entity state updates** and coordinator refresh cycles (power, temps, fans commands)
- ✅ **Service call execution** and error handling
- ✅ **Individual hashboard control** (3 boards: ASC 0, 1, 2)
- ✅ **Real-time monitoring** (all sensors displaying real values, not "Unknown")
- **Solar power logic** and automatic adjustments (ready for implementation)
- **Multi-miner priority-based** power distribution (ready for implementation)
- **Hardware failure scenarios** (miner offline, network issues)

### Known Working Commands
**LuxOS API Commands (Port 4028 TCP + Session Authentication):**
- `stats` - Complete miner statistics (hashrate, temperatures, fan speeds)
- `devs` - Individual hashboard status and temperatures  
- `pools` - Mining pool connection and share statistics
- `power` - Real-time power consumption (1851W)
- `temps` - Detailed temperature sensors for all boards
- `fans` - Fan speeds and control information (4 fans)
- `version` - LuxOS version and miner identification
- `summary` - Overall miner status summary
- `session` - Get current session information
- `logon` - Create authentication session (username,password)
- `curtail` - Sleep/wakeup commands for main miner control
- `enableboard` / `disableboard` - Individual hashboard control (session_id,board_id)
- `profileget` / `profileset` - Profile management (session_id,profile_name)

### Troubleshooting
**If Issues Occur (Should Not Happen in v1.0.9+):**
1. **Sensor "Unknown" Values**: Update to v1.0.9+ (fixed sensor data parsing)
2. **Switch Not Working**: Update to v1.0.8+ (fixed with curtail commands and session management)
3. **Profile Dropdown Empty**: Update to v1.0.8+ (fixed with real LuxOS profiles)
4. **Connection Issues**: 
   - Verify port 4028 is accessible (`telnet 192.168.1.212 4028`)
   - Check credentials are `root`/`root`
   - Run debug scripts to identify specific connection problems
   - Ensure LuxOS firmware is installed and API is enabled
5. **Permission Issues**: Ensure LuxOS allows API access (should be enabled by default)

**Integration Status Check:**
- All features ✅ **WORKING** as of v1.0.9
- Complete sensor data ✅ **WORKING** (power, temp, fans, efficiency)  
- All switches ✅ **WORKING** (main miner + hashboards)
- Profile system ✅ **WORKING** (real LuxOS profiles)
- Session management ✅ **WORKING** (automatic authentication)

