def vigenereEncrypt_cipher(plaintext: str, key: str):
    plaintext = plaintext.lower().strip()
    key = key.lower().strip()

    ciphertext = ""
    key_index = 0

    for char in plaintext:
        if 'a' <= char <= 'z':   # tylko zwykłe litery
            shift = ord(key[key_index % len(key)]) - ord('a')

            letter_value = ord(char) - ord('a')
            encrypted_value = (letter_value + shift) % 26

            ciphertext += chr(encrypted_value + ord('a'))
            key_index += 1
        else:
            ciphertext += char

    return ciphertext


def vigenereDecrypt_cipher(ciphertext: str, key: str):
    ciphertext = ciphertext.lower().strip()
    key = key.lower().strip()

    plaintext = ""
    key_index = 0

    for char in ciphertext:
        if 'a' <= char <= 'z':
            shift = ord(key[key_index % len(key)]) - ord('a')

            letter_value = ord(char) - ord('a')
            decrypted_value = (letter_value - shift) % 26

            plaintext += chr(decrypted_value + ord('a'))
            key_index += 1
        else:
            plaintext += char

    return plaintext