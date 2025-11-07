#!/bin/bash
# Script to copy automation files to Home Assistant

HA_HOST="192.168.1.147"
HA_USER="hassio"
HA_PASS="hassio"
HA_CONFIG="/config"

echo "Copying automation files to Home Assistant at $HA_HOST..."

# Create automations directory if it doesn't exist
sshpass -p "$HA_PASS" ssh -o StrictHostKeyChecking=no $HA_USER@$HA_HOST "mkdir -p $HA_CONFIG/automations"

# Copy the full automation file
echo "Copying solar_power_control_full.yaml..."
sshpass -p "$HA_PASS" scp -o StrictHostKeyChecking=no \
    automations/solar_power_control_full.yaml \
    $HA_USER@$HA_HOST:$HA_CONFIG/automations/

# Copy the README
echo "Copying README.md..."
sshpass -p "$HA_PASS" scp -o StrictHostKeyChecking=no \
    automations/README.md \
    $HA_USER@$HA_HOST:$HA_CONFIG/automations/

echo "Done! Files copied to $HA_HOST:$HA_CONFIG/automations/"
echo ""
echo "Next steps:"
echo "1. In Home Assistant, go to Settings → Automations & Scenes"
echo "2. The automation should appear automatically if you have 'automation: !include_dir_merge_list automations/' in configuration.yaml"
echo "3. Otherwise, manually import the YAML from $HA_CONFIG/automations/solar_power_control_full.yaml"
