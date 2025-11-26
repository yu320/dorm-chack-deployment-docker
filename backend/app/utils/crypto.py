# backend/app/utils/crypto.py
import os
from cryptography.fernet import Fernet
from typing import Optional

class Crypto:
    def __init__(self, key: Optional[str] = None):
        if key:
            self.key = key.encode('utf-8')
        else:
            self.key = os.getenv("FERNET_KEY")
            if not self.key:
                raise ValueError("FERNET_KEY environment variable not set and no key provided.")
            self.key = self.key.encode('utf-8')
        self.fernet = Fernet(self.key)

    def encrypt(self, data: str) -> bytes:
        return self.fernet.encrypt(data.encode('utf-8'))

    def decrypt(self, token: bytes) -> str:
        return self.fernet.decrypt(token).decode('utf-8')