import hmac
import hashlib

from predict_service.settings import ENCRYPTION_KEY


def hash(data):
    """Hash the data using hmac""" 
    return hmac.new(bytes(ENCRYPTION_KEY, 'utf-8'),
                    bytes(data, 'utf-8'),
                    digestmod=hashlib.sha256).hexdigest()
