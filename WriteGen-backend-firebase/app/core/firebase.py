import json
import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud import storage
import os

# Read service account JSON from environment variable
firebase_creds = os.getenv("FIREBASE_CREDENTIALS_JSON")

if not firebase_creds:
    raise Exception("Missing FIREBASE_CREDENTIALS_JSON environment variable")

# Convert JSON string to Python dict
firebase_creds_dict = json.loads(firebase_creds)

# Initialize Firebase app
cred = credentials.Certificate(firebase_creds_dict)
firebase_admin.initialize_app(cred)

db = firestore.client()
storage_client = storage.Client()
