# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PV-Miner is a Home Assistant custom integration for solar-powered Bitcoin mining. It controls Antminer S21+, S19j Pro, and S19j Pro+ devices running **LuxOS firmware** over their native API, exposing entities and services that let HA automations follow available solar power.

User-facing strings are German (translations/de.json + en.json). Code, comments, and commits are English. Current version is tracked in [custom_components/pv_miner/manifest.json](custom_components/pv_miner/manifest.json) — bump it in every commit (see Git Versioning Workflow).

## Architecture

**Integration type**: HA `device` integration, `local_polling` iot_class. One config entry per miner.

### Communication layer — [custom_components/pv_miner/luxos_api.py](custom_components/pv_miner/luxos_api.py)

Dual-protocol client. **Not Luxor's cloud REST API** — this talks to the miner directly on the LAN.

- `_tcp_command()` — primary path. Raw socket on **port 4028** with newline-delimited JSON, wrapped in `loop.run_in_executor()` so the sync socket call doesn't block HA's event loop.
- `_http_command()` — fallback on **port 8080** via `aiohttp`.
- `_execute_command()` — tries TCP first, falls back to HTTP on failure.
- `_ensure_session()` — calls `logon` once and caches the `session_id`. Any authenticated command (`curtail`, `profileset`, `enableboard`, `disableboard`, `atmset`) gets the session_id prepended to its `parameter` string, e.g. `"session_id,profile_name"`.

When editing this file, preserve the executor-wrap pattern: doing synchronous socket I/O on the event loop will hang HA.

### Coordinator pattern — [custom_components/pv_miner/\_\_init\_\_.py](custom_components/pv_miner/__init__.py)

A single `DataUpdateCoordinator` per miner fans out concurrent LuxOS commands per poll: `stats`, `devs`, `pools`, `power`, `temps`, `fans`. All entity platforms (`sensor`, `switch`, `select`, `number`) subscribe to this coordinator and extract their slice from the combined dict — e.g. `coordinator.data["power"][0]["POWER"][0]["Power"]`. Add new data sources here, not in the entities.

### Solar auto-control loop — [custom_components/pv_miner/solar_coordinator.py](custom_components/pv_miner/solar_coordinator.py)

Added in v1.0.30. Built-in loop that reads a HA power-meter sensor (e.g. `sensor.pro3em_total_active_power`) and walks the LuxOS profile ladder up/down to follow available solar. v1.0.31 added auto sleep (`curtail` to sleep when solar < ~100W) and wake when solar returns. This makes the YAML automations in [automations/](automations/) optional — they remain as an alternative for users who want the logic in HA rather than in the integration.

### Entity platforms

`sensor.py` (monitoring), `switch.py` (mining on/off, profile presets), `select.py` (profile dropdown — populated dynamically from `profileget`), `number.py` (power limits). Hashboard-per-board switches were **removed in v1.0.26** — see "LuxOS firmware bug" below.

### Config flow — [custom_components/pv_miner/config_flow.py](custom_components/pv_miner/config_flow.py)

Three steps: `async_step_user` (host/user/pass) → `async_step_power` (min/max W, priority) → `async_step_intervals` (poll intervals). Each step validates before advancing.

### Services — [custom_components/pv_miner/services.py](custom_components/pv_miner/services.py) + [services.yaml](custom_components/pv_miner/services.yaml)

Service registration is global (not per-entry). v1.0.29 fixed a bug where services were lost after restart — if touching service setup, verify they survive a HA restart, not just a reload.

## Development workflow

### Running tests

```bash
python3 -m pytest __tests__/                          # all tests
python3 -m pytest __tests__/test_luxos_api.py         # single file
python3 -m pytest __tests__/test_luxos_api.py::test_logon -v   # single test
```

Tests in [\_\_tests\_\_/](__tests__/) cover the API client, config flow, and ATM/hashboard control paths. They mock the miner socket — no live miner needed.

### Live-miner diagnostics (root-level scripts)

These run **outside** Home Assistant against a real miner — use them when sensors show "Unknown" or commands appear to succeed but nothing changes:

- [test_hashboard_simple.py](test_hashboard_simple.py) — interactive: connects, logs on, reads ATM/board state, lets you toggle boards, then verifies whether state actually changed. This is how the "LuxOS firmware bug" below was confirmed.
- [test_hashboard_control.py](test_hashboard_control.py) — non-interactive variant.
- [fetch_ha_logs.py](fetch_ha_logs.py) — pulls HA logs via REST when SSH is unavailable; needs a long-lived access token.

### Deploying to a running HA instance

The integration is consumed at `<ha-config>/custom_components/pv_miner/`. Use one of the helper scripts:

```bash
./copy_to_ha.sh         # rsync-based local copy
python3 copy_to_ha.py   # python equivalent
./upload_to_ha.sh       # SCP to remote HA host
```

HA must be **restarted** (not just reloaded) after any Python code change.

### Git versioning workflow

Every commit that ships changes to `custom_components/pv_miner/` must bump `manifest.json` `version` and create a matching tag — HACS users pull from tags.

```bash
# 1. Bump manifest.json "version" (1.0.X for fixes, 1.X.0 for features)
# 2. Commit with conventional message: fix:/feat:/docs:
# 3. Tag and push:
git tag -a v1.0.NN -m "Release notes"
git push origin main --tags
# 4. Optional: gh release create v1.0.NN --notes "..." --latest
```

Each release also gets a `RELEASE_NOTES_v1.0.NN.md` at the repo root.

## Key LuxOS commands

All over TCP/4028. Authenticated commands need `session_id` injected into `parameter`.

- **Read-only**: `stats`, `devs`, `pools`, `power`, `temps`, `fans`, `version`, `summary`, `profileget`, `atmget`
- **Authenticated**: `logon`, `curtail` (sleep/wakeup), `profileset`, `enableboard`, `disableboard`, `atmset`

## Known firmware quirks (read before debugging)

**"Miner is already active" responses are not errors.** Calling `curtail wakeup` on a running miner returns this — v1.0.22 demoted it to DEBUG at every layer (TCP, HTTP, `_execute_command`, curtail wrapper, switch). If you reintroduce ERROR-level logging here, you'll spam the HA log on every poll.

**Hashboard enable/disable is broken in LuxOS firmware ~2025.10.15.** Commands return `STATUS=S` "Board enabled/disabled" but board state never actually changes. Confirmed by direct TCP calls bypassing the integration. This is a firmware bug, not an integration bug — do not "fix" it by retrying or by re-adding the per-board switches removed in v1.0.26. Power control is done via **profile switching** instead (LuxOS profiles -16 → +1 map to ~2223W → ~3693W); see [automations/solar_power_control_full.yaml](automations/solar_power_control_full.yaml) (19-step) or [automations/solar_power_control.yaml](automations/solar_power_control.yaml) (9-step).

**Hashboard commands when miner is asleep return "curtail mode is idle or sleep".** v1.0.20 added auto-wake before any board command — preserve that ordering if you refactor switch.py.

## Common debugging scenarios

- **Connection fails**: `telnet <miner_ip> 4028` first. Default creds are `root` / `root`. Then run `python3 test_hashboard_simple.py` — it isolates whether the issue is API, auth, or HA-side.
- **Sensors "Unknown"**: check the coordinator log for failures on `power` / `temps` / `fans` — these are the commands that newer firmware sometimes renames or restructures.
- **Profile dropdown empty**: `profileget` returned nothing. Verify profiles exist via the LuxOS web UI; the integration does not create them.
- **Service buttons stop working after HA restart** (not reload): regression of the v1.0.29 fix — check `services.py` is registering on integration setup, not on entry setup.
