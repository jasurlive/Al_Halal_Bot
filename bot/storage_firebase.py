# storage_firebase.py

import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "./firestore_botcontrol.json"
    )  # ✅ Replace with your actual path
    firebase_admin.initialize_app(
        cred,
        {
            "databaseURL": "https://jasurlivenew-default-rtdb.firebaseio.com/"  # ✅ Replace with your actual DB URL
        },
    )


def add_user_chat(user_id):
    """Add or update a user chat ID in the database."""
    ref = db.reference("user_chat_dict")
    ref.child(str(user_id)).set(user_id)


def get_user_chat(user_id):
    """Retrieve a user chat ID from the database."""
    ref = db.reference(f"user_chat_dict/{user_id}")
    return ref.get()
