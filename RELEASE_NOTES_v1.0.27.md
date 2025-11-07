# Release v1.0.27 - Pro3EM Integration & Full Solar Automation

## What's New

### Pro3EM Energy Meter Integration
- All automations now use `sensor.pro3em_total_active_power` directly
- No configuration needed - works out of the box with Pro3EM meter
- Real-time solar power monitoring for dynamic miner control

### Full 19-Step Solar Power Automation
- Complete coverage of all available power profiles from -16 to +1
- Granular ~80W intervals between each power step
- Power range: 500W (sleep) to 3693W (685MHz maximum)
- File: `automations/solar_power_control_full.yaml`

### Power Profile Details
| Step | Solar Power | Profile | Miner Power | Hashrate |
|------|------------|---------|-------------|----------|
| 1 | 500-2200W | Sleep | ~50W | 0 TH/s |
| 2 | 2200-2282W | 260MHz | 2223W | 48 TH/s |
| 3 | 2282-2365W | 285MHz | 2311W | 53 TH/s |
| 4-18 | ... | ... | ... | ... |
| 19 | 3610W+ | 685MHz | 3693W | 127 TH/s |

See full table in `automations/README.md`

### Bug Fixes
- Removed non-functional hashboard switches (LuxOS firmware 2025.10.15.191043 limitation)
- Replaced with working power profile switching

## Installation

1. **Update Integration**:
   - HACS → Integrations → PV Miner → Redownload (select v1.0.27)

2. **Add Automation**:
   - Copy `automations/solar_power_control_full.yaml` from repository
   - Settings → Automations & Scenes → Create Automation → Edit in YAML
   - Paste and save

3. **Verify**:
   - Check `sensor.pro3em_total_active_power` exists
   - Verify miner entity IDs match your setup

## Files Changed

- `custom_components/pv_miner/manifest.json` - Version 1.0.27
- `custom_components/pv_miner/switch.py` - Removed hashboard switches
- `automations/solar_power_control_full.yaml` - Full 19-step automation
- `automations/README.md` - Complete documentation

## Documentation

- Setup guide: `automations/README.md`
- Integration docs: `CLAUDE.md`
- Repository: https://github.com/Solar-TechNick/PV-Miner

---

🤖 Generated with Claude Code
