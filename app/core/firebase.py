import json
import os
import urllib.parse
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

    # Fallback: construct minimal service account dict from individual env vars
    client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
    private_key = os.getenv("FIREBASE_PRIVATE_KEY")
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    if client_email and private_key and project_id:
        # private_key from env may contain literal '\n' sequences; convert them to actual newlines
        normalized_key = private_key.replace("\\n", "\n")
        # Build a full-service-account-like dict expected by google-auth
        client_x509_url = f"https://www.googleapis.com/robot/v1/metadata/x509/{urllib.parse.quote(client_email)}"
        return {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": "",
            "private_key": normalized_key,
            "client_email": client_email,
            "client_id": "",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": client_x509_url,
        }

    # If no credentials found and we're in development, return None to use mocks
    if os.getenv("ENVIRONMENT") in ["development", "local", "test"]:
        return None
    
    raise Exception(
        "Missing Firebase credentials. Set FIREBASE_CREDENTIALS_JSON (JSON string) or FIREBASE_CREDENTIALS_PATH/GOOGLE_APPLICATION_CREDENTIALS (path to JSON file)."
    )


firebase_creds = _load_firebase_credentials()

# Initialize Firebase only if credentials are provided
db = None
bucket = None

if firebase_creds:
    try:
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
        print("✓ Firebase initialized successfully")
    except Exception as e:
        print(f"⚠ Firebase initialization failed: {e}. Using mock implementations.")
        firebase_creds = None

# Create mock implementations if Firebase is not available
if not firebase_creds or not db or not bucket:
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Using mock Firebase implementations for development")
    
    class MockFirestoreDB:
        """Mock Firestore database for development."""
        def __init__(self):
            self._data = {}
        
        def collection(self, name):
            if name not in self._data:
                self._data[name] = {}
            return MockCollection(self._data[name])
    
    class MockCollection:
        """Mock Firestore collection."""
        def __init__(self, data):
            self.data = data
        
        def document(self, doc_id=None):
            return MockDocument(self.data, doc_id)
        
        def where(self, field, op, value):
            return MockQuery(self.data, field, op, value)
    
    class MockDocument:
        """Mock Firestore document."""
        def __init__(self, collection, doc_id=None):
            self.collection = collection
            self.doc_id = doc_id
        
        def get(self):
            if self.doc_id and self.doc_id in self.collection:
                return MockSnapshot(self.collection[self.doc_id], self.doc_id)
            return MockSnapshot(None, self.doc_id)
        
        def set(self, data):
            if not self.doc_id:
                import uuid
                self.doc_id = uuid.uuid4().hex
            self.collection[self.doc_id] = data
        
        def update(self, data):
            if self.doc_id and self.doc_id in self.collection:
                self.collection[self.doc_id].update(data)
        
        def delete(self):
            if self.doc_id and self.doc_id in self.collection:
                del self.collection[self.doc_id]
        
        @property
        def id(self):
            if not self.doc_id:
                import uuid
                self.doc_id = uuid.uuid4().hex
            return self.doc_id
    
    class MockSnapshot:
        """Mock document snapshot."""
        def __init__(self, data, doc_id):
            self.data_dict = data
            self.doc_id = doc_id
        
        def exists(self):
            return self.data_dict is not None
        
        def to_dict(self):
            return self.data_dict or {}
        
        @property
        def id(self):
            return self.doc_id
    
    class MockQuery:
        """Mock query."""
        def __init__(self, data, field, op, value):
            self.data = data
            self.field = field
            self.op = op
            self.value = value
        
        def stream(self):
            results = []
            for doc_id, doc_data in self.data.items():
                if self._match(doc_data):
                    results.append(MockSnapshot(doc_data, doc_id))
            return results
        
        def _match(self, doc_data):
            val = doc_data.get(self.field)
            if self.op == "==":
                return val == self.value
            return False
    
    class MockBucket:
        """Mock storage bucket."""
        def __init__(self):
            self._files = {}
        
        def blob(self, name):
            return MockBlob(self._files, name)
    
    class MockBlob:
        """Mock storage blob."""
        def __init__(self, files, name):
            self.files = files
            self.name = name
            self.public_url = f"http://localhost:8000/files/{name}"
        
        def upload_from_filename(self, filename):
            try:
                with open(filename, 'rb') as f:
                    self.files[self.name] = f.read()
            except Exception as e:
                logger.error(f"Failed to upload: {e}")
        
        def download_to_filename(self, filename):
            try:
                if self.name in self.files:
                    with open(filename, 'wb') as f:
                        f.write(self.files[self.name])
            except Exception as e:
                logger.error(f"Failed to download: {e}")
        
        def make_public(self):
            pass
        
        def delete(self):
            if self.name in self.files:
                del self.files[self.name]
    
    if not db:
        db = MockFirestoreDB()
    if not bucket:
        bucket = MockBucket()



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
