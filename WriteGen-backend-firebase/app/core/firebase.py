# app/core/firebase.py
import os
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from google.cloud import firestore as gcf_firestore

FIREBASE_CREDS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "firebase/firebase-adminsdk.json")
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", None)  # e.g. my-project.appspot.com

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDS_PATH)
    firebase_admin.initialize_app(cred, {
        "storageBucket": FIREBASE_STORAGE_BUCKET
    })

db = firestore.client()
bucket = storage.bucket()

def verify_id_token(id_token: str):
    """
    Verify Firebase ID token, returns decoded token dict or raise Exception.
    """
    try:
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        raise

def user_doc_ref(uid: str):
    return db.collection("users").document(uid)
