import firebase_admin
from firebase_admin import credentials, auth

# Check if the Firebase app is already initialized
if not firebase_admin._apps:
    # Initialize Firebase Admin SDK if not initialized yet
    cred = credentials.Certificate("fnl-4fad6-firebase-adminsdk-lovi2-be32da0a06.json")
    firebase_admin.initialize_app(cred)

def verify_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None
