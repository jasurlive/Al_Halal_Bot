import os
import json
import logging
from datetime import datetime, timedelta, timezone
import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)

firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
if not firebase_credentials:
    logger.critical("Missing FIREBASE_CREDENTIALS env variable")
    raise ValueError("Missing FIREBASE_CREDENTIALS env variable")
cred = credentials.Certificate(json.loads(firebase_credentials))

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
    logger.info("Firebase app initialized.")

db = firestore.client()


def save_booking_session(user_id, chat_id):
    try:
        doc_ref = db.collection("sessions").document(str(user_id))
        doc_ref.set(
            {
                "user_id": user_id,
                "chat_id": chat_id,
                "timestamp": datetime.now(timezone.utc),
            }
        )
        logger.info(f"Saved booking session for user_id={user_id}")
    except Exception as e:
        logger.error(f"Failed to save booking session: {e}", exc_info=True)


def get_booking_session(user_id):
    try:
        doc = db.collection("sessions").document(str(user_id)).get()
        if doc.exists:
            data = doc.to_dict()
            if datetime.now(timezone.utc) - data["timestamp"] <= timedelta(weeks=2):
                logger.info(f"Retrieved booking session for user_id={user_id}")
                return data
            else:
                logger.info(f"Session expired for user_id={user_id}")
        else:
            logger.info(f"No session found for user_id={user_id}")
    except Exception as e:
        logger.error(f"Failed to get booking session: {e}", exc_info=True)
    return None


save_user_info = save_booking_session
get_user_chat_info = get_booking_session

__all__ = [
    "save_booking_session",
    "get_booking_session",
    "save_user_info",
    "get_user_chat_info",
]
