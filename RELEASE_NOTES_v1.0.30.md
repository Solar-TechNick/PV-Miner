# Release v1.0.30 - Built-in Automatic Solar Power Adjustment

## What's New

### Automatic Solar Power Tracking

Added **built-in automatic solar power adjustment** that works when "auto" solar mode is selected. No external automations needed!

**How it works:**
1. Select "auto" in the Solar Mode dropdown
2. The integration automatically monitors `sensor.pro3em_total_active_power`
3. Every 30 seconds, it adjusts the miner's power profile based on available solar power
4. Uses 18 different power profiles from 260MHz (2223W) to 685MHz (3693W)

### Features

- **Automatic Profile Selection**: Automatically selects the best power profile for current solar production
- **Seamless Integration**: Works directly with Pro3EM energy meter (`sensor.pro3em_total_active_power`)
- **Smart Power Mapping**: Maps solar power to optimal miner profiles with ~100W intervals
- **No External Automations**: Everything built into the integration
- **Manual Override**: Switch to "manual" mode to control power manually

### Power Profile Mapping

The automatic system uses this mapping:

| Available Solar | Profile | Power Draw | Hashrate |
|----------------|---------|------------|----------|
| 0-2300W | 260MHz | 2223W | 48 TH/s |
| 2300-2400W | 285MHz | ~2300W | ~52 TH/s |
| 2400-2500W | 310MHz | ~2400W | ~56 TH/s |
| ... | ... | ... | ... |
| 3900W+ | 685MHz | 3693W | 127 TH/s |

Full 18-step power adjustment between min and max profiles.

## Installation

### Update Integration

1. **HACS Update**:
   - HACS → Integrations → PV Miner → Redownload (select v1.0.30)
   - **IMPORTANT**: Restart Home Assistant after updating

2. **Manual Update**:
   ```bash
   cd /config/custom_components/
   rm -rf pv_miner/
   git clone https://github.com/Solar-TechNick/PV-Miner.git pv_miner_temp
   cp -r pv_miner_temp/custom_components/pv_miner ./
   rm -rf pv_miner_temp/
   ```

### How to Use

1. **Restart Home Assistant** (required after update)

2. **Enable Auto Mode**:
   - Go to your miner entity
   - Find "Solar Mode" selector
   - Select "auto"

3. **Watch it work**:
   - The integration will automatically adjust power every 30 seconds
   - Check logs to see adjustments: Settings → System → Logs → Filter by "pv_miner"
   - You'll see messages like: "Auto-adjusting s19: 3200W solar -> profile 510MHz"

## Files Changed

- `custom_components/pv_miner/__init__.py` - Added solar coordinator integration
- `custom_components/pv_miner/select.py` - Hook solar mode selector to coordinator
- `custom_components/pv_miner/solar_coordinator.py` - **NEW**: Built-in automatic adjustment logic
- `custom_components/pv_miner/manifest.json` - Version 1.0.30

## Technical Details

### Solar Coordinator

The new `SolarPowerCoordinator` class:
- Runs every 30 seconds when auto mode is enabled
- Monitors `sensor.pro3em_total_active_power` for solar production
- Maps solar power to appropriate LuxOS power profiles
- Only changes profile when needed (reduces API calls)
- Logs all adjustments for monitoring

### Solar Sensor

By default, monitors: `sensor.pro3em_total_active_power`

If you need to change this, edit line 100 in `__init__.py`:
```python
"sensor.pro3em_total_active_power",  # Change to your solar sensor
```

## Upgrading from v1.0.29

1. Update the integration via HACS or manually
2. **Restart Home Assistant** (required)
3. Set Solar Mode to "auto"
4. Monitor logs to verify automatic adjustments are working

## Previous Releases

- [v1.0.29 Release Notes](RELEASE_NOTES_v1.0.29.md) - Service registration fix
- [v1.0.28 Release Notes](RELEASE_NOTES_v1.0.28.md) - Dashboard updates
- [v1.0.27 Release Notes](RELEASE_NOTES_v1.0.27.md) - Pro3EM integration

## Documentation

- Dashboard examples: `pv_miner_dashboard.yaml`, `pv_miner_mobile_dashboard.yaml`
- Automation guide: [automations/README.md](automations/README.md)
- Integration docs: [CLAUDE.md](CLAUDE.md)
- Repository: https://github.com/Solar-TechNick/PV-Miner

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
