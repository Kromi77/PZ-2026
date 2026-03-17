from fastapi import APIRouter
from pydantic import BaseModel
from app.services import crypto_service as service
from app.schemas import crypto_schema as schema

router = APIRouter()

@router.post("/xor/encrypt", response_model=schema.XOREncryptResponse)
async def encrypt_xor(params: schema.XOREncryptRequest):
    """
    Szyfruje podany tekst przy użyciu algorytmu XOR i klucza.
    Zwraca wynik jako tekst.
    """
    result = service.xor_cipher(params.text, params.key)
    return schema.XOREncryptResponse(output=result)

@router.post("/xor/decrypt", response_model=schema.XORDecryptResponse)
async def decrypt_xor(params: schema.XORDecryptRequest):
    """
    Deszyfruje podany tekst przy użyciu algorytmu XOR i klucza.
    Zwraca wynik jako tekst.
    """
    result = service.xor_cipher(params.text, params.key)
    return schema.XORDecryptResponse(output=result)