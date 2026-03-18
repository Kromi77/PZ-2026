from fastapi import APIRouter
from pydantic import BaseModel
from app.services import xorCipher_service as xorService
from app.schemas import xorCipher_schema as xorSchema

router = APIRouter()

@router.post("/encrypt/xor", response_model=xorSchema.XOREncryptResponse)
async def encrypt_xor(params: xorSchema.XOREncryptRequest):
    """
    Szyfruje podany tekst przy użyciu algorytmu XOR i klucza.
    Zwraca wynik jako tekst.
    """
    result = xorService.xor_cipher(params.text, params.key)
    return xorSchema.XOREncryptResponse(output=result)

@router.post("/decrypt/xor", response_model=xorSchema.XORDecryptResponse)
async def decrypt_xor(params: xorSchema.XORDecryptRequest):
    """
    Deszyfruje podany tekst przy użyciu algorytmu XOR i klucza.
    Zwraca wynik jako tekst.
    """
    result = xorService.xor_cipher(params.text, params.key)
    return xorSchema.XORDecryptResponse(output=result)