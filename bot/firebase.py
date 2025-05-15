import os
import json

from datetime import datetime, timedelta, timezone
import firebase_admin
from firebase_admin import credentials, firestore

# === BEGIN: Load credentials from ENV ===
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
if not firebase_credentials:
    raise ValueError("Missing FIREBASE_CREDENTIALS env variable")
cred = credentials.Certificate(json.loads(firebase_credentials))
# === END ===

# === Initialize app ===
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()


# Function to save a booking session
def save_booking_session(user_id, chat_id):
    doc_ref = db.collection("sessions").document(str(user_id))
    doc_ref.set(
        {
            "user_id": user_id,
            "chat_id": chat_id,
            "timestamp": datetime.now(timezone.utc),
        }
    )


# Function to get a booking session
def get_booking_session(user_id):
    doc = db.collection("sessions").document(str(user_id)).get()
    if doc.exists:
        data = doc.to_dict()
        if datetime.utcnow() - data["timestamp"] <= timedelta(weeks=2):
            return data
    return None


# Aliases for compatibility with cases.py
save_user_info = save_booking_session
get_user_chat_info = get_booking_session

__all__ = [
    "save_booking_session",
    "get_booking_session",
    "save_user_info",
    "get_user_chat_info",
]
