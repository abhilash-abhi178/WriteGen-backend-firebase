import json
import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud import storage


# Helper: load credentials JSON from either env JSON or a file path
def _load_firebase_credentials() -> dict:
    raw = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            raise Exception("Invalid JSON in FIREBASE_CREDENTIALS_JSON environment variable")

    # Try a credentials file path provided specifically for this app
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path and os.path.exists(cred_path):
        try:
            with open(cred_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to read Firebase credentials file '{cred_path}': {e}")

    raise Exception(
        "Missing Firebase credentials. Set FIREBASE_CREDENTIALS_JSON (JSON string) or FIREBASE_CREDENTIALS_PATH/GOOGLE_APPLICATION_CREDENTIALS (path to JSON file)."
    )


firebase_creds = _load_firebase_credentials()

# Initialize Firebase using certificate dict
cred = credentials.Certificate(firebase_creds)

# Avoid double-initialization in environments that reuse processes
if not firebase_admin._apps:
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
