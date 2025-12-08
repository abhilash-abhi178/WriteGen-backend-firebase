# app/core/mock_db.py
"""
Mock database for development/testing without Firebase.
Replace this with real Firebase when ready.
"""

from datetime import datetime
from typing import Dict, List, Optional
import uuid

class MockDocument:
    """Mock Firestore document."""
    def __init__(self, doc_id: str, data: dict):
        self.id = doc_id
        self._data = data
    
    def to_dict(self):
        return self._data.copy()
    
    @property
    def exists(self):
        return True
    
    def get(self, key, default=None):
        return self._data.get(key, default)


class MockCollection:
    """Mock Firestore collection."""
    def __init__(self, name: str, db_store: dict):
        self.name = name
        self.db_store = db_store
        if name not in self.db_store:
            self.db_store[name] = {}
    
    def document(self, doc_id: str = None):
        if doc_id is None:
            doc_id = str(uuid.uuid4())
        return MockDocumentRef(doc_id, self)
    
    def where(self, field: str, op: str, value):
        """Filter documents."""
        class QueryResult:
            def __init__(self, collection, field, op, value):
                self.collection = collection
                self.field = field
                self.op = op
                self.value = value
            
            def stream(self):
                results = []
                for doc_id, doc_data in self.collection.db_store[self.collection.name].items():
                    if self.op == "==":
                        if doc_data.get(self.field) == self.value:
                            results.append(MockDocument(doc_id, doc_data))
                return results
            
            def where(self, field: str, op: str, value):
                """Chain where clauses."""
                filtered = []
                for doc in self.stream():
                    doc_data = doc.to_dict()
                    if op == "==":
                        if doc_data.get(field) == value:
                            filtered.append(doc)
                
                class ChainedResult:
                    def __init__(self, docs):
                        self.docs = docs
                    def stream(self):
                        return self.docs
                
                return ChainedResult(filtered)
        
        return QueryResult(self, field, op, value)
    
    def stream(self):
        """Get all documents."""
        return [MockDocument(doc_id, data) 
                for doc_id, data in self.db_store[self.name].items()]


class MockDocumentRef:
    """Mock Firestore document reference."""
    def __init__(self, doc_id: str, collection: MockCollection):
        self.id = doc_id
        self.collection = collection
    
    def set(self, data: dict):
        """Set document data."""
        self.collection.db_store[self.collection.name][self.id] = data.copy()
    
    def update(self, data: dict):
        """Update document data."""
        if self.id in self.collection.db_store[self.collection.name]:
            self.collection.db_store[self.collection.name][self.id].update(data)
    
    def get(self):
        """Get document."""
        if self.id in self.collection.db_store[self.collection.name]:
            data = self.collection.db_store[self.collection.name][self.id]
            return MockDocument(self.id, data)
        
        class EmptyDoc:
            exists = False
            def to_dict(self):
                return {}
        return EmptyDoc()
    
    def delete(self):
        """Delete document."""
        if self.id in self.collection.db_store[self.collection.name]:
            del self.collection.db_store[self.collection.name][self.id]


class MockDB:
    """Mock Firestore database."""
    def __init__(self):
        self._store = {}
    
    def collection(self, name: str):
        return MockCollection(name, self._store)


class MockBlob:
    """Mock Cloud Storage blob."""
    def __init__(self, path: str, bucket):
        self.path = path
        self.bucket = bucket
        self.public_url = f"http://localhost:8000/storage/{path}"
    
    def upload_from_filename(self, filename: str):
        """Mock upload."""
        import os
        if os.path.exists(filename):
            self.bucket._files[self.path] = filename
    
    def make_public(self):
        """Mock make public."""
        pass
    
    def delete(self):
        """Mock delete."""
        if self.path in self.bucket._files:
            del self.bucket._files[self.path]


class MockBucket:
    """Mock Cloud Storage bucket."""
    def __init__(self, name: str):
        self.name = name
        self._files = {}
    
    def blob(self, path: str):
        return MockBlob(path, self)


# Global instances
mock_db = MockDB()
mock_bucket = MockBucket("writegen-mock")

print("✓ Mock database initialized (in-memory storage)")
