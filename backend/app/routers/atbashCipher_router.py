from fastapi import APIRouter
from app.services import atbashCipher_service as service
from app.schemas import atbashCipher_schema as schema

router = APIRouter(tags=["Cipher"])

@router.post("/atbash/encrypt", response_model=schema.AtbashEncryptResponse)
async def encrypt_atbash(params: schema.AtbashEncryptRequest):
    """
    Szyfruje tekst szyfrem Atbash (A<->Z).
    """
    result = service.atbash_cipher(params.text)
    return schema.AtbashEncryptResponse(output=result)

@router.post("/atbash/decrypt", response_model=schema.AtbashDecryptResponse)
async def decrypt_atbash(params: schema.AtbashDecryptRequest):
    """
    Deszyfruje tekst szyfrem Atbash. 
    """
    result = service.atbash_cipher(params.text)
    return schema.AtbashDecryptResponse(output=result)