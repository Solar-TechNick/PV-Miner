# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PV-Miner is a Home Assistant custom integration for solar-powered Bitcoin mining. Controls Antminer devices (S21+, S19j Pro, S19j Pro+) running LuxOS firmware via their native API, enabling automated power management based on solar availability.

## Architecture Overview

**Integration Type**: Home Assistant custom component (local polling device integration)

**Communication Layer**:
- **Primary**: LuxOS TCP API (port 4028) - Direct socket communication with JSON protocol
- **Fallback**: LuxOS HTTP API (port 8080) - REST endpoints for advanced features
- **Authentication**: Session-based (logon command creates session_id used in subsequent commands)

**Core Components**:
1. **luxos_api.py**: Dual-protocol API client (TCP primary, HTTP fallback)
2. **Coordinator Pattern**: DataUpdateCoordinator in `__init__.py` manages polling and state updates
3. **Multi-platform Entities**: sensor.py (monitoring), switch.py (control), select.py (profiles), number.py (limits)
4. **Multi-step Config Flow**: config_flow.py handles connection → power settings → intervals
5. **Service Layer**: services.py exposes HA service calls for automation integration

**Data Flow Architecture**:
- Coordinator polls multiple LuxOS commands concurrently: `stats`, `devs`, `pools`, `power`, `temps`, `fans`
- Entity classes subscribe to coordinator and extract their specific data from combined response
- Session management is automatic - API client handles logon and session_id injection transparently
- Commands requiring authentication (curtail, profileset, enableboard/disableboard) use session_id parameter

## Key Architectural Patterns

**LuxOS API Dual-Protocol Design** (luxos_api.py):

- `_tcp_command()`: Primary method using sync sockets wrapped in `run_in_executor()` to avoid blocking event loop
- `_http_command()`: Fallback using aiohttp for HTTP/8080 endpoints
- `_execute_command()`: Intelligent router that tries TCP first, falls back to HTTP on failure
- Session management: `_ensure_session()` automatically calls `logon` command and caches session_id
- All authenticated commands inject session_id parameter: `{"command": "profileset", "parameter": "session_id,profile_name"}`

**Coordinator Data Collection Pattern** (\_\_init\_\_.py):

```python
# Coordinator fetches multiple commands in parallel for efficiency
async def _async_update_data():
    stats = await api.get_stats()      # Hashrate, uptime
    devs = await api.get_devs()        # Per-hashboard data
    pools = await api.get_pools()      # Mining pool info
    power = await api._execute_command("power", "")   # Real power consumption
    temps = await api._execute_command("temps", "")   # Detailed temperatures
    fans = await api._execute_command("fans", "")     # Fan speeds
    return {"stats": stats, "devs": devs, ...}  # Combined data for all entities
```

**Entity Data Extraction Pattern** (sensor.py, switch.py, etc):

- Each entity subscribes to coordinator via `@property coordinator_data`
- Entities extract only their needed data from coordinator's combined response
- Example: Power sensor reads `coordinator.data["power"][0]["POWER"][0]["Power"]`
- Example: Temperature sensor averages values from `coordinator.data["temps"]`

**Multi-Step Configuration Flow** (config_flow.py):

1. `async_step_user()`: Connection details (host, username, password)
2. `async_step_power()`: Power limits (min/max watts, priority)
3. `async_step_intervals()`: Update intervals (miner scan, solar scan)
4. Each step validates and stores data, final step creates config entry

## Development Commands

### Testing and Debugging

```bash
# Test miner connectivity (no dependencies)
python3 simple_debug.py <miner_ip>

# Test full API functionality
python3 test_api_direct.py

# Debug with aiohttp (external dependencies)
python3 debug_connection.py <miner_ip>

# Run integration tests
python3 -m pytest __tests__/

# Run specific test file
python3 -m pytest __tests__/test_luxos_api.py

# Test with coverage (if pytest-cov installed)
python3 -m pytest __tests__/ --cov=custom_components/pv_miner
```

### Home Assistant Development Workflow

```bash
# 1. Copy integration to HA custom_components directory
cp -r custom_components/pv_miner /path/to/homeassistant/custom_components/

# 2. Enable debug logging in configuration.yaml
# logger:
#   default: info
#   logs:
#     custom_components.pv_miner: debug

# 3. Restart Home Assistant (required after code changes)
# Developer Tools → Restart

# 4. Reload integration (for config changes only, not code changes)
# Developer Tools → YAML → Reload all YAML configuration
```

### Git Versioning Workflow

**IMPORTANT**: Always update manifest.json version and create tags when committing:

```bash
# 1. Edit manifest.json - increment "version" field (e.g., "1.0.14" → "1.0.15")

# 2. Commit with conventional commit message
git add .
git commit -m "fix: description"      # Bug fixes (1.0.X)
# OR
git commit -m "feat: description"     # New features (1.X.0)
# OR
git commit -m "docs: description"     # Documentation only

# 3. Create and push version tag
git tag -a v1.0.15 -m "Release notes here"
git push origin main --tags

# 4. Create GitHub release (if gh CLI available)
gh release create v1.0.15 --title "v1.0.15" --notes "Release notes" --latest
```

## Important Implementation Details

**Current Version**: 1.0.25 (see manifest.json)

**Language Convention**: German for user-facing strings (translations/de.json, translations/en.json), English for code and technical documentation.

**Supported Hardware**:

- Antminer S21+, S19j Pro, S19j Pro+ running LuxOS firmware
- Default credentials: username `root`, password `root`
- Test miners: 192.168.1.210, 192.168.1.211, 192.168.1.212

**Key LuxOS Commands** (all via port 4028 TCP):

- Monitoring: `stats`, `devs`, `pools`, `power`, `temps`, `fans`, `version`, `summary`
- Control (require session_id): `curtail` (sleep/wakeup), `enableboard`, `disableboard`, `profileget`, `profileset`
- Authentication: `logon` (creates session), `session` (get current session info)

## Common Debugging Scenarios

**Connection Issues**:

1. Verify miner is reachable: `telnet <miner_ip> 4028`
2. Check credentials (default: root/root)
3. Run debug script: `python3 simple_debug.py <miner_ip>`
4. Check Home Assistant logs: Settings → System → Logs, filter by `pv_miner`

**Sensor Shows "Unknown"**:

- Fixed in v1.0.9+. Update manifest.json version if needed.
- Verify coordinator is fetching `power`, `temps`, `fans` commands successfully in logs.

**Switch Not Responding**:

- Ensure miner supports LuxOS curtail commands (S21+, S19j Pro with LuxOS firmware)
- Check session management in logs - should see "LuxOS session created" messages
- Verify hashboard commands use correct format: `session_id,board_id` (e.g., `123abc,0`)

**Profile Dropdown Empty**:

- Profiles are loaded dynamically from miner on first connection
- Check logs for `profileget` command results
- Ensure miner has LuxOS profiles configured (use LuxOS web interface to verify)

## Diagnostic Tools

**test_hashboard_simple.py**: Standalone diagnostic tool for testing LuxOS hashboard control directly (bypasses Home Assistant). Useful for diagnosing firmware issues. Usage:
```bash
python3 test_hashboard_simple.py
```
Features:
- Tests basic miner connection
- Gets session ID and ATM status
- Shows current hashboard states
- Interactive board enable/disable testing
- Verifies if commands actually change board state

**fetch_ha_logs.py**: Fetches Home Assistant logs via REST API when SSH is not available. Requires a long-lived access token from HA.

## Recent Version History

- **v1.0.25**: Added hashboard control verification and LuxOS firmware limitation detection
- **v1.0.24**: Added detailed diagnostic logging for hashboard control operations
- **v1.0.23**: Added connection logging (shows miner IP on startup)
- **v1.0.22**: Comprehensive "already active" error suppression at all API layers
- **v1.0.21**: Initial error handling improvements for "already active" errors
- **v1.0.20**: Auto-wake miner before hashboard control operations
- **v1.0.19**: HACS validation fixes and repository restructuring

## Error Handling Best Practices

**"Miner is already active" errors**: This is expected behavior when calling resume_mining() on an active miner. As of v1.0.22, these are properly suppressed at all layers:
- TCP API layer: Logs as DEBUG instead of ERROR
- HTTP API layer: Logs as DEBUG instead of ERROR
- Execute command layer: Logs as DEBUG instead of ERROR
- Curtail command layer: Skips WARNING logs
- Switch layer: Gracefully handles the response

**Hashboard control when miner is asleep**: As of v1.0.20, hashboard switches automatically call resume_mining() before enable/disable operations to prevent "curtail mode is idle or sleep" errors.

**Hashboard control not working (v1.0.25)**:

**CONFIRMED BUG**: LuxOS firmware 2025.10.15.191043 has non-functional `enableboard`/`disableboard` commands. Extensive testing confirms:
- Commands return success ("Board enabled"/"Board disabled") with STATUS='S'
- Board state never changes (remains Enabled=Y regardless of command)
- Issue persists even with ATM disabled
- Issue persists even with Home Assistant completely off
- Tested over 30+ seconds with no state change
- Affects all hashboards regardless of their working status

**Testing performed**: Direct TCP API calls to miner at 192.168.1.210, bypassing all integration layers. Commands accepted but have zero effect on hardware.

**Root cause**: This is a LuxOS firmware bug/limitation, NOT an integration issue. The hardware reports the command succeeded but doesn't execute it.

**Recommended alternatives for solar following**:
1. **Power profile switching** (Best option): Switch between frequency profiles (e.g., "260MHz" high power, "220MHz" medium, "180MHz" low) - this DOES work and provides granular power control
2. **Full miner on/off**: Use curtail sleep/wake to turn entire miner on/off - this works but is all-or-nothing
3. **Contact LuxOS support**: Report this bug and request a firmware fix

The integration now verifies board state changes after commands and logs warnings when firmware doesn't support the feature (v1.0.25).

## Future Development Areas

Based on todo.md, planned features include:

- **Solar Integration**: Automatic power adjustment based on available solar power (entities ready, automation logic pending)
- **Multi-miner Management**: Priority-based power distribution across multiple miners (framework exists, needs coordination logic)
- **Sun Curve Mode**: Automatic power adjustment following daily solar patterns (UI exists, calculation logic needed)
- **Temperature Protection**: Auto-underclock at configurable temperature thresholds (sensors ready, action logic pending)
