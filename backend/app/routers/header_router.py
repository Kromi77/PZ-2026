from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import io
from app.services import headerBMP_service as BMPService
from app.services import headerWAV_service as WAVService

router = APIRouter()

"""
!!!WSZYSTKIE ENDPOINTY STWORZONE TYMCZASOWO DO PÓŹNIEJSZEGO USUNIĘCIA!!!
"""

@router.post("/header/inject-bmp/")
async def inject_bmp_route(file: UploadFile = File(...)):
    # przygotowanie przykładowej tablicy bajtów (dodatkowe dane)
    additional_header_data = bytes([0xDE, 0xAD, 0xBE, 0xEF, 0x12, 0x34, 0x56, 0x78])

    try:
        # wywołanie funkcji modyfikującej w pamięci
        modified_bmp = BMPService.inject_data_to_bmp_header(file.file, additional_header_data)

        # zwrot pliku do klienta z pamięci podręcznej
        return StreamingResponse(
            modified_bmp,
            media_type="image/bmp",
            headers={"Content-Disposition": f"attachment; filename=modified_{file.filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/header/extract-bmp/")
async def extract_bmp_route(file: UploadFile = File(...)):
    # długość wcześniej dodanych danych
    data_length_to_remove = 8

    try:
        # wywołanie funkcji przywracającej oryginalny plik
        restored_bmp = BMPService.remove_data_from_bmp_header(file.file, data_length_to_remove)

        # zwrot przywróconego pliku
        return StreamingResponse(
            restored_bmp,
            media_type="image/bmp",
            headers={"Content-Disposition": f"attachment; filename=restored_{file.filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
# Importujesz tylko serwis - router nie musi wiedzieć o 'io'
from app.services import headerWAV_service as WAVService

router = APIRouter()

@router.post("/header/inject-wav/")
async def inject_wav_route(file: UploadFile = File(...)):
    # Przygotowanie danych (8 bajtów)
    additional_header_data = bytes([0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00, 0x11])

    try:
        # Przekazujemy file.file bezpośrednio, tak jak w Twoim BMP
        # Funkcja w serwisie poradzi sobie z odczytem
        modified_wav = WAVService.inject_data_to_wav_header(file.file, additional_header_data)

        return StreamingResponse(
            modified_wav,
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename=modified_{file.filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/header/extract-wav/")
async def extract_wav_route(file: UploadFile = File(...)):
    try:
        # Tutaj również przekazujemy bezpośrednio file.file
        restored_wav = WAVService.remove_data_from_wav_header(file.file)

        return StreamingResponse(
            restored_wav,
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename=restored_{file.filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

"""
!!!KONIEC TYMCZASOWYCH ENDPOINTÓW!!!
"""