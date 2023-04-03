import hmac
import hashlib

from cryptography.fernet import Fernet
from predict_service.settings import ENCRYPTION_KEY, PUBLIC_KEY


def hash(data):
    """Hash the data using hmac""" 
    return hmac.new(bytes(ENCRYPTION_KEY, 'utf-8'),
                    bytes(data, 'utf-8'),
                    digestmod=hashlib.sha256).hexdigest()

def encrypt(data):
    """Encrypt the data using Fernet"""
    fernet = Fernet(PUBLIC_KEY)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data.decode()

def decrypt(data):
    """Decrypt the data using Fernet"""
    fernet = Fernet(PUBLIC_KEY)
    decrypted_data = fernet.decrypt(data.encode())
    return decrypted_data.decode()