import json
import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud import storage

# Load Firebase JSON from environment variable
firebase_creds_raw = os.getenv("FIREBASE_CREDENTIALS_JSON")
if not firebase_creds_raw:
    raise Exception("Missing FIREBASE_CREDENTIALS_JSON environment variable")

firebase_creds = json.loads(firebase_creds_raw)

# Initialize Firebase using certificate dict
cred = credentials.Certificate(firebase_creds)

# App init (with storage bucket)
firebase_admin.initialize_app(cred, {
    "storageBucket": f"{firebase_creds['project_id']}.appspot.com"
})

# Firestore client
db = firestore.client()

# Storage client (explicitly pass credentials)
storage_client = storage.Client(
    project=firebase_creds["project_id"],
    credentials=cred.get_credential()
)

bucket = storage_client.bucket(f"{firebase_creds['project_id']}.appspot.com")


# ---------------------------------------------------------
# FUNCTIONS REQUIRED BY YOUR ROUTES
# ---------------------------------------------------------

def verify_id_token(token: str):
    """
    Verifies Firebase ID Token sent by Android app.
    Returns decoded user info or raises error.
    """
    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception as e:
        raise Exception(f"Invalid Firebase ID token: {e}")


def user_doc_ref(uid: str):
    """
    Returns Firestore document reference for the user.
    Used in multiple route files.
    """
    return db.collection("users").document(uid)
