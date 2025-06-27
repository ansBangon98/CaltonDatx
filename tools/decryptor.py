from Crypto.Cipher import AES

def decrypt(encrypted_path, key, output_path):
    def unpad(data):
        padding_len = data[-1]
        return data[:-padding_len]

    with open(encrypted_path, 'rb') as f:
        iv = f.read(16)
        ciphertext = f.read()

    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_plaintext = cipher.decrypt(ciphertext)
    plaintext = unpad(padded_plaintext)

    with open(output_path, "wb") as out:
        out.write(plaintext)
    
    return output_path

