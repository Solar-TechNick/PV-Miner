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

The Home Assistant custom component is now fully implemented with the following structure:

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
```

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

When testing features, consider:

- LuxOS API connectivity and authentication
- Entity state updates and coordinator refresh cycles
- Service call execution and error handling
- Power profile switching and frequency adjustments
- Solar power logic and automatic adjustments
- Multi-miner priority-based power distribution
- Hardware failure scenarios (miner offline, network issues)
