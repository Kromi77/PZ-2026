from fastapi import APIRouter, Depends, HTTPException
from app.services import xorCipher_service as xorService
from app.schemas import xorCipher_schema as xorSchema

router = APIRouter(tags=["Cipher"])

@router.post("/encrypt/xor", response_model=xorSchema.XOREncryptResponse)
async def encrypt_xor(params: xorSchema.XOREncryptRequest):
    """
    Szyfruje podany tekst przy użyciu algorytmu XOR i klucza.
    Zwraca wynik jako tekst w formacie Base64.
    """
    result = xorService.encrypt_xor(params.text, params.key)
    return xorSchema.XOREncryptResponse(output=result)

@router.post("/encrypt/xor/file", response_model=xorSchema.XOREncryptResponse)
async def encrypt_xor_file(params: xorSchema.XORFileRequest = Depends(xorService.xor_file_request)):
    """
    Szyfruje tekst i klucz pobrane z pliku .txt.
    Plik powinien zawierać dwie linie: pierwsza to tekst, druga to klucz.
    Zwraca wynik jako tekst w formacie Base64.
    """
    file = params.file
    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="Plik musi być typu .txt")
    content = await file.read()
    try:
        lines = content.decode("latin1").splitlines()
        text = lines[0]
        key = lines[1]
    except Exception:
        raise HTTPException(status_code=400, detail="Plik musi zawierać dwie linie: tekst i klucz.")
    text = xorService._unescape_unicode_escapes(text)
    key = xorService._unescape_unicode_escapes(key)
    result = xorService.encrypt_xor(text, key)
    return xorSchema.XOREncryptResponse(output=result)

@router.post("/decrypt/xor", response_model=xorSchema.XORDecryptResponse)
async def decrypt_xor(params: xorSchema.XORDecryptRequest):
    """
    Deszyfruje podany tekst z formatu Base64 przy użyciu algorytmu XOR i klucza.
    Zwraca wynik jako tekst jawny.
    """
    result = xorService.decrypt_xor(params.text, params.key)
    return xorSchema.XORDecryptResponse(output=result)

@router.post("/decrypt/xor/file", response_model=xorSchema.XORDecryptResponse)
async def decrypt_xor_file(params: xorSchema.XORFileRequest = Depends(xorService.xor_file_request)):
    """
    Deszyfruje tekst i klucz pobrane z pliku .txt.
    Plik powinien zawierać dwie linie: pierwsza to tekst zaszyfrowany (Base64), druga to klucz.
    Zwraca wynik jako tekst jawny.
    """
    file = params.file
    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="Plik musi być typu .txt")
    content = await file.read()
    try:
        lines = content.decode("latin1").splitlines()
        text = lines[0]
        key = lines[1]
    except Exception:
        raise HTTPException(status_code=400, detail="Plik musi zawierać dwie linie: tekst i klucz.")
    text = xorService._unescape_unicode_escapes(text)
    key = xorService._unescape_unicode_escapes(key)
    result = xorService.decrypt_xor(text, key)
    return xorSchema.XORDecryptResponse(output=result)