import json
import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud import storage

# Load Firebase JSON from environment
firebase_creds_raw = os.getenv("FIREBASE_CREDENTIALS_JSON")

if not firebase_creds_raw:
    raise Exception("Missing FIREBASE_CREDENTIALS_JSON environment variable")

firebase_creds = json.loads(firebase_creds_raw)

# Use certificate from dict (not file)
cred = credentials.Certificate(firebase_creds)

# Initialize Firebase
firebase_admin.initialize_app(cred, {
    "storageBucket": f"{firebase_creds['project_id']}.appspot.com",
})

# Firestore
db = firestore.client()

# Storage client using SAME credentials
storage_client = storage.Client(
    project=firebase_creds["project_id"],
    credentials=cred.get_credential(),
)

bucket = storage_client.bucket(f"{firebase_creds['project_id']}.appspot.com")
