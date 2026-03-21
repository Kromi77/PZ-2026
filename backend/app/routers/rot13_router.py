from fastapi import APIRouter
from app.services import rot13_service as service
from app.schemas import rot13_schema as schema

router = APIRouter()

@router.post("/rot13/process", response_model=schema.Rot13Response)
async def encrypt_rot13(params: schema.Rot13Request):
    """
    Przetwarza tekst algorytmem ROT13 (przesunięcie o 13 znaków).
    ROT13 jest szyfrem symetrycznym - ta sama operacja służy
    zarówno do szyfrowania, jak i deszyfrowania.
    """
    result = service.process_rot13(params.text)
    return schema.Rot13Response(output=result)