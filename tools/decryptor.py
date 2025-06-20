import os
import tempfile

from Crypto.Cipher import AES

def decrypt(encrypted_path, key, orig_file_extension):
    # file_extension = os.path.splitext(encrypted_path)[1]
    file_extension = orig_file_extension
    def unpad(data):
        padding_len = data[-1]
        return data[:-padding_len]

    with open(encrypted_path, 'rb') as f:
        iv = f.read(16)
        ciphertext = f.read()

    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_plaintext = cipher.decrypt(ciphertext)
    plaintext = unpad(padded_plaintext)

    temp_path = None
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp:
        temp.write(plaintext)
        temp.flush()
        temp_path = temp
    return temp_path
