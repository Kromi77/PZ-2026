import io
from typing import Any
from app.schemas.header_schema import Cipher, DeploymentMode
from app.services import headerBMP_service, headerWAV_service
from app.services import steganography_service
from app.services import cezarCipher_service
from app.services import atbashCipher_service
from app.services import columnarCipher_service
from app.services import railFenceCipher_service
from app.services import rot13_service
from app.services import vigenereCipher_service
from app.services import xorCipher_service

def _derive_key_from_sliders(cipher_type: Cipher, sliders: list[int]) -> Any:
    """
    Wyprowadza klucz kryptograficzny na podstawie suwaków steganograficznych z nagłówka,
    zwracając odpowiedni typ danych (int lub str) wymagany przez konkretny szyfr.
    """
    k1 = sliders[0] if len(sliders) > 0 else 3
    k2 = sliders[1] if len(sliders) > 1 else 0
    k3 = sliders[2] if len(sliders) > 2 else 0
    
    if cipher_type == Cipher.CEZAR:
        return k1 if k1 != 0 else 3
        
    elif cipher_type == Cipher.XOR:
        # Szyfr XOR oczekuje klucza jako string.
        combined = k1 ^ k2 ^ k3
        return str(combined) if combined != 0 else "7"
        
    elif cipher_type == Cipher.RAIL_FENCE:
        # Szyfr płotkowy oczekuje inta określającego ilość szyn (min. 2).
        return max(2, k1)
        
    elif cipher_type in (Cipher.VIGENERE, Cipher.COLUMNAR):
        # Oba te szyfry oczekują klucza w postaci słowa kluczowego (string).
        words = ["SECRET", "KOD", "STEGO", "FASTAPI", "MATRIX", "CIPHER"]
        return words[k1 % len(words)]
        
    # Atbash i ROT13 nie wymagają dynamicznego klucza (ROT13 ma stały shift 13)
    return None

def _prepare_user_key(cipher_type: Cipher, key: str) -> Any:
    key = key.strip() if key else ""

    if cipher_type in (Cipher.ATBASH, Cipher.ROT13):
        return None

    if not key:
        raise ValueError(f"{cipher_type.value} wymaga podania klucza deszyfrowania.")

    if cipher_type == Cipher.CEZAR:
        try:
            return int(key)
        except ValueError:
            raise ValueError("Klucz dla Szyfru Cezara musi być liczbą całkowitą.")

    if cipher_type == Cipher.RAIL_FENCE:
        try:
            rails = int(key)
        except ValueError:
            raise ValueError("Klucz dla Szyfru płotkowego musi być liczbą całkowitą.")

        if rails < 2:
            raise ValueError("Klucz dla Szyfru płotkowego musi być większy lub równy 2.")

        return rails

    return key

def _decrypt_text(encrypted_text: str, cipher_type: Cipher, key: Any) -> str:
    """Kieruje tekst do odpowiedniego algorytmu deszyfrującego używając poprawnego nazewnictwa."""
    if cipher_type == Cipher.CEZAR:
        return cezarCipher_service.caesar_cipher(encrypted_text, -key)
        
    elif cipher_type == Cipher.ATBASH:
        return atbashCipher_service.atbash_cipher(encrypted_text)
        
    elif cipher_type == Cipher.ROT13:
        return rot13_service.process_rot13(encrypted_text)
        
    elif cipher_type == Cipher.XOR:
        return xorCipher_service.xor_cipher(encrypted_text, key)
        
    elif cipher_type == Cipher.RAIL_FENCE:
        return railFenceCipher_service.rail_fence_decrypt(encrypted_text, key)
        
    elif cipher_type == Cipher.VIGENERE:
        return vigenereCipher_service.vigenereDecrypt_cipher(encrypted_text, key)
        
    elif cipher_type == Cipher.COLUMNAR:
        return columnarCipher_service.columnar_decrypt(encrypted_text, key)
        
    return f"[Błąd - nieznany szyfr {cipher_type.value}] {encrypted_text}"

def process_file(file_content: bytes, media_type: str, key: str = "") -> dict:
    """
    Główna funkcja Modułu Dekodera realizująca:
    1. Analizę pliku
    2. Identyfikację parametrów
    3. Ekstrakcję i deszyfrowanie
    """
    file_stream = io.BytesIO(file_content)
    
    # ---------------------------------------------------------
    # Pkt 1 & 2: Analiza pliku i Identyfikacja parametrów
    # ---------------------------------------------------------
    try:
        if media_type.lower() == "bmp":
            header = headerBMP_service.extract_bmp_header_from_file(file_stream)
            sliders = header.sliders
        elif media_type.lower() == "wav":
            header = headerWAV_service.extract_wav_header_from_file(file_stream)
            sliders = [header.slider]
        else:
            raise ValueError("Nieobsługiwany format. Dozwolone: bmp, wav.")
    except ValueError as e:
        raise ValueError(f"Analiza pliku wykazała brak ukrytej wiadomości lub uszkodzenie: {str(e)}")

    cipher_type = header.cipher
    deployment_mode = header.deployment_mode
    total_bits = header.bits

    # ---------------------------------------------------------
    # Pkt 3: Ekstrakcja wiadomości (Steganografia)
    # ---------------------------------------------------------
    is_uniform = (deployment_mode == DeploymentMode.UNIFORM)
    
    if media_type.lower() == "bmp":
        encrypted_message = steganography_service.extract_message_from_bmp(
            bmp_file_content=file_content,
            uniform=is_uniform,
            total_bits=total_bits,
            sliders=sliders
        )
    else:
        encrypted_message = steganography_service.extract_message_from_wav(
            wav_file_content=file_content,
            uniform=is_uniform,
            total_bits=total_bits,
            slider=sliders[0]
        )

    if not encrypted_message:
        raise ValueError("Nie udało się odczytać ciągu bitów z danych steganograficznych.")

    # ---------------------------------------------------------
    # Pkt 3 cd.: Deszyfrowanie (Kryptografia)
    # ---------------------------------------------------------
    crypto_key = _prepare_user_key(cipher_type, key)
    decrypted_text = _decrypt_text(encrypted_message, cipher_type, crypto_key)

    return {
        "cipher_used": cipher_type.value,
        "deployment_mode": "Równomierne" if is_uniform else "Ciągłe",
        "bits_extracted": total_bits,
        "decrypted_text": decrypted_text
    }