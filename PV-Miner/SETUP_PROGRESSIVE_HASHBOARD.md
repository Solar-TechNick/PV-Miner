# Progressive Hashboard Control Setup

This guide explains how to enable the progressive hashboard control feature for your PV Miner.

## What is Progressive Hashboard Control?

Progressive hashboard control automatically enables/disables individual hashboards based on available solar power:

- **500W-800W**: Only Hashboard 0 runs (17 TH/s @ 385MHz)
- **800W-1000W**: Hashboards 0+1 run (48.1 TH/s @ 260MHz)
- **1000W+**: All 3 hashboards run (default profile)

This provides finer-grained power control than just using frequency profiles alone.

**How it works**: The integration temporarily pauses ATM (Advanced Thermal Management), switches the hashboards, then re-enables ATM automatically.

## Setup Instructions

### Step 1: Add Helper to Configuration

You need to add an `input_boolean` helper to your Home Assistant configuration. There are two ways to do this:

#### Option A: Via Configuration.yaml (Recommended)

1. Open your Home Assistant `configuration.yaml` file
2. Add the following lines:

```yaml
input_boolean:
  pv_miner_progressive_hashboard:
    name: Progressive Hashboard Control
    icon: mdi:chip
    initial: off
```

**Note**: If you already have an `input_boolean:` section in your configuration.yaml, just add the `pv_miner_progressive_hashboard` part under it:

```yaml
input_boolean:
  # Your existing input booleans here
  existing_helper_1:
    name: Existing Helper

  # Add this new one
  pv_miner_progressive_hashboard:
    name: Progressive Hashboard Control
    icon: mdi:chip
    initial: off
```

#### Option B: Via Home Assistant UI

1. Go to **Settings** → **Devices & Services** → **Helpers** tab
2. Click **+ CREATE HELPER**
3. Select **Toggle**
4. Fill in:
   - **Name**: `Progressive Hashboard Control`
   - **Icon**: `mdi:chip`
   - **Entity ID**: `input_boolean.pv_miner_progressive_hashboard` (should auto-generate)
5. Click **CREATE**

### Step 2: Restart Home Assistant

After adding the helper to `configuration.yaml`, you must restart Home Assistant:

1. Go to **Settings** → **System**
2. Click **RESTART** in the top right
3. Wait for Home Assistant to restart (1-2 minutes)

### Step 3: Add Automations

Copy the contents of `pv_miner_automations.yaml` to your Home Assistant automations:

**Via UI:**
1. Go to **Settings** → **Automations & Scenes**
2. Click **+ CREATE AUTOMATION**
3. Click **⋮** (three dots) → **Edit in YAML**
4. Copy each automation from `pv_miner_automations.yaml` one at a time

**Via File:**
If you prefer editing `automations.yaml` directly:
1. Copy the automation sections from `pv_miner_automations.yaml`
2. Paste them into your `config/automations.yaml` file
3. Go to **Developer Tools** → **YAML** → **Reload Automations**

### Step 4: Configure Dashboards

The dashboards have already been updated with the toggle switch:

**Main Dashboard** ([pv_miner_dashboard.yaml](pv_miner_dashboard.yaml)):
- Toggle appears in the "Individual Hashboard Control" section

**Mobile Dashboard** ([pv_miner_mobile_dashboard.yaml](pv_miner_mobile_dashboard.yaml)):
- Toggle appears above the hashboard buttons

Import these dashboards into Home Assistant as usual.

## How to Use

### Enable Progressive Control

1. Open your PV Miner dashboard
2. Find the **"Progressive Hashboard Control"** toggle
3. Turn it **ON**

When enabled:

- The miner will automatically manage hashboards based on solar power
- At 500W-800W, only 1 board runs (Board 0)
- At 800W-1000W, 2 boards run (Boards 0+1)
- At 1000W+, all 3 boards run

### Disable Progressive Control

Turn the toggle **OFF** to disable the feature:

- All 3 hashboards will remain active at all times
- Only the frequency/power profile automations will control power usage
- Manual hashboard control via dashboard still works

## Troubleshooting

### Error: "Integration 'pv_miner_progressive_hashboard' not found"

This means the `input_boolean` helper wasn't added correctly.

**Solution:**
1. Double-check your `configuration.yaml` has the correct syntax (see Step 1)
2. Make sure it's under `input_boolean:` not `input_boolean.pv_miner_progressive_hashboard:`
3. Restart Home Assistant again after fixing

### Toggle doesn't appear in dashboard

**Solution:**
1. Make sure you restarted Home Assistant after adding the helper
2. Check that the entity exists: Go to **Developer Tools** → **States**
3. Search for `input_boolean.pv_miner_progressive_hashboard`
4. If it doesn't exist, go back to Step 1

### Automations don't trigger

**Solution:**
1. Check that the toggle is turned **ON**
2. Verify your solar sensor (`sensor.pro3em_total_active_power`) is working
3. Check automation traces: **Settings** → **Automations & Scenes** → Select automation → **TRACES**

## Testing

To test if it's working:

1. Turn on **Progressive Hashboard Control** toggle
2. Check your solar power sensor value
3. The automations should trigger based on your current solar power:
   - If solar is 600W → Only Board 0 should be enabled
   - If solar is 900W → Boards 0+1 should be enabled
   - If solar is 1200W → All 3 boards should be enabled
4. Check the hashboard switches in your dashboard or via States
5. Check the automation traces to see if they're triggering correctly

## Default Behavior

The helper defaults to **OFF** when Home Assistant starts. This means:
- Progressive control is disabled by default
- All 3 hashboards stay active unless you turn on the toggle
- This is the safest option to prevent unexpected behavior

If you want it to start enabled, change `initial: off` to `initial: on` in your configuration.yaml.
