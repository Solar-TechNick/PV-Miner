# Release v1.0.28 - Dashboard Updates

## What's New

### Updated Dashboards
- Removed references to non-functional hashboard switches
- Added power profile quick-access buttons to both dashboards
- Updated both desktop and mobile dashboard configurations

### Dashboard Changes

#### Desktop Dashboard ([pv_miner_dashboard.yaml](pv_miner_dashboard.yaml))
- **Removed**: Individual hashboard control section (switch.s19_hashboard_0/1/2)
- **Added**: Power Profile Control section with 4 buttons:
  - 🔋 Min (260MHz) - 2223W, 48 TH/s
  - ⚡ Low (385MHz) - ~2600W, ~70 TH/s
  - ⚖️ Mid (510MHz) - ~3000W, ~95 TH/s
  - 🔥 Max (685MHz) - 3693W, 127 TH/s

#### Mobile Dashboard ([pv_miner_mobile_dashboard.yaml](pv_miner_mobile_dashboard.yaml))
- **Removed**: Progressive hashboard toggle and hashboard status buttons
- **Added**: Compact power profile buttons (Min, Low, Mid, Max)
- Optimized for mobile screen space

### Why This Change?

LuxOS firmware 2025.10.15.191043 has a known issue where `enableboard` and `disableboard` commands don't work. The hashboard switch entities were removed in v1.0.27, so the dashboards needed to be updated to reflect this change.

Power profiles provide better granular control anyway, with 19 different power levels from 260MHz to 685MHz.

## Installation

### Update Integration

1. **HACS Update**:
   - HACS → Integrations → PV Miner → Redownload (select v1.0.28)
   - **IMPORTANT**: Restart Home Assistant after updating

2. **Manual Update**:
   ```bash
   cd /config/custom_components/
   rm -rf pv_miner/
   git clone https://github.com/Solar-TechNick/PV-Miner.git pv_miner_temp
   cp -r pv_miner_temp/custom_components/pv_miner ./
   rm -rf pv_miner_temp/
   ```

### Update Dashboards

1. **Desktop Dashboard**:
   - Copy [pv_miner_dashboard.yaml](https://raw.githubusercontent.com/Solar-TechNick/PV-Miner/main/pv_miner_dashboard.yaml)
   - Settings → Dashboards → Edit Dashboard → Raw Configuration Editor
   - Paste and save

2. **Mobile Dashboard**:
   - Copy [pv_miner_mobile_dashboard.yaml](https://raw.githubusercontent.com/Solar-TechNick/PV-Miner/main/pv_miner_mobile_dashboard.yaml)
   - Settings → Dashboards → Edit Dashboard → Raw Configuration Editor
   - Paste and save

3. **Replace Entity IDs**:
   - Find and replace `s19` with your actual miner entity name
   - Update solar sensor names to match your setup

## Files Changed

- `custom_components/pv_miner/manifest.json` - Version 1.0.28
- `pv_miner_dashboard.yaml` - Removed hashboard switches, added power profiles
- `pv_miner_mobile_dashboard.yaml` - Removed hashboard switches, added power profiles

## Upgrading from v1.0.27

If you're upgrading from v1.0.27:
1. Update the integration via HACS
2. **Restart Home Assistant** (required to fix service registration)
3. Update your dashboard YAML files
4. Your automations don't need any changes

## Previous Release

See [v1.0.27 Release Notes](RELEASE_NOTES_v1.0.27.md) for the Pro3EM integration and full 19-step solar automation.

## Documentation

- Dashboard examples: `pv_miner_dashboard.yaml`, `pv_miner_mobile_dashboard.yaml`
- Automation guide: [automations/README.md](automations/README.md)
- Integration docs: [CLAUDE.md](CLAUDE.md)
- Repository: https://github.com/Solar-TechNick/PV-Miner

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
