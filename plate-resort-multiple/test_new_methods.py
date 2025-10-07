#!/usr/bin/env python3
"""
Test the new move_to_angle and get_position methods
"""

from plate_resort.client.cli import PlateResortClient

def test_new_methods():
    # Connect to your Pi server
    client = PlateResortClient(
        api_url="http://100.83.140.57:8000",
        api_key="your-secret-api-key-2024"
    )
    
    print("🔍 Testing new methods...")
    
    try:
        # Test move to angle
        print("\n1. Testing move_to_angle:")
        result = client.move_to_angle(45.0)
        print(f"   Result: {result}")
        
    except Exception as e:
        print(f"❌ move_to_angle failed: {e}")
        print("   This is expected if the server doesn't have the new code yet.")
    
    try:
        # Test get position 
        print("\n2. Testing get_position:")
        result = client.get_position()
        print(f"   Result: {result}")
        
    except Exception as e:
        print(f"❌ get_position failed: {e}")
        print("   This is expected if the server doesn't have the new code yet.")
        
    print("\n💡 To use these new methods, you need to:")
    print("   1. Update the code on your Pi")
    print("   2. Restart the server")
    print("   3. Or install the new package version on the Pi")

if __name__ == "__main__":
    test_new_methods()