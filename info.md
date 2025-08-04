# PV Miner - Solar Bitcoin Mining Integration

[![HACS](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Solar-TechNick/PV-Miner.svg)](https://github.com/Solar-TechNick/PV-Miner/releases)

A comprehensive Home Assistant integration for solar-powered Bitcoin mining with Antminer S21+, S19j Pro, and S19j Pro+ using LuxOS firmware.

## Features

- **Real-time Monitoring**: Hashrate, power consumption, temperature, efficiency
- **Individual Control**: Main miner and individual hashboard switches
- **Power Profiles**: Max Power, Balanced, Eco, Night modes, Standby
- **Solar Integration**: Automatic power adjustment based on available solar power
- **Service Calls**: Emergency stop, solar max, eco mode, pool switching
- **Multi-language**: English and German translations

## Supported Hardware

- Antminer S21+, S19j Pro, S19j Pro+ with LuxOS firmware
- Any solar panel setup with Home Assistant integration
- MPPT charge controllers (Victron, EPEver, etc.)

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add `https://github.com/Solar-TechNick/PV-Miner` as an Integration
6. Find "PV Miner" in HACS and install it
7. Restart Home Assistant

### Manual Installation

1. Download this repository
2. Copy the `custom_components/pv_miner` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "PV Miner"
4. Enter your miner details:
   - IP Address (e.g., 192.168.1.210)
   - Miner Name (e.g., "Antminer S19j Pro+")
   - Username (default: "root")
   - Password (default: "root")
5. Configure power limits and priorities
6. Set update intervals

## Documentation

For detailed setup instructions, automation examples, and troubleshooting, see the [complete documentation](https://github.com/Solar-TechNick/PV-Miner/blob/main/README_INTEGRATION.md).

## Support

- [Issues](https://github.com/Solar-TechNick/PV-Miner/issues)
- [Discussions](https://github.com/Solar-TechNick/PV-Miner/discussions)
- [LuxOS API Documentation](https://docs.luxor.tech/)