# ☀️ PV Miner Dashboard Setup Guide

Complete setup instructions for the PV Miner Home Assistant Dashboard and Automations.

## 📋 Prerequisites

Before setting up the dashboard, ensure you have:

1. ✅ **PV Miner Integration v1.0.13+** installed and working
2. ✅ **Your miner** connected and responding (tested at 192.168.99.202)  
3. ✅ **Solar sensors** configured in Home Assistant (replace sensor names)
4. ✅ **Battery sensors** configured (if using battery backup)
5. ✅ **Mobile app** configured for notifications (optional)

## 🎛️ Dashboard Installation

### Step 1: Add Dashboard YAML

1. **Copy the Dashboard Code**:
   - Copy contents of `pv_miner_dashboard.yaml`

2. **Add to Home Assistant**:
   - Go to **Settings** → **Dashboards** 
   - Click **Add Dashboard**
   - Choose **New dashboard from YAML**
   - Paste the YAML content
   - Click **Save**

### Step 2: Customize Entity Names

**IMPORTANT**: Replace all instances of `antminer_s21` with your actual miner entity names:

```yaml
# Change from:
entity: switch.antminer_s21_miner

# Change to (example):
entity: switch.your_miner_name_miner
```

**Your Actual Entity Names** (based on your miner at 192.168.99.202):
Find these in **Settings** → **Devices & Services** → **PV Miner** → your device:

- Main Switch: `switch.[your_miner_name]_miner`
- Hashrate: `sensor.[your_miner_name]_hashrate`  
- Power: `sensor.[your_miner_name]_power_consumption`
- Temperature: `sensor.[your_miner_name]_temperature`
- Profile Select: `select.[your_miner_name]_power_profile`
- Hashboards: `switch.[your_miner_name]_hashboard_0/1/2`

### Step 3: Configure Solar Sensors

Replace these placeholders with your actual solar sensor entities:

```yaml
# Replace these in the dashboard:
sensor.solar_power_production  # Your solar production sensor
sensor.battery_soc            # Your battery state of charge sensor
```

**Common Solar Sensor Names**:
- Victron: `sensor.battery_voltage`, `sensor.pv_power`
- SolarEdge: `sensor.solaredge_current_power`  
- Fronius: `sensor.power_photovoltaics`
- Enphase: `sensor.envoy_current_power_production`

## 🤖 Automation Setup

### Step 1: Install Automations

1. **Option A - YAML Mode**:
   - Copy contents of `pv_miner_automations.yaml`
   - Add to your `automations.yaml` file
   - Restart Home Assistant

2. **Option B - UI Mode**:
   - Go to **Settings** → **Automations & Scenes**
   - Click **Create Automation**
   - Choose **Start from scratch**
   - Switch to **YAML mode** (⚙️ icon)
   - Paste individual automation YAML
   - Repeat for each automation

### Step 2: Customize Automation Parameters

**Solar Power Thresholds** (adjust based on your setup):
```yaml
# High Power Mode
above: 6000  # Watts - when you have excess solar

# Medium Power Mode  
above: 4000  # Watts - moderate solar
below: 6000

# Eco Mode
above: 2000  # Watts - limited solar
below: 4000  

# Sleep Mode
below: 2000  # Watts - insufficient solar
```

**Battery Protection** (adjust based on your battery):
```yaml
# Low battery warning
below: 30  # 30% SOC

# Critical battery emergency  
below: 20  # 20% SOC
```

**Temperature Limits** (adjust based on your environment):
```yaml
# High temperature reduction
above: 75  # °C

# Emergency temperature stop
above: 85  # °C
```

### Step 3: Configure Notifications

Replace notification targets:
```yaml
# Replace with your mobile app:
service: notify.mobile_app_your_phone

# Or use other notification methods:
service: notify.telegram
service: notify.discord
service: notify.email
```

## 🎯 Available Profile Names

Your S21+ miner has these profiles available (use exact names in automations):

**🔋 Low Power (2100-2900W)**:
- `"310MHz"` - 104.3TH/s, 2136W (Ultra Eco)
- `"335MHz"` - 112.7TH/s, 2314W  
- `"360MHz"` - 121.1TH/s, 2499W
- `"385MHz"` - 129.5TH/s, 2692W
- `"410MHz"` - 138.0TH/s, 2892W

**⚖️ Medium Power (3100-4500W)**:
- `"435MHz"` - 146.4TH/s, 3101W
- `"460MHz"` - 154.8TH/s, 3317W  
- `"485MHz"` - 163.2TH/s, 3541W
- `"510MHz"` - 171.6TH/s, 3773W
- `"535MHz"` - 180.0TH/s, 4012W
- `"560MHz"` - 188.4TH/s, 4260W (Recommended balanced)
- `"585MHz"` - 196.9TH/s, 4515W

**🔥 High Power (4800-8500W)**:
- `"610MHz"` - 205.3TH/s, 4778W
- `"635MHz"` - 213.7TH/s, 5049W
- `"660MHz"` - 222.1TH/s, 5327W
- `"685MHz"` - 230.5TH/s, 5613W
- `"default"` - 238.9TH/s, 5908W (Standard)
- `"735MHz"` - 247.4TH/s, 6209W  
- `"760MHz"` - 255.8TH/s, 6519W
- `"785MHz"` - 264.2TH/s, 6837W
- `"810MHz"` - 272.6TH/s, 7162W (High performance)
- `"835MHz"` - 281.0TH/s, 7495W
- `"860MHz"` - 289.4TH/s, 7836W
- `"885MHz"` - 297.8TH/s, 8184W
- `"910MHz"` - 306.3TH/s, 8541W (Maximum)

## 🔧 Quick Service Call Examples

Use these in automations or scripts:

```yaml
# Wake up miner
service: pv_miner.wake_miner
target:
  entity_id: switch.your_miner_miner

# Put miner to sleep  
service: pv_miner.sleep_miner
target:
  entity_id: switch.your_miner_miner

# Set specific profile
service: pv_miner.set_power_profile
data:
  profile: "560MHz"
target:
  entity_id: switch.your_miner_miner

# Solar max mode
service: pv_miner.solar_max
target:
  entity_id: switch.your_miner_miner

# Eco mode
service: pv_miner.eco_mode  
target:
  entity_id: switch.your_miner_miner

# Emergency stop
service: pv_miner.emergency_stop
target:
  entity_id: switch.your_miner_miner
```

## 📊 Dashboard Features

### Main Control Panel
- ✅ **Quick Status**: Miner state, hashrate, power, efficiency at a glance
- ✅ **Solar Integration**: Solar production, battery SOC, available power
- ✅ **Quick Controls**: Wake, Sleep, Solar Max, Eco Mode buttons

### Profile Management  
- ✅ **Dynamic Profiles**: All 25 profiles loaded from your miner
- ✅ **Quick Select**: Buttons for common profiles (Eco, Balanced, Default, High)
- ✅ **Advanced Controls**: Power limits, frequency offset, solar mode

### Performance Monitoring
- ✅ **Gauges**: Visual hashrate and power consumption meters
- ✅ **Temperature**: Main temp + individual hashboard temperatures  
- ✅ **History Charts**: 24-hour performance and solar correlation graphs

### Individual Control
- ✅ **Hashboard Switches**: Control each mining board independently
- ✅ **System Info**: Uptime, mining pool, fan speed
- ✅ **Status Summary**: Comprehensive overview with current values

## 🚀 Getting Started

1. **Install the dashboard** using the YAML file
2. **Customize entity names** to match your miner
3. **Add your solar sensors** to replace placeholders
4. **Install automations** for smart solar mining
5. **Test basic functions** (wake, sleep, profile change)
6. **Customize thresholds** based on your solar system
7. **Enable notifications** for monitoring alerts

## 🆘 Troubleshooting

**Dashboard not showing entities**:
- Check entity names match exactly
- Ensure PV Miner integration is running
- Verify miner is connected and responding

**Automations not triggering**:
- Check solar sensor names are correct
- Verify trigger thresholds match your system  
- Test individual service calls manually

**Profile switching failing**:
- Ensure miner is awake (not in sleep mode)
- Check profile names are exact (case-sensitive)
- Use dynamic profiles from your actual miner

**Need Help?**
- Check Home Assistant logs for errors
- Test API directly using included test scripts
- Verify miner connectivity at 192.168.99.202

## 🎉 Result

You'll have a complete solar mining control center with:
- **Smart automation** that adapts to solar conditions
- **Full manual control** with comprehensive dashboard
- **Safety features** for temperature and battery protection  
- **Performance monitoring** with historical data
- **Mobile notifications** for important events

Perfect for maximizing your solar Bitcoin mining efficiency! ⚡☀️₿