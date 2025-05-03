# firebase.py
import os
import json
import uuid
from datetime import datetime, timedelta
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

# Define bot's unique user ID
BOT_USER_ID = "alhalal_bot"  # You can set this as an environment variable if needed


def save_booking_session(user_id, chat_id):
    if user_id != BOT_USER_ID:
        raise PermissionError(
            "This bot cannot access booking sessions for non-bot users."
        )

    doc_ref = db.collection("sessions").document(str(user_id))
    doc_ref.set(
        {
            "user_id": user_id,
            "chat_id": chat_id,
            "order_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow(),
        }
    )


def get_booking_session(user_id):
    if user_id != BOT_USER_ID:
        raise PermissionError(
            "This bot cannot access booking sessions for non-bot users."
        )

    doc = db.collection("sessions").document(str(user_id)).get()
    if doc.exists:
        data = doc.to_dict()
        if datetime.utcnow() - data["timestamp"] <= timedelta(weeks=2):
            return data
    return None
