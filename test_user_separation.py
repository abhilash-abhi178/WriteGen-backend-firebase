"""
Test script to verify user-specific data separation.
Run this after starting the backend server.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_user_separation():
    print("🧪 Testing user-specific data separation\n")
    
    # Create two test users
    print("1. Creating User A...")
    user_a_data = {
        "email": "usera@test.com",
        "password": "password123",
        "display_name": "User A"
    }
    resp_a = requests.post(f"{BASE_URL}/auth/signup", json=user_a_data)
    if resp_a.status_code == 200:
        token_a = resp_a.json()["access_token"]
        print(f"   ✓ User A created. Token: {token_a[:20]}...")
    else:
        print(f"   ✗ Failed: {resp_a.text}")
        return
    
    print("\n2. Creating User B...")
    user_b_data = {
        "email": "userb@test.com",
        "password": "password456",
        "display_name": "User B"
    }
    resp_b = requests.post(f"{BASE_URL}/auth/signup", json=user_b_data)
    if resp_b.status_code == 200:
        token_b = resp_b.json()["access_token"]
        print(f"   ✓ User B created. Token: {token_b[:20]}...")
    else:
        print(f"   ✗ Failed: {resp_b.text}")
        return
    
    # Get User A profile
    print("\n3. Fetching User A profile...")
    profile_a = requests.get(
        f"{BASE_URL}/auth/profile",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    if profile_a.status_code == 200:
        data = profile_a.json()
        print(f"   ✓ Name: {data['name']}, Email: {data['email']}")
    else:
        print(f"   ✗ Failed: {profile_a.text}")
    
    # Get User B profile
    print("\n4. Fetching User B profile...")
    profile_b = requests.get(
        f"{BASE_URL}/auth/profile",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    if profile_b.status_code == 200:
        data = profile_b.json()
        print(f"   ✓ Name: {data['name']}, Email: {data['email']}")
    else:
        print(f"   ✗ Failed: {profile_b.text}")
    
    # Get User A dashboard stats
    print("\n5. Fetching User A dashboard stats...")
    stats_a = requests.get(
        f"{BASE_URL}/dashboard/stats",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    if stats_a.status_code == 200:
        print(f"   ✓ Stats: {json.dumps(stats_a.json(), indent=6)}")
    else:
        print(f"   ✗ Failed: {stats_a.text}")
    
    # Get User B dashboard stats
    print("\n6. Fetching User B dashboard stats...")
    stats_b = requests.get(
        f"{BASE_URL}/dashboard/stats",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    if stats_b.status_code == 200:
        print(f"   ✓ Stats: {json.dumps(stats_b.json(), indent=6)}")
    else:
        print(f"   ✗ Failed: {stats_b.text}")
    
    print("\n✅ User separation test complete!")
    print("\nEach user should only see their own data.")
    print("Upload samples or create documents for each user to verify further.")

if __name__ == "__main__":
    test_user_separation()
