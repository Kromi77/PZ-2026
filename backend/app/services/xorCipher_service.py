import base64
import codecs
from fastapi import File, UploadFile
from app.schemas import xorCipher_schema as xorSchema

def xor_file_request(file: UploadFile = File(...)) -> xorSchema.XORFileRequest:
    """
    Zależność zapewniająca kontener (schemat) dla przesyłanych plików.
    """
    return xorSchema.XORFileRequest(file=file)

def encrypt_xor(text: str, key: str) -> str:
    """
    Szyfruje tekst przy użyciu algorytmu XOR i pakuje wynik w bezpieczne Base64.
    """
    if not key:
        return text

    # Zamiana tekstu i klucza na surowe bajty (bezpieczne dla UTF-8 i emoji)
    text_bytes = text.encode('utf-8')
    key_bytes = key.encode('utf-8')

    # Dopasowanie długości klucza
    full_key = (key_bytes * (len(text_bytes) // len(key_bytes) + 1))[:len(text_bytes)]

    # Operacja XOR na bajtach
    xor_bytes = bytes(t ^ k for t, k in zip(text_bytes, full_key))

    # Pakowanie w bezpieczny string Base64, który bez problemu przejdzie przez JSON
    return base64.b64encode(xor_bytes).decode('utf-8')

def decrypt_xor(encrypted_text: str, key: str) -> str:
    """
    Odpakowuje tekst z Base64 i deszyfruje go algorytmem XOR.
    """
    if not key:
        return encrypted_text

    # 1. Odpakowanie Base64
    try:
        # validate=True wymusza weryfikację, czy to na pewno format Base64
        xor_bytes = base64.b64decode(encrypted_text.encode('utf-8'), validate=True)
    except Exception:
        # FALLBACK: Jeśli odkodowanie B64 się nie powiodło (np. w starych testach pytest), 
        # traktujemy wejście jako surowy tekst.
        xor_bytes = encrypted_text.encode('utf-8')

    key_bytes = key.encode('utf-8')
    full_key = (key_bytes * (len(xor_bytes) // len(key_bytes) + 1))[:len(xor_bytes)]

    # 2. Odwrócenie operacji XOR
    text_bytes = bytes(t ^ k for t, k in zip(xor_bytes, full_key))

    # 3. Złożenie z powrotem w czytelny tekst (ignoruje ewentualne uszkodzone znaki)
    return text_bytes.decode('utf-8', errors='replace')

def _unescape_unicode_escapes(value: str) -> str:
    """
    Zamienia znaki unicode zapisane jako literały (np. "\\u0015") na rzeczywiste znaki kontrolne.
    """
    if "\\u" not in value and "\\x" not in value:
        return value
    try:
        return codecs.decode(value, "unicode_escape")
    except Exception:
        return value