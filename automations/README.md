# PV Miner Solar Power Control Automation

This automation automatically adjusts your miner's power consumption based on available solar power, using 9 power steps from 500W (standby) to 3500W (high performance).

## Power Steps

| Step | Solar Power | Action | Profile | Miner Power | Hashrate |
|------|------------|--------|---------|-------------|----------|
| 1 | 500-2100W | Sleep mode | - | ~50W | 0 TH/s |
| 2 | 2100-2300W | Profile switch | 260MHz | 2223W | 48 TH/s |
| 3 | 2300-2500W | Profile switch | 310MHz | 2399W | 57 TH/s |
| 4 | 2500-2700W | Profile switch | 360MHz | 2576W | 67 TH/s |
| 5 | 2700-2900W | Profile switch | 435MHz | 2838W | 80 TH/s |
| 6 | 2900-3100W | Profile switch | 485MHz | 3009W | 90 TH/s |
| 7 | 3100-3300W | Profile switch | 535MHz | 3180W | 99 TH/s |
| 8 | 3300-3500W | Profile switch | 610MHz | 3436W | 113 TH/s |
| 9 | 3500W+ | Profile switch | 635MHz | 3522W | 118 TH/s |

## Installation

### Step 1: Configure Your Solar Power Sensor

Replace `sensor.solar_power_available` in the automation with your actual solar power sensor entity ID. This should be a sensor that reports available solar power in watts.

**Example solar power sensors**:
- `sensor.solar_panels_power` - Direct solar production
- `sensor.grid_power` - If you want to use grid power (negative = exporting)
- `sensor.house_surplus_power` - House production minus consumption

### Step 2: Configure Entity IDs

Replace the following entity IDs in `solar_power_control.yaml`:
- `switch.pv_miner_miner_enabled` - Your miner on/off switch
- `select.pv_miner_power_profile` - Your miner profile selector

You can find your actual entity IDs in Home Assistant:
1. Go to **Developer Tools** → **States**
2. Search for "pv_miner"
3. Copy the entity IDs

### Step 3: Add Automation to Home Assistant

**Option A: Via UI (Recommended)**:
1. Copy the contents of `solar_power_control.yaml`
2. In Home Assistant, go to **Settings** → **Automations & Scenes**
3. Click **Create Automation** → **Create new automation** → **Edit in YAML**
4. Paste the automation YAML
5. Click **Save**

**Option B: Via Configuration File**:
1. Copy `solar_power_control.yaml` to your Home Assistant `config/automations/` folder
2. Add to `configuration.yaml`:
   ```yaml
   automation: !include_dir_merge_list automations/
   ```
3. Restart Home Assistant

### Step 4: Test the Automation

1. Check that your solar power sensor is working: **Developer Tools** → **States**
2. Manually change the solar power value to test different steps
3. Check the automation runs: **Settings** → **Automations** → **PV Miner: Solar Power Control** → **Run**
4. Monitor notifications to see power adjustments

## Customization

### Adjust Power Thresholds

Edit the conditions in `solar_power_control.yaml` to match your needs:

```yaml
- condition: template
  value_template: "{{ states('sensor.solar_power_available') | float(0) >= 2100 and states('sensor.solar_power_available') | float(0) < 2300 }}"
```

Change the values (2100, 2300) to your desired thresholds.

### Disable Notifications

Remove or comment out the `notify.persistent_notification` services if you don't want notifications:

```yaml
# - service: notify.persistent_notification
#   data:
#     title: "PV Miner Power Control"
#     message: "..."
```

### Add Hysteresis (Prevent Rapid Switching)

Add a time-based condition to prevent frequent profile changes:

```yaml
condition:
  - condition: template
    value_template: "{{ states('sensor.solar_power_available') not in ['unknown', 'unavailable'] }}"
  - condition: template
    value_template: "{{ as_timestamp(now()) - as_timestamp(state_attr('automation.pv_miner_power_control', 'last_triggered')) > 300 }}"
    # Prevents running more than once every 5 minutes
```

## Troubleshooting

### Automation Not Triggering

**Check solar power sensor**:
```yaml
Developer Tools → States → sensor.solar_power_available
```
Make sure it's reporting values and not "unknown" or "unavailable".

**Check automation is enabled**:
```
Settings → Automations → PV Miner: Solar Power Control
```
Make sure the toggle is ON.

### Wrong Profile Being Selected

**Check the condition ranges** in the automation and make sure they match your solar power availability.

**Check entity IDs** are correct:
- Miner switch: `switch.pv_miner_miner_enabled`
- Profile selector: `select.pv_miner_power_profile`

### Miner Not Responding

1. Check miner is online and reachable
2. Check PV Miner integration is loaded: **Settings** → **Devices & Services** → **PV Miner**
3. Try manually changing the profile in Home Assistant UI
4. Check Home Assistant logs: **Settings** → **System** → **Logs**, filter by "pv_miner"

## Advanced: Multi-Miner Setup

If you have multiple miners, duplicate the automation and adjust:
1. Change the automation ID: `pv_miner_1_power_control`, `pv_miner_2_power_control`, etc.
2. Adjust entity IDs for each miner
3. Optionally distribute power between miners based on priority

Example priority-based control:
- Miner 1: Gets power first (500-3500W)
- Miner 2: Only starts when solar > 3500W
- Miner 3: Only starts when solar > 6000W

## Support

For issues or questions:
- GitHub: https://github.com/Solar-TechNick/PV-Miner/issues
- Integration docs: See CLAUDE.md in the repository
