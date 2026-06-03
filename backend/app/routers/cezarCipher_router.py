from fastapi import APIRouter
from app.services import cezarCipher_service as service
from app.schemas import cezarCipher_schema as schema

router = APIRouter(tags=["Cipher"])

@router.post("/caesar/encrypt", response_model=schema.CaesarResponse)
async def encrypt_caesar(params: schema.CaesarEncryptRequest):
    """
    Szyfruje tekst szyfrem Cezara. 
    Kluczem jest liczba całkowita - przesunięcie.
    """
    # Szyfrowanie = przesunięcie w prawo (dodatnie)
    result = service.caesar_cipher(params.text, params.shift)
    return schema.CaesarResponse(output=result)

@router.post("/caesar/decrypt", response_model=schema.CaesarResponse)
async def decrypt_caesar(params: schema.CaesarDecryptRequest):
    """
    Deszyfruje tekst szyfrem Cezara. 
    Używamy tego samego klucza, co przy szyfrowaniu.
    """
    # Deszyfrowanie = przesunięcie w lewo (ujemne)
    result = service.caesar_cipher(params.text, -params.shift)
    return schema.CaesarResponse(output=result)