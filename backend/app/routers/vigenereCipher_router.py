from fastapi import APIRouter
from app.services import vigenereCipher_service as service
from app.schemas import vigenereCipher_schema as schema

router = APIRouter()

@router.post("/vinegre/encrypt", response_model=schema.VigenereResponse)
async def encrypt_vigenere(params: schema.VigenereEncryptRequest):
    """
    Szyfruje tekst szyfrem Vigenere. 
    Kluczem jest słowo klucz(słowo jakie podaliśmy).
    """
    # Szyfrowanie = przesunięcie w prawo (dodatnie)
    result = service.vigenereEncrypt_cipher(params.text, params.key)
    return schema.VigenereResponse(output=result)

@router.post("/vinegre/decrypt", response_model=schema.VigenereResponse)
async def decrypt_vigenere(params: schema.VigenereDecryptRequest):
    """
    Deszyfruje tekst szyfrem Vigenere. 
    Używamy tego samego klucza, co przy szyfrowaniu.
    """
    #Deszyfrowanie = przesunięcie w lewo (ujemne)
    result = service.vigenereDecrypt_cipher(params.text, params.key)
    return schema.VigenereResponse(output=result)