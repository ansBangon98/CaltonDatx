from Crypto.Cipher import AES
import tempfile

def decrypt_model(encrypted_path, key):
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
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tflite") as temp:
    # with tempfile.NamedTemporaryFile(delete=False, suffix=".onnx") as temp:
        temp.write(plaintext)
        temp.flush()
        temp_path = temp
        # model = load_model(temp.name)

    # Optionally delete the temp file
    # os.remove(temp.name)
    # return model
    return temp_path

# # Example usage
# key = b'ThisIsA32ByteKeyForAES256Encrypt!'
# model = decrypt_model('model_encrypted.bin', key)
# model.summary()
