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