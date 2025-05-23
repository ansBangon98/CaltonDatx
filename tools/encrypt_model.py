from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

import key_generator as keygen
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import core.state as state



def pad(data):
    padding = AES.block_size - len(data) % AES.block_size
    return data + bytes([padding]) * padding

def encrypt_model(model_path, output_path, key):
    with open(model_path, 'rb') as f:
        plaintext = f.read()

    plaintext_padded = pad(plaintext)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(plaintext_padded)

    with open(output_path, 'wb') as f:
        f.write(iv + ciphertext)
    print('model has been encrypted')

key = keygen.generate_32byte_key(state.encryption_key)
encrypt_model('./models/face_people.tflite', './models/face_people.bin', key)