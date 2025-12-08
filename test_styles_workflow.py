#!/usr/bin/env python3
"""Test handwriting styles workflow"""

import requests
import json
import uuid
from datetime import datetime
from PIL import Image
import io

BASE_URL = "http://localhost:8000"
test_user = f"test_user_{uuid.uuid4().hex[:8]}"
test_password = "Test@123"

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (200, 100), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def test_styles_workflow():
    print("🧪 Testing Handwriting Styles Workflow")
    print("=" * 60)
    
    # 1️⃣  Create user and upload samples
    print("\n1️⃣  Creating test user...")
    signup_resp = requests.post(
        f"{BASE_URL}/api/auth/signup",
        json={
            "name": "Style Test User",
            "display_name": "Style Tester",
            "email": test_user + "@example.com",
            "password": test_password
        }
    )
    if signup_resp.status_code not in [200, 201]:
        print(f"   ✗ Signup failed: {signup_resp.text}")
        return
    
    token = signup_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   ✓ User created")
    
    # 2️⃣  Upload handwriting samples
    print("\n2️⃣  Uploading handwriting samples...")
    files = [
        ('files', ('sample_1.jpg', create_test_image(), 'image/jpeg')),
        ('files', ('sample_2.jpg', create_test_image(), 'image/jpeg')),
        ('files', ('sample_3.jpg', create_test_image(), 'image/jpeg')),
    ]
    upload_resp = requests.post(
        f"{BASE_URL}/api/samples/upload",
        files=files,
        headers=headers
    )
    if upload_resp.status_code not in [200, 201]:
        print(f"   ✗ Upload failed: {upload_resp.text}")
        return
    
    upload_data = upload_resp.json()
    sample_ids = [s.get('id') for s in upload_data.get('samples', [])]
    print(f"   ✓ Uploaded {len(sample_ids)} samples")
    
    # 3️⃣  Create style from samples
    print("\n3️⃣  Creating handwriting style...")
    style_resp = requests.post(
        f"{BASE_URL}/api/styles/create",
        json={
            "sample_ids": sample_ids,
            "style_name": "Test Handwriting Style"
        },
        headers=headers
    )
    if style_resp.status_code not in [200, 201, 202]:
        print(f"   ✗ Style creation failed: {style_resp.status_code}")
        print(f"   {style_resp.text}")
        return
    
    style_data = style_resp.json()
    style_id = style_data.get('style_id') or style_data.get('id')
    print(f"   ✓ Style created successfully")
    print(f"   Style ID: {style_id}")
    print(f"   Status: {style_data.get('status')}")
    print(f"   Confidence: {style_data.get('confidence')}")
    
    # 4️⃣  List all styles
    print("\n4️⃣  Listing user's styles...")
    list_resp = requests.get(
        f"{BASE_URL}/api/styles/",
        headers=headers
    )
    if list_resp.status_code == 200:
        styles = list_resp.json()
        if isinstance(styles, dict):
            styles = styles.get('styles', [])
        print(f"   ✓ Found {len(styles)} styles")
        for style in styles:
            print(f"      - {style.get('name')} (ID: {style.get('id', style.get('style_id'))[:8]}...)")
    else:
        print(f"   ✗ Failed to list styles: {list_resp.text}")
    
    # 5️⃣  Get specific style
    print(f"\n5️⃣  Fetching style details (ID: {style_id[:8]}...)...")
    detail_resp = requests.get(
        f"{BASE_URL}/api/styles/{style_id}",
        headers=headers
    )
    if detail_resp.status_code == 200:
        style_detail = detail_resp.json()
        print(f"   ✓ Style retrieved")
        print(f"   Name: {style_detail.get('name')}")
        print(f"   Status: {style_detail.get('status')}")
        print(f"   Sample Count: {len(style_detail.get('sample_ids', []))}")
        print(f"   Character Count: {style_detail.get('character_count')}")
    else:
        print(f"   ✗ Failed to get style: {detail_resp.text}")
    
    # 6️⃣  Create document with style
    print("\n6️⃣  Creating document with handwriting style...")
    doc_resp = requests.post(
        f"{BASE_URL}/api/generate/create",
        json={
            "title": "Document with Style",
            "content": "This is test content for handwriting generation",
            "style_id": style_id,
            "page_count": 1
        },
        headers=headers
    )
    if doc_resp.status_code in [200, 201, 202]:
        doc_data = doc_resp.json()
        doc_id = doc_data.get('id') or doc_data.get('document_id')
        print(f"   ✓ Document created")
        print(f"   Document ID: {doc_id}")
        print(f"   Status: {doc_data.get('status')}")
    else:
        print(f"   ✗ Document creation failed: {doc_resp.text}")
    
    # 7️⃣  Check profile for style status
    print("\n7️⃣  Verifying profile style status...")
    profile_resp = requests.get(
        f"{BASE_URL}/api/auth/profile",
        headers=headers
    )
    if profile_resp.status_code == 200:
        profile = profile_resp.json()
        print(f"   ✓ Profile retrieved")
        print(f"   Has Style Profile: {profile.get('hasStyleProfile')}")
        print(f"   Style Status: {profile.get('style_status', 'N/A')}")
    else:
        print(f"   ✗ Profile fetch failed: {profile_resp.text}")
    
    print("\n" + "=" * 60)
    print("✅ Style workflow test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_styles_workflow()
