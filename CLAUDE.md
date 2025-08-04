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

### v1.0.2 (Current) - Connection Fix

- ✅ **CRITICAL**: Fixed "Cannot connect to miner" issue
- ✅ **CGMiner API**: Uses port 4028 for reliable connection
- ✅ **Authentication**: Changed default password to `root`
- ✅ **Debugging**: Added comprehensive debug tools
- ✅ **Verified**: Tested on S21+ with LuxOS 2025.7.10.152155

### v1.0.1 - HACS Improvements

- ✅ **HACS**: Fixed validation (7/8 checks passing)
- ✅ **Repository**: Added topics and GitHub templates
- ✅ **API**: Enhanced error handling and logging

### v1.0.0 - Initial Release

- ✅ **Integration**: Complete Home Assistant custom component
- ✅ **Features**: All planned functionality implemented
- ✅ **Languages**: English and German translations

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

## Features Implemented

### Core Integration Features

- **Manual Configuration**: Step-by-step setup with IP, credentials, power limits, and update intervals
- **Real-time Monitoring**: Hashrate, power consumption, temperature, fan speed, efficiency, uptime
- **Individual Control**: Main miner switch and individual hashboard switches (0, 1, 2)
- **Power Management**: Power limit controls, frequency adjustment (-16 to +4), and solar power input
- **Profile System**: Predefined profiles (Max Power, Balanced, Ultra Eco, Night modes, Standby)
- **Solar Integration**: Manual solar power input with automatic power adjustment logic
- **Pool Management**: Mining pool switching and configuration
- **Service Calls**: Emergency stop, solar max, eco mode, power profile switching

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
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest __tests__/

# Run with coverage
pytest __tests__/ --cov=custom_components/pv_miner
```

### Development Commands

- **Install Integration**: Copy `custom_components/pv_miner` to HA custom_components directory
- **Restart HA**: Required after code changes
- **Debug Logging**: Enable debug logging for `custom_components.pv_miner` domain
- **API Testing**: Use `test_connection()` method to verify miner connectivity

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
- ✅ **CGMiner API (Port 4028)**: Full functionality confirmed
- ✅ **Real-time Data**: Hashrate 239.4 TH/s, 3 hashboards, temperatures
- ✅ **Device Status**: All boards alive and operational
- ✅ **Pool Management**: NiceHash connection active
- ❌ **Web API Endpoints**: Return 404 (bypassed with TCP API)

### Authentication
- **Default Username**: `root`
- **Default Password**: `root` (changed from `rootz` in v1.0.2)
- **API Method**: Direct TCP connection to CGMiner API
- **Fallback**: Web API for advanced LuxOS features

### Testing Checklist
When testing features, verify:

- **CGMiner API connectivity** via port 4028 (primary method)
- **Entity state updates** and coordinator refresh cycles
- **Service call execution** and error handling
- **Individual hashboard control** (3 boards: ASC 0, 1, 2)
- **Real-time monitoring** (hashrate, temperature, power)
- **Solar power logic** and automatic adjustments
- **Multi-miner priority-based** power distribution
- **Hardware failure scenarios** (miner offline, network issues)

### Known Working Commands
**CGMiner API Commands (Port 4028):**
- `stats` - Complete miner statistics and performance data
- `devs` - Individual hashboard status and temperatures  
- `pools` - Mining pool connection and share statistics
- `version` - LuxOS version and miner identification
- `summary` - Overall miner status summary

### Troubleshooting
**Connection Issues:**
1. Verify port 4028 is accessible (`telnet 192.168.1.212 4028`)
2. Check credentials are `root`/`root` (not `rootz`)
3. Run debug scripts to identify specific connection problems
4. Ensure LuxOS firmware is installed and CGMiner API is enabled

