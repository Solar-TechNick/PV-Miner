#!/usr/bin/env python3
"""Test the new dynamic profile system."""
import asyncio
import sys
import os

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def test_dynamic_profiles():
    """Test the new dynamic profile system."""
    host = "192.168.99.202"
    username = "root"
    password = "root"
    
    print(f"🔍 Testing dynamic profile system on {host}")
    
    api = LuxOSAPI(host, username, password)
    
    try:
        print("\n1. Testing connection...")
        connected = await api.test_connection()
        if not connected:
            print("❌ Cannot connect to miner!")
            return
        print(f"✅ Connected with session: {api._luxos_session_id}")
        
        print("\n2. Testing get_available_profiles()...")
        profiles = await api.get_available_profiles()
        print(f"✅ Found {len(profiles)} profiles: {profiles[:10]}...")  # Show first 10
        
        print("\n3. Testing get_all_profiles_with_details()...")
        profile_details = await api.get_all_profiles_with_details()
        print(f"✅ Got detailed info for {len(profile_details)} profiles")
        
        # Show some examples
        example_profiles = ["310MHz", "default", "560MHz", "810MHz"]
        for profile in example_profiles:
            if profile in profile_details:
                details = profile_details[profile]
                print(f"   {profile}: {details['description']}")
        
        print("\n4. Testing profile switching...")
        test_profiles = ["310MHz", "default"]
        
        for profile in test_profiles:
            try:
                print(f"   Setting profile to '{profile}'...")
                result = await api.set_profile(profile)
                print(f"   ✅ Success: {result['STATUS'][0]['Msg'] if 'STATUS' in result else 'OK'}")
                await asyncio.sleep(1)  # Brief pause between profile changes
            except Exception as e:
                print(f"   ❌ Failed to set {profile}: {e}")
        
        print("\n✅ Dynamic profile system test completed!")
        print(f"Your miner now has {len(profiles)} available profiles instead of fixed ones!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(test_dynamic_profiles())