#!/usr/bin/env python3
"""Test dynamic profiles with miner awake."""
import asyncio
import sys
import os

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def test_profiles_awake():
    """Test profiles with miner in awake state."""
    host = "192.168.99.202"
    username = "root"
    password = "root"
    
    print(f"🔍 Testing profile switching with awake miner on {host}")
    
    api = LuxOSAPI(host, username, password)
    
    try:
        print("\n1. Connecting and waking miner...")
        connected = await api.test_connection()
        if not connected:
            print("❌ Cannot connect!")
            return
            
        # Wake up the miner first
        await api.resume_mining()
        print("✅ Miner woken up")
        
        # Wait a moment for miner to be ready
        await asyncio.sleep(3)
        
        print("\n2. Testing profile switching...")
        test_profiles = ["310MHz", "default", "560MHz"]
        
        for profile in test_profiles:
            try:
                print(f"   Setting profile to '{profile}'...")
                result = await api.set_profile(profile)
                print(f"   ✅ Success: {result['STATUS'][0]['Msg'] if 'STATUS' in result else 'OK'}")
                await asyncio.sleep(2)  # Brief pause between profile changes
            except Exception as e:
                print(f"   ❌ Failed to set {profile}: {e}")
        
        print(f"\n3. Available profiles summary:")
        profile_details = await api.get_all_profiles_with_details()
        
        # Group profiles by power ranges for better overview
        low_power = []
        medium_power = []
        high_power = []
        
        for name, details in profile_details.items():
            watts = details.get('watts', 0)
            if watts < 3000:
                low_power.append(f"{name} ({watts}W)")
            elif watts < 5000:
                medium_power.append(f"{name} ({watts}W)")
            else:
                high_power.append(f"{name} ({watts}W)")
        
        print(f"   🔋 Low Power (< 3000W): {low_power[:5]}...")
        print(f"   ⚡ Medium Power (3000-5000W): {medium_power[:5]}...")
        print(f"   🔥 High Power (> 5000W): {high_power[:5]}...")
        
        print(f"\n✅ Total: {len(profile_details)} dynamic profiles available!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(test_profiles_awake())