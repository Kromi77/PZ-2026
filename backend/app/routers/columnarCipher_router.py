from fastapi import APIRouter
from app.services import columnarCipher_service as service
from app.schemas import columnarCipher_schema as schema

router = APIRouter()

@router.post("/columnar/encrypt", response_model=schema.ColumnarResponse)
async def encrypt_columnar(params: schema.ColumnarEncryptRequest):
    """
    Szyfruje tekst szyfrem kolumnowym (columnar transposition cipher).
    
    Klucz to słowo, którego litery określają kolejność czytania kolumn.
    Litery są numerowane alfabetycznie, a tekst jest czytany w tej kolejności.
    """
    result = service.columnar_encrypt(params.text, params.key)
    return schema.ColumnarResponse(output=result)

@router.post("/columnar/decrypt", response_model=schema.ColumnarResponse)
async def decrypt_columnar(params: schema.ColumnarDecryptRequest):
    """
    Deszyfruje tekst zaszyfrowany szyfrem kolumnowym.
    
    Klucz musi być identyczny jak przy szyfrowaniu.
    """
    result = service.columnar_decrypt(params.text, params.key)
    return schema.ColumnarResponse(output=result)
