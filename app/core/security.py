from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import base64
import hashlib
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_fernet_key(key: str) -> bytes:
    hash_obj = hashlib.sha256(key.encode())
    return base64.urlsafe_b64encode(hash_obj.digest())


def get_encryption_key() -> bytes:
    return generate_fernet_key(settings.pan_encryption_key)


fernet = Fernet(get_encryption_key())


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None


def encrypt_pan(pan: str) -> str:
    try:
        encrypted = fernet.encrypt(pan.encode())
        return encrypted.decode()
    except Exception as e:
        logger.error(f"Failed to encrypt PAN: {e}")
        raise


def decrypt_pan(encrypted_pan: str) -> str:
    try:
        decrypted = fernet.decrypt(encrypted_pan.encode())
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Failed to decrypt PAN: {e}")
        raise


def mask_pan(pan: str) -> str:
    if len(pan) != 10:
        return "XXXXXXXXXX"
    return f"XXXXXX{pan[6:]}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
