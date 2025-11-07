#!/usr/bin/env python3
"""
Fetch Home Assistant logs via REST API to diagnose hashboard control issues.
"""
import asyncio
import aiohttp
import sys

async def fetch_ha_logs():
    """Fetch logs from Home Assistant."""
    HA_HOST = input("Enter Home Assistant IP (default: 192.168.1.147): ").strip() or "192.168.1.147"
    HA_PORT = input("Enter Home Assistant port (default: 8123): ").strip() or "8123"
    HA_TOKEN = input("Enter Home Assistant long-lived access token (leave empty to try without auth): ").strip()

    base_url = f"http://{HA_HOST}:{HA_PORT}"

    headers = {}
    if HA_TOKEN:
        headers["Authorization"] = f"Bearer {HA_TOKEN}"
        headers["Content-Type"] = "application/json"

    print(f"\n{'='*80}")
    print(f"Fetching logs from {base_url}")
    print(f"{'='*80}\n")

    async with aiohttp.ClientSession() as session:
        # Try to fetch error logs
        try:
            print("Fetching error log...")
            async with session.get(f"{base_url}/api/error_log", headers=headers) as response:
                if response.status == 200:
                    text = await response.text()

                    # Filter for PV Miner related logs
                    lines = text.split('\n')
                    pv_miner_lines = [line for line in lines if 'pv_miner' in line.lower() or 'hashboard' in line.lower()]

                    if pv_miner_lines:
                        print(f"\nFound {len(pv_miner_lines)} PV Miner related log entries:\n")
                        print('\n'.join(pv_miner_lines[-50:]))  # Last 50 entries
                    else:
                        print("No PV Miner related logs found in error log.")
                        print("\nShowing last 20 lines of error log:")
                        print('\n'.join(lines[-20:]))
                else:
                    print(f"Failed to fetch error log: HTTP {response.status}")
                    error_text = await response.text()
                    print(f"Response: {error_text[:500]}")
        except Exception as e:
            print(f"Error fetching logs: {e}")

        # Try to get state of hashboard switches
        print(f"\n{'='*80}")
        print("Checking hashboard switch states...")
        print(f"{'='*80}\n")

        try:
            async with session.get(f"{base_url}/api/states", headers=headers) as response:
                if response.status == 200:
                    states = await response.json()

                    # Find all PV Miner entities
                    pv_entities = [s for s in states if 'pv_miner' in s.get('entity_id', '')]

                    print(f"Found {len(pv_entities)} PV Miner entities:\n")

                    for entity in pv_entities:
                        entity_id = entity.get('entity_id', 'unknown')
                        state = entity.get('state', 'unknown')
                        friendly_name = entity.get('attributes', {}).get('friendly_name', 'unknown')

                        if 'hashboard' in entity_id:
                            print(f"  {friendly_name} ({entity_id}): {state}")
                else:
                    print(f"Failed to fetch states: HTTP {response.status}")
        except Exception as e:
            print(f"Error fetching states: {e}")

        # Provide instructions for creating long-lived token
        if not HA_TOKEN or response.status == 401:
            print(f"\n{'='*80}")
            print("To create a long-lived access token:")
            print("1. Open Home Assistant web UI")
            print("2. Click your profile icon (bottom left)")
            print("3. Scroll down to 'Long-Lived Access Tokens'")
            print("4. Click 'Create Token'")
            print("5. Give it a name like 'API Access'")
            print("6. Copy the token and run this script again")
            print(f"{'='*80}\n")

if __name__ == "__main__":
    print("=== Home Assistant Log Fetcher ===\n")
    asyncio.run(fetch_ha_logs())
