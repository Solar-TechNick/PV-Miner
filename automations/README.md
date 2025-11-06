# PV Miner Solar Power Control Automation

This automation automatically adjusts your miner's power consumption based on available solar power from your Pro3EM meter, using 19 power steps from 500W (standby) to 3693W (maximum performance).

**Use `solar_power_control_full.yaml` for the complete 19-step automation with all available power profiles.**

## Power Steps (Full 19-Step Automation)

| Step | Solar Power | Action | Profile | Miner Power | Hashrate |
|------|------------|--------|---------|-------------|----------|
| 1 | 500-2200W | Sleep mode | - | ~50W | 0 TH/s |
| 2 | 2200-2282W | Profile switch | 260MHz | 2223W | 48 TH/s |
| 3 | 2282-2365W | Profile switch | 285MHz | 2311W | 53 TH/s |
| 4 | 2365-2448W | Profile switch | 310MHz | 2399W | 57 TH/s |
| 5 | 2448-2531W | Profile switch | 335MHz | 2488W | 62 TH/s |
| 6 | 2531-2614W | Profile switch | 360MHz | 2576W | 67 TH/s |
| 7 | 2614-2697W | Profile switch | 385MHz | 2664W | 71 TH/s |
| 8 | 2697-2780W | Profile switch | 410MHz | 2752W | 76 TH/s |
| 9 | 2780-2863W | Profile switch | 435MHz | 2838W | 80 TH/s |
| 10 | 2863-2946W | Profile switch | 460MHz | 2923W | 85 TH/s |
| 11 | 2946-3029W | Profile switch | 485MHz | 3009W | 90 TH/s |
| 12 | 3029-3112W | Profile switch | 510MHz | 3094W | 94 TH/s |
| 13 | 3112-3195W | Profile switch | 535MHz | 3180W | 99 TH/s |
| 14 | 3195-3278W | Profile switch | 560MHz | 3265W | 104 TH/s |
| 15 | 3278-3361W | Profile switch | 585MHz | 3351W | 108 TH/s |
| 16 | 3361-3444W | Profile switch | 610MHz | 3436W | 113 TH/s |
| 17 | 3444-3527W | Profile switch | 635MHz | 3522W | 118 TH/s |
| 18 | 3527-3610W | Profile switch | default | 3608W | 122 TH/s |
| 19 | 3610W+ | Profile switch | 685MHz | 3693W | 127 TH/s |

## Installation

### Step 1: Configure Your Solar Power Sensor

The automation uses `sensor.pro3em_total_active_power` from your Pro3EM energy meter. This sensor reports the total active power in watts.

**Already configured**: The automation is preconfigured to use the Pro3EM sensor. No changes needed unless you want to use a different power source.

### Step 2: Configure Entity IDs

The following entity IDs are used in `solar_power_control_full.yaml`:
- `switch.pv_miner_miner_enabled` - Your miner on/off switch
- `select.pv_miner_power_profile` - Your miner profile selector

If your miner has a different name, update these entity IDs:
1. Go to **Developer Tools** → **States**
2. Search for your miner name
3. Update the entity IDs in the automation file

### Step 3: Add Automation to Home Assistant

**Option A: Via UI (Recommended)**:
1. Copy the contents of `solar_power_control_full.yaml`
2. In Home Assistant, go to **Settings** → **Automations & Scenes**
3. Click **Create Automation** → **Create new automation** → **Edit in YAML**
4. Paste the automation YAML
5. Click **Save**

**Option B: Via Configuration File**:
1. Copy `solar_power_control_full.yaml` to your Home Assistant `config/automations/` folder
2. Add to `configuration.yaml`:
   ```yaml
   automation: !include_dir_merge_list automations/
   ```
3. Restart Home Assistant

### Step 4: Test the Automation

1. Check that your Pro3EM power sensor is working: **Developer Tools** → **States** → Search for `sensor.pro3em_total_active_power`
2. Check the automation runs: **Settings** → **Automations** → **PV Miner: Solar Power Control (Full Range)** → **Run**
3. Monitor your miner's power profile changes in the PV Miner device page

## Customization

### Adjust Power Thresholds

Edit the conditions in `solar_power_control_full.yaml` to match your needs:

```yaml
- condition: template
  value_template: "{{ states('sensor.pro3em_total_active_power') | float(0) >= 2200 and states('sensor.pro3em_total_active_power') | float(0) < 2282 }}"
```

Change the values (2200, 2282) to your desired thresholds. The current thresholds are set with ~80W intervals between each profile step.

### Add Hysteresis (Prevent Rapid Switching)

Add a time-based condition to prevent frequent profile changes:

```yaml
condition:
  - condition: template
    value_template: "{{ states('sensor.pro3em_total_active_power') not in ['unknown', 'unavailable'] }}"
  - condition: template
    value_template: "{{ as_timestamp(now()) - as_timestamp(state_attr('automation.pv_miner_power_control_full', 'last_triggered')) > 300 }}"
    # Prevents running more than once every 5 minutes
```

## Troubleshooting

### Automation Not Triggering

**Check Pro3EM power sensor**:
```yaml
Developer Tools → States → sensor.pro3em_total_active_power
```
Make sure it's reporting values and not "unknown" or "unavailable".

**Check automation is enabled**:
```
Settings → Automations → PV Miner: Solar Power Control (Full Range)
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
