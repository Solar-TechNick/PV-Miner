# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PV Miner is a Home Assistant Custom Component (HACS integration) for solar-powered Bitcoin mining control. It manages Antminer S21+, S19j Pro, and S19j Pro+ miners running LuxOS firmware, with automatic power adjustment based on available solar power.

**Key Technologies:**
- Home Assistant integration (Python 3.11+)
- LuxOS API communication via TCP (port 4028) and HTTP
- Async I/O using aiohttp
- HACS distribution

## Architecture

### Component Structure

The integration follows Home Assistant's standard architecture:

1. **luxos_api.py** - LuxOS API client
   - Communicates with miners via TCP socket (port 4028) for LuxOS API commands
   - HTTP session management for web-based authentication
   - Handles two communication methods:
     - TCP API (port 4028): Primary method for all miner commands
     - HTTP API: Legacy fallback and session creation
   - Dynamic profile discovery from miner capabilities

2. **\_\_init\_\_.py** - Integration setup and coordinator
   - `PVMinerCoordinator`: Manages data updates via DataUpdateCoordinator
   - Platform setup: sensor, switch, number, select
   - Service registration

3. **Platform Files**:
   - **sensor.py**: Hashrate, power, temperature, efficiency, pool status
   - **switch.py**: Main miner control + individual hashboard toggles (0, 1, 2)
   - **number.py**: Power limit and frequency offset controls
   - **select.py**: Power profile and solar mode selection with dynamic profile loading

4. **services.py** - Service implementations
   - set_power_profile: Apply predefined power profiles
   - set_power_limit: Dynamic power limiting
   - emergency_stop: Immediate shutdown
   - solar_max / eco_mode: Quick power presets
   - sleep_miner / wake_miner: Low-power modes
   - set_pool: Mining pool configuration

5. **config_flow.py** - UI configuration flow
   - IP address, credentials, scan intervals
   - Power limits and priority settings

### Key Concepts

**Dynamic Profile System**: Power profiles are no longer hardcoded. The integration discovers available profiles from the miner at runtime via LuxOS API. This allows support for different miner models with varying capabilities without code changes.

**Coordinator Pattern**: Home Assistant's DataUpdateCoordinator centralizes API calls, reducing redundant requests. All entities (sensors, switches) share the same data and update schedule.

**Priority-Based Power Distribution**: When multiple miners are configured, the integration can distribute available solar power based on configurable priority values.

**Individual Hashboard Control**: Each miner has 3 hashboards that can be independently enabled/disabled, allowing fine-grained power management.

## Development Commands

### Running Tests

Tests are located in two places:
- `PV-Miner/debug_files/__tests__/` - Integration tests with actual miner communication
- `test_scripts/` - Standalone test scripts for API validation

Run integration tests (requires pytest):
```bash
pytest PV-Miner/debug_files/__tests__/
```

Run standalone test scripts (require direct miner access):
```bash
python3 test_scripts/test_logon.py
python3 test_scripts/test_hashboard_control.py
python3 test_scripts/test_atm_control.py
```

**Note**: Test scripts expect miner at IP 192.168.1.210 with credentials admin/admin. Update MINER_IP, USERNAME, PASSWORD variables as needed.

### Testing in Home Assistant

For development testing:
1. Copy `PV-Miner/custom_components/pv_miner/` to your HA `custom_components/` directory
2. Restart Home Assistant
3. Add integration via UI: Settings → Integrations → Add Integration → "PV Miner"
4. Check logs: `tail -f /config/home-assistant.log | grep pv_miner`

### Installing via HACS (for users)

The integration is distributed via HACS:
1. Add custom repository: `https://github.com/Solar-TechNick/PV-Miner`
2. Install "PV Miner" integration
3. Restart Home Assistant

## Code Patterns

### LuxOS API Communication

Always use TCP API (port 4028) as the primary method:

```python
# LuxOS TCP API command format
cmd_data = {
    "command": "profiles",  # Command name
    "parameter": ""         # Optional parameter
}
```

Common commands:
- `stats`: General miner statistics
- `devs`: Device information and hashboard status
- `pools`: Mining pool configuration
- `profiles`: Get available power profiles
- `profileset`: Set active profile
- `ascset`: Control individual hashboards
- `power`: Power consumption data
- `temps`: Temperature readings
- `fans`: Fan speed data

### Session Management

LuxOS requires session creation for certain operations. The API client handles this automatically:

```python
async def _ensure_session(self):
    """Ensure we have a valid LuxOS session."""
    if not self._luxos_session_id:
        await self._create_luxos_session()
```

### Error Handling

All LuxOS API errors raise `LuxOSAPIError`. Always wrap API calls:

```python
try:
    result = await self._api.set_power_profile(profile_name)
except LuxOSAPIError as err:
    _LOGGER.error("Failed to set profile: %s", err)
    raise
```

### Entity Naming Convention

Entities follow the pattern:
- `sensor.{miner_name}_{metric}` - e.g., `sensor.antminer_s19j_pro_hashrate`
- `switch.{miner_name}_{control}` - e.g., `switch.antminer_s19j_pro_hashboard_0`
- `number.{miner_name}_{setting}` - e.g., `number.antminer_s19j_pro_power_limit`
- `select.{miner_name}_{selector}` - e.g., `select.antminer_s19j_pro_power_profile`

## Important Implementation Notes

1. **Profile Discovery**: Never hardcode power profiles. Always fetch them dynamically using the `profiles` command. Different miner models have different available profiles.

2. **Hashboard Indexing**: Hashboards are 0-indexed (0, 1, 2). LuxOS uses the `ascset` command format: `ascset|0,disable,ASIC` where 0 is the board number.

3. **Power Monitoring**: The integration tracks power consumption through multiple data sources (stats, power command) for accuracy and redundancy.

4. **Async Everything**: All I/O operations must be async. Use `asyncio.to_thread()` for synchronous socket operations.

5. **Update Intervals**: Default scan interval is 30s. Solar scan interval is 600s (10 minutes). These are configurable per integration instance.

6. **Service Target**: Services target the main miner switch entity (`switch.{miner_name}_miner`), which then controls the entire miner or coordinates with other entities.

## Configuration Files

Example configurations are provided in YAML files:
- `pv_miner_automations.yaml` - Solar-based automation examples with 10-step power scaling
- `pv_miner_helpers.yaml` - Helper entities for progressive hashboard control
- `pv_miner_dashboard.yaml` - Desktop dashboard layout
- `pv_miner_mobile_dashboard.yaml` - Mobile-optimized dashboard

These are reference implementations showing integration usage patterns.

## Localization

Translations in `custom_components/pv_miner/translations/`:
- `de.json` - German (primary)
- `en.json` - English

When adding new config options or services, update both translation files.

## Hardware Context

**Supported Miners**: Antminer S21+, S19j Pro, S19j Pro+ (LuxOS firmware required)
**Power Ranges**: Typically 500W (minimum) to 4200W (maximum) depending on model
**Communication**: Local network only, no cloud dependency
**API Ports**: TCP 4028 (LuxOS API), HTTP 80/443 (web interface)

## Common Pitfalls

1. **Socket Timeout**: LuxOS TCP connections can be slow. Always use 10-15s timeouts.
2. **Response Format**: LuxOS responses end with null byte (`\x00`). Strip before JSON parsing.
3. **Status Validation**: Check `STATUS` section in responses. `"STATUS": "S"` = success, `"E"` = error.
4. **Profile Names**: Profile names returned by API may not match display names. Store mapping.
5. **Hashboard State**: Disabled hashboards still report temperature. Check enable state separately.
