import hashlib

def generate_32byte_key(passphrase: str) -> bytes:
    return hashlib.sha256(passphrase.encode()).digest()
