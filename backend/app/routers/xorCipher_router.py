from fastapi import APIRouter, Depends, HTTPException
from app.services import xorCipher_service as xorService
from app.schemas import xorCipher_schema as xorSchema

router = APIRouter(tags=["Cipher"])

@router.post("/encrypt/xor", response_model=xorSchema.XOREncryptResponse)
async def encrypt_xor(params: xorSchema.XOREncryptRequest):
    """
    Szyfruje podany tekst przy użyciu algorytmu XOR i klucza.
    Zwraca wynik jako tekst.
    """
    result = xorService.xor_cipher(params.text, params.key)
    return xorSchema.XOREncryptResponse(output=result)

@router.post("/encrypt/xor/file", response_model=xorSchema.XOREncryptResponse)
async def encrypt_xor_file(params: xorSchema.XORFileRequest = Depends(xorService.xor_file_request)):
    """
    Szyfruje tekst i klucz pobrane z pliku .txt.
    Plik powinien zawierać dwie linie: pierwsza to tekst, druga to klucz.
    Zwraca wynik jako tekst.
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
    result = xorService.xor_cipher(text, key)
    return xorSchema.XOREncryptResponse(output=result)

@router.post("/decrypt/xor", response_model=xorSchema.XORDecryptResponse)
async def decrypt_xor(params: xorSchema.XORDecryptRequest):
    """
    Deszyfruje podany tekst przy użyciu algorytmu XOR i klucza.
    Zwraca wynik jako tekst.
    """
    result = xorService.xor_cipher(params.text, params.key)
    return xorSchema.XORDecryptResponse(output=result)

@router.post("/decrypt/xor/file", response_model=xorSchema.XORDecryptResponse)
async def decrypt_xor_file(params: xorSchema.XORFileRequest = Depends(xorService.xor_file_request)):
    """
    Deszyfruje tekst i klucz pobrane z pliku .txt.
    Plik powinien zawierać dwie linie: pierwsza to tekst zaszyfrowany, druga to klucz.
    Zwraca wynik jako tekst.
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
    result = xorService.xor_cipher(text, key)
    return xorSchema.XORDecryptResponse(output=result)