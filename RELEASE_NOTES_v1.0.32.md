# Release Notes - v1.0.32

## Bug Fixes

### Critical: Fixed Service Call Entity Mapping
- **Issue**: Service calls (e.g., `pv_miner.set_power_profile`, `pv_miner.wake_miner`, etc.) always targeted the first configured miner regardless of which entity was selected
- **Root Cause**: `services.py` line 207-234 used a simplified entity-to-config-entry mapping that just picked the first config entry and broke the loop
- **Fix**: Implemented proper entity registry lookup to correctly map each entity to its parent config entry
- **Impact**: Multi-miner setups can now correctly target individual miners with service calls

## Technical Details

### Changed Files
- `custom_components/pv_miner/services.py:207-237`
  - Added Home Assistant entity registry import
  - Use `entity_registry.async_get(entity_id)` to properly find config entry
  - Extract `config_entry_id` from entity entry instead of iterating all entries

### Service Calls Now Working Correctly
All services now properly target the correct miner when called:
- `set_power_profile`
- `set_power_limit`
- `emergency_stop`
- `solar_max`
- `eco_mode`
- `set_pool`
- `sleep_miner`
- `wake_miner`

## Upgrade Instructions

1. Copy updated integration files to Home Assistant:
   ```bash
   ./copy_to_ha.sh
   # or
   python3 copy_to_ha.py
   # or
   ./upload_to_ha.sh
   ```

2. **Restart Home Assistant** (full restart required, not just reload)

3. Test service calls with multiple miners configured

## Testing Checklist

- [ ] Service calls target the correct miner in multi-miner setups
- [ ] Profile changes apply to the selected miner entity
- [ ] Sleep/wake commands affect the correct miner
- [ ] Dashboard service buttons work for each miner independently

## Version

- **Version**: 1.0.32
- **Date**: 2026-05-15
- **Type**: Bug fix
- **Breaking Changes**: None
