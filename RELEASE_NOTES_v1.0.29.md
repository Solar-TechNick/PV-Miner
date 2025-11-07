# Release v1.0.29 - Service Registration Fix

## What's New

### Bug Fix: Dashboard Service Buttons

Fixed issue where dashboard service buttons (Wake, Sleep, Solar Max, Eco Mode, etc.) were not working after Home Assistant restart.

**Problem**: Services were being registered multiple times (once per config entry), which could cause conflicts and prevent proper service registration.

**Solution**: Services are now registered only once globally, preventing duplicate registration issues.

## Technical Details

### Changes Made

- **custom_components/pv_miner/\_\_init\_\_.py**: Added check to ensure services are only registered once, not per config entry
  - Services now check if already registered before attempting registration
  - Prevents `hass.services.async_register()` from being called multiple times

### Why This Matters

Home Assistant services should be registered at the integration level, not per device. This fix ensures:
- Dashboard buttons work reliably after restart
- No service registration conflicts with multiple miners
- Proper service cleanup on integration reload

## Installation

### Update Integration

1. **HACS Update**:
   - HACS → Integrations → PV Miner → Redownload (select v1.0.29)
   - **IMPORTANT**: Restart Home Assistant after updating

2. **Manual Update**:
   ```bash
   cd /config/custom_components/
   rm -rf pv_miner/
   git clone https://github.com/Solar-TechNick/PV-Miner.git pv_miner_temp
   cp -r pv_miner_temp/custom_components/pv_miner ./
   rm -rf pv_miner_temp/
   ```

### After Update

1. **Restart Home Assistant** (required to register services properly)
2. Test dashboard buttons:
   - Wake Miner button should work
   - Sleep Miner button should work
   - Power profile buttons should work
   - All service calls should execute without errors

## Files Changed

- `custom_components/pv_miner/__init__.py` - Added service registration check
- `custom_components/pv_miner/manifest.json` - Version 1.0.29

## Upgrading from v1.0.28

If you're upgrading from v1.0.28:
1. Update the integration via HACS or manually
2. **Restart Home Assistant** (required to fix service registration)
3. Test dashboard buttons - they should now work correctly

## Previous Releases

- [v1.0.28 Release Notes](RELEASE_NOTES_v1.0.28.md) - Dashboard updates
- [v1.0.27 Release Notes](RELEASE_NOTES_v1.0.27.md) - Pro3EM integration

## Documentation

- Dashboard examples: `pv_miner_dashboard.yaml`, `pv_miner_mobile_dashboard.yaml`
- Automation guide: [automations/README.md](automations/README.md)
- Integration docs: [CLAUDE.md](CLAUDE.md)
- Repository: https://github.com/Solar-TechNick/PV-Miner

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
