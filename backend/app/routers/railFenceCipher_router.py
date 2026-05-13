from fastapi import APIRouter
from app.services import railFenceCipher_service as service
from app.schemas import railFenceCipher_schema as schema

router = APIRouter(tags=["Cipher"])


@router.post("/railfence/encrypt", response_model=schema.RailFenceResponse)
async def encrypt_rail_fence(params: schema.RailFenceEncryptRequest):
    """
    Szyfruje tekst szyfrem płotkowym (Rail Fence).
    Kluczem jest liczba szyn (rails >= 2).
    """
    result = service.rail_fence_encrypt(params.text, params.rails)
    return schema.RailFenceResponse(output=result)


@router.post("/railfence/decrypt", response_model=schema.RailFenceResponse)
async def decrypt_rail_fence(params: schema.RailFenceDecryptRequest):
    """
    Deszyfruje tekst zaszyfrowany szyfrem płotkowym.
    Wymaga podania tej samej liczby szyn co przy szyfrowaniu.
    """
    result = service.rail_fence_decrypt(params.text, params.rails)
    return schema.RailFenceResponse(output=result)
