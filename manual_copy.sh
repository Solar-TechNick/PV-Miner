#!/bin/bash
# Manual copy instructions for Home Assistant

cat << 'EOF'
================================================================================
MANUAL COPY INSTRUCTIONS FOR HOME ASSISTANT
================================================================================

The automation file is ready to be copied to your Home Assistant.

OPTION 1 - Direct Copy via Command Line (Recommended):
-------------------------------------------------------
Run these commands one at a time and enter password 'hassio' when prompted:

ssh hassio@192.168.1.147 "mkdir -p /config/automations"

scp automations/solar_power_control_full.yaml hassio@192.168.1.147:/config/automations/

scp automations/README.md hassio@192.168.1.147:/config/automations/


OPTION 2 - Via GitHub (Easiest if you don't have SSH):
-------------------------------------------------------
1. Open: https://github.com/Solar-TechNick/PV-Miner/blob/main/automations/solar_power_control_full.yaml
2. Click "Raw" button
3. Copy all content (Ctrl+A, Ctrl+C)
4. In Home Assistant:
   - Settings → Automations & Scenes
   - Create Automation → Edit in YAML
   - Paste the content
   - Save


OPTION 3 - Via Home Assistant File Editor Add-on:
--------------------------------------------------
If you have the File Editor add-on installed:
1. Open File Editor in Home Assistant
2. Navigate to /config/automations/
3. Create new file: solar_power_control_full.yaml
4. Paste content from GitHub (see Option 2, steps 1-3)
5. Save file
6. Restart Home Assistant or reload automations


VERIFICATION:
-------------
After copying, verify in Home Assistant:
- Developer Tools → States → Check sensor.pro3em_total_active_power exists
- Settings → Automations → Look for "PV Miner: Solar Power Control (Full Range)"

================================================================================
EOF

echo ""
echo "Would you like me to attempt SSH copy now? (You'll need to enter password)"
read -p "Press ENTER to try SSH copy, or Ctrl+C to cancel: "

echo ""
echo "Creating automations directory..."
ssh -o StrictHostKeyChecking=no hassio@192.168.1.147 "mkdir -p /config/automations"

echo ""
echo "Copying solar_power_control_full.yaml..."
scp -o StrictHostKeyChecking=no automations/solar_power_control_full.yaml hassio@192.168.1.147:/config/automations/

echo ""
echo "Copying README.md..."
scp -o StrictHostKeyChecking=no automations/README.md hassio@192.168.1.147:/config/automations/

echo ""
echo "=== Files copied successfully! ==="
echo "Location: /config/automations/ on Home Assistant"
echo ""
echo "Next: Add the automation in Home Assistant UI"
echo "      Settings → Automations & Scenes → Create Automation → Edit in YAML"
