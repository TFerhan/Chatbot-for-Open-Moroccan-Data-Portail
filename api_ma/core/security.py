from fastapi import HTTPException, Depends
from fastapi.security import APIKeyHeader
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from utils.logging_config import logger

try:
    load_dotenv("config.env")
    API_KEY = os.getenv("API_KEY")
except Exception as e:
    logger.error(f"Failed to load environment variables: {e}")
    raise Exception(f"Failed to load environment variables: {e}")

api_key_header = APIKeyHeader(name="X-Api-Key")


def encrypt_string(input_string, cipher_suite):
    # Chiffrer la chaîne d'entrée
    encrypted_text = cipher_suite.encrypt(input_string.encode())
    return encrypted_text

def decrypt_string(encrypted_text, cipher_suite):
    # Déchiffrer le texte chiffré
    decrypted_text = cipher_suite.decrypt(encrypted_text).decode()
    return decrypted_text

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return api_key