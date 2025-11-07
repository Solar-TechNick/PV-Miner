#!/bin/bash
# Upload automation files to Home Assistant

HOST="192.168.1.147"
USER="hassio"
PASS="hassio"

echo "=== Uploading automation files to Home Assistant ==="
echo "Target: $USER@$HOST"
echo ""

# Method 1: Try with ssh-copy using password
# This creates the directory and copies files
(
echo "$PASS"
sleep 1
echo "mkdir -p /config/automations"
sleep 1
echo "exit"
) | ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $USER@$HOST 2>/dev/null

# Now copy the files using SCP
echo "Copying solar_power_control_full.yaml..."
(
echo "$PASS"
) | scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    automations/solar_power_control_full.yaml \
    $USER@$HOST:/config/automations/ 2>&1

echo "Copying README.md..."
(
echo "$PASS"
) | scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    automations/README.md \
    $USER@$HOST:/config/automations/ 2>&1

echo ""
echo "=== Upload complete! ==="
echo "Files uploaded to /config/automations/ on Home Assistant"
echo ""
echo "Next steps in Home Assistant:"
echo "1. Go to Settings → Automations & Scenes"
echo "2. Click 'Create Automation' → 'Edit in YAML'"
echo "3. Paste the contents of /config/automations/solar_power_control_full.yaml"
echo "4. Save the automation"
