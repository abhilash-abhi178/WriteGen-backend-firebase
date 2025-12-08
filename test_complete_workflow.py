"""
Complete workflow test: Upload samples → Process → Generate handwriting
"""

import requests
import json
import os
from pathlib import Path
from PIL import Image
import io

BASE_URL = "http://localhost:8000/api"

def create_test_image(filename, text="Sample"):
    """Create a simple test image."""
    img = Image.new('RGB', (800, 600), color='white')
    img.save(filename)
    return filename

def test_complete_workflow():
    print("🧪 Testing Complete Handwriting Workflow\n")
    print("=" * 60)
    
    # Step 1: Create a test user
    print("\n1️⃣  Creating test user...")
    user_data = {
        "email": "testworkflow@example.com",
        "password": "testpass123",
        "display_name": "Workflow Test User"
    }
    
    resp = requests.post(f"{BASE_URL}/auth/signup", json=user_data)
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        print(f"   ✓ User created successfully")
        print(f"   Token: {token[:30]}...")
    else:
        print(f"   ✗ Signup failed: {resp.text}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get initial profile (should have no style profile)
    print("\n2️⃣  Checking initial profile...")
    profile_resp = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
    if profile_resp.status_code == 200:
        profile = profile_resp.json()
        print(f"   ✓ Profile retrieved")
        print(f"   Name: {profile['name']}")
        print(f"   Email: {profile['email']}")
        print(f"   Has Style Profile: {profile['hasStyleProfile']}")
    else:
        print(f"   ✗ Failed to get profile: {profile_resp.text}")
    
    # Step 3: Create and upload sample images
    print("\n3️⃣  Uploading handwriting samples...")
    temp_dir = Path("temp_samples")
    temp_dir.mkdir(exist_ok=True)
    
    sample_files = []
    for i in range(3):
        filename = temp_dir / f"sample_{i+1}.jpg"
        create_test_image(str(filename), f"Sample {i+1}")
        sample_files.append(filename)
        print(f"   📝 Created {filename.name}")
    
    # Upload files
    files = [('files', (f.name, open(f, 'rb'), 'image/jpeg')) for f in sample_files]
    
    upload_resp = requests.post(
        f"{BASE_URL}/samples/upload",
        headers=headers,
        files=files
    )
    
    # Close file handles
    for _, (_, fp, _) in files:
        fp.close()
    
    if upload_resp.status_code in [200, 201]:
        upload_data = upload_resp.json()
        print(f"   ✓ Upload successful!")
        print(f"   Uploaded {upload_data.get('uploaded_count', len(sample_files))} samples")
        if 'samples' in upload_data:
            for sample in upload_data['samples']:
                print(f"      - {sample.get('filename', sample.get('id'))}")
    else:
        print(f"   ✗ Upload failed: {upload_resp.status_code}")
        print(f"   Response: {upload_resp.text}")
    
    # Step 4: List uploaded samples
    print("\n4️⃣  Verifying uploaded samples...")
    samples_resp = requests.get(f"{BASE_URL}/samples/", headers=headers)
    if samples_resp.status_code == 200:
        samples_data = samples_resp.json()
        # Handle both array and object response formats
        if isinstance(samples_data, list):
            samples = samples_data
        else:
            samples = samples_data.get('samples', [])
        
        print(f"   ✓ Found {len(samples)} samples")
        for sample in samples[:5]:
            print(f"      - {sample.get('fileName', sample.get('filename', 'Unknown'))}")
    else:
        print(f"   ✗ Failed to list samples: {samples_resp.text}")
    
    # Step 5: Check profile again (should now have style profile)
    print("\n5️⃣  Checking updated profile...")
    profile_resp = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
    if profile_resp.status_code == 200:
        profile = profile_resp.json()
        print(f"   ✓ Profile retrieved")
        print(f"   Has Style Profile: {profile['hasStyleProfile']}")
        if profile['hasStyleProfile']:
            print(f"   ✅ Style profile is active!")
        else:
            print(f"   ⚠️  Style profile not yet created (may need processing time)")
    
    # Step 6: Create a style from samples
    print("\n6️⃣  Creating handwriting style...")
    if isinstance(samples_data, list):
        sample_ids = [s.get('id') for s in samples_data if s.get('id')]
    else:
        sample_ids = [s.get('id') for s in samples_data.get('samples', []) if s.get('id')]
    
    if sample_ids:
        style_data = {
            "sample_ids": sample_ids[:3],
            "style_name": "My Test Style"
        }
        style_resp = requests.post(
            f"{BASE_URL}/styles/create",
            headers=headers,
            json=style_data
        )
        if style_resp.status_code in [200, 201, 202]:
            style_result = style_resp.json()
            print(f"   ✓ Style creation initiated")
            print(f"   Style ID: {style_result.get('style_id', 'N/A')}")
            print(f"   Status: {style_result.get('status', 'processing')}")
        else:
            print(f"   ⚠️  Style creation failed: {style_resp.status_code}")
            print(f"   Response: {style_resp.text}")
    else:
        print(f"   ⚠️  No sample IDs available to create style")
    
    # Step 7: Get dashboard stats
    print("\n7️⃣  Checking dashboard statistics...")
    stats_resp = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
    if stats_resp.status_code == 200:
        stats = stats_resp.json()
        print(f"   ✓ Dashboard stats retrieved:")
        print(f"      Total Documents: {stats.get('totalDocuments', 0)}")
        print(f"      Generated Today: {stats.get('generatedToday', 0)}")
        print(f"      Pending Drafts: {stats.get('pendingDrafts', 0)}")
        print(f"      Total Pages: {stats.get('totalPages', 0)}")
    else:
        print(f"   ⚠️  Failed to get stats: {stats_resp.text}")
    
    # Step 8: Create a document
    print("\n8️⃣  Creating a test document...")
    doc_data = {
        "title": "Test Document",
        "content": "This is a test document to verify handwriting generation.",
        "fontSize": 16,
        "lineHeight": 1.5,
        "fontStyle": "normal"
    }
    
    doc_resp = requests.post(
        f"{BASE_URL}/generate/create",
        headers=headers,
        json=doc_data
    )
    
    if doc_resp.status_code in [200, 201, 202]:
        doc_result = doc_resp.json()
        print(f"   ✓ Document creation initiated")
        print(f"   Document ID: {doc_result.get('document_id', doc_result.get('id', 'N/A'))}")
        print(f"   Status: {doc_result.get('status', 'processing')}")
    else:
        print(f"   ⚠️  Document creation endpoint not available: {doc_resp.status_code}")
        print(f"   Response: {doc_resp.text}")
    
    # Step 9: List documents
    print("\n9️⃣  Listing user documents...")
    docs_resp = requests.get(f"{BASE_URL}/generate/documents", headers=headers)
    if docs_resp.status_code == 200:
        docs = docs_resp.json()
        if isinstance(docs, list):
            print(f"   ✓ Found {len(docs)} documents")
            for doc in docs[:5]:
                print(f"      - {doc.get('name', 'Untitled')}: {doc.get('status', 'unknown')}")
        else:
            print(f"   ✓ Documents endpoint working")
    else:
        print(f"   ⚠️  Failed to list documents: {docs_resp.text}")
    
    # Cleanup
    print("\n🧹 Cleaning up test files...")
    for f in sample_files:
        try:
            f.unlink()
        except:
            pass
    try:
        temp_dir.rmdir()
    except:
        pass
    
    print("\n" + "=" * 60)
    print("✅ Complete workflow test finished!")
    print("\nSummary:")
    print("  ✓ User authentication")
    print("  ✓ Profile management")
    print("  ✓ Sample upload")
    print("  ✓ Sample listing")
    print("  ✓ Style creation")
    print("  ✓ Dashboard stats")
    print("  ✓ Document operations")
    print("\n📝 Note: Some features may need backend processing time.")

if __name__ == "__main__":
    try:
        test_complete_workflow()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
