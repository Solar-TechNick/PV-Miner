# Release v1.0.31 - Automatic Sleep/Wake for Solar Mode

## What's New

### Automatic Miner Sleep/Wake

Enhanced the automatic solar power tracking (v1.0.30) with **intelligent sleep/wake functionality**. The miner now automatically sleeps when there's no solar power and wakes when solar returns!

**How it works:**
1. **Low Solar (< 500W)**: Miner automatically goes to sleep to save power
2. **Solar Returns (>= 500W)**: Miner automatically wakes up and adjusts to appropriate power profile
3. **Profile Switching**: Continuously adjusts between all 18 power profiles (-16 to +1: 260MHz to 685MHz) to maximize performance based on available solar

### Features

- **Automatic Sleep**: Puts miner to sleep when solar production drops below 500W
- **Automatic Wake**: Wakes miner when solar production returns (with 5-second stabilization delay)
- **Smart Profile Switching**: Adjusts power profile every 30 seconds to match available solar power
- **Zero Manual Intervention**: Everything happens automatically in "auto" mode
- **Detailed Logging**: All sleep/wake/profile changes are logged for monitoring

## Example Operation

**Morning (sunrise)**:
- 6:00 AM - Solar: 300W → Miner stays asleep
- 7:00 AM - Solar: 2300W → Miner wakes, sets to 260MHz (2223W, profile -16)
- 8:00 AM - Solar: 2500W → Switches to 335MHz profile (profile -12)
- 9:00 AM - Solar: 3000W → Switches to 460MHz profile (profile -6)
- 10:00 AM - Solar: 3800W → Switches to 660MHz profile (profile +0)

**Evening (sunset)**:
- 5:00 PM - Solar: 3500W → Running at 585MHz (profile -2)
- 6:00 PM - Solar: 2400W → Switches to 310MHz (profile -14)
- 7:00 PM - Solar: 400W → Miner goes to sleep

## Installation

### Update Integration

1. **HACS Update**:
   - HACS → Integrations → PV Miner → Redownload (select v1.0.31)
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

3. **Monitor Operation**:
   - Watch the integration automatically manage your miner
   - Check logs: Settings → System → Logs → Filter by "pv_miner"
   - You'll see messages like:
     - "Auto-sleeping s19: 50W solar (insufficient power)"
     - "Auto-waking s19: 2500W solar available"
     - "Auto-adjusting s19: 3200W solar -> profile 510MHz (was 460MHz)"

## Files Changed

- `custom_components/pv_miner/solar_coordinator.py` - Added sleep/wake logic
- `custom_components/pv_miner/manifest.json` - Version 1.0.31

## Technical Details

### Sleep/Wake Logic

The solar coordinator now includes three operational states:

1. **Sleep State** (`available_power < 500W`):
   - Calls `pause_mining()` API to put miner to sleep
   - Sets `_current_profile = "sleep"`
   - Logs sleep action with power level
   - Skips profile adjustments while asleep

2. **Wake State** (`available_power >= 500W` and was sleeping):
   - Calls `resume_mining()` API to wake miner
   - Waits 5 seconds for miner to stabilize
   - Proceeds to set appropriate power profile
   - Logs wake action with available power

3. **Active State** (miner awake, adjusting profiles):
   - Monitors available solar power every 30 seconds
   - Maps power to optimal profile using 18-step mapping
   - Only changes profile when different from current
   - Logs all profile changes

### Power Threshold

The 500W threshold prevents frequent sleep/wake cycles:
- Below 500W: Not enough to run miner at minimum (260MHz = 2223W)
- Above 500W: Enough to justify waking and setting minimum profile
- Provides buffer zone to prevent oscillation during cloudy conditions

## Upgrading from v1.0.30

1. Update the integration via HACS or manually
2. **Restart Home Assistant** (required)
3. Set Solar Mode to "auto"
4. Monitor logs to verify automatic sleep/wake is working
5. Test with low solar conditions (evening) - miner should sleep
6. Test with solar return (morning) - miner should wake and adjust

## Previous Releases

- [v1.0.30 Release Notes](RELEASE_NOTES_v1.0.30.md) - Built-in automatic solar power adjustment
- [v1.0.29 Release Notes](RELEASE_NOTES_v1.0.29.md) - Service registration fix
- [v1.0.28 Release Notes](RELEASE_NOTES_v1.0.28.md) - Dashboard updates

## Documentation

- Dashboard examples: `pv_miner_dashboard.yaml`, `pv_miner_mobile_dashboard.yaml`
- Automation guide: [automations/README.md](automations/README.md)
- Integration docs: [CLAUDE.md](CLAUDE.md)
- Repository: https://github.com/Solar-TechNick/PV-Miner

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
