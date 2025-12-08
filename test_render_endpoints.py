#!/usr/bin/env python3
"""Test if endpoints exist on Render"""

import requests
import json

BACKEND_URL = "https://writegen-backend-firebase.onrender.com"

print("Testing Render Backend Endpoints")
print("=" * 60)

# Test 1: Root endpoint
print("\n1. Testing root endpoint...")
try:
    resp = requests.get(f"{BACKEND_URL}/", timeout=10)
    print(f"   Status: {resp.status_code}")
    print(f"   Response: {resp.json()}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Check if signup endpoint exists
print("\n2. Testing POST /api/auth/signup (should exist)...")
try:
    resp = requests.post(
        f"{BACKEND_URL}/api/auth/signup",
        json={
            "name": "Test",
            "display_name": "Tester",
            "email": "test@example.com",
            "password": "Test@123"
        },
        timeout=10
    )
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 404:
        print(f"   ✗ Endpoint NOT FOUND - Server may not have latest code")
    else:
        print(f"   Response: {resp.text[:200]}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Check if login endpoint exists
print("\n3. Testing POST /api/auth/login (should exist)...")
try:
    resp = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "test"
        },
        timeout=10
    )
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 404:
        print(f"   ✗ Endpoint NOT FOUND - Server may not have latest code")
    else:
        print(f"   Response: {resp.text[:200]}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
