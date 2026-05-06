from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import io
from app.services import headerBMP_service as BMPService
from app.services import headerWAV_service as WAVService
from app.schemas.header_schema import BMPHeader, WAVHeader


router = APIRouter()

"""
!!!WSZYSTKIE ENDPOINTY STWORZONE TYMCZASOWO DO PÓŹNIEJSZEGO USUNIĘCIA!!!
"""


def parse_bmp_header(
    cipher: str = Form("Szyfr Cezara"),
    sliderR: int = Form(0),
    sliderG: int = Form(4),
    sliderB: int = Form(8),
    bites: int = Form(123456789),
    deployment_mode: int = Form(0),
) -> BMPHeader:
    return BMPHeader(
        cipher=cipher,
        slider=[sliderR, sliderG, sliderB],
        bites=bites,
        deployment_mode=deployment_mode,
    )


def parse_wav_header(
    cipher: str = Form("Szyfr Cezara"),
    slider: int = Form(8),
    bites: int = Form(123456789),
    deployment_mode: int = Form(0),
) -> WAVHeader:
    return WAVHeader(
        cipher=cipher,
        slider=slider,
        bites=bites,
        deployment_mode=deployment_mode,
    )


@router.post("/header/inject-bmp/")
async def inject_bmp_route(header: BMPHeader = Depends(parse_bmp_header), file: UploadFile = File(...)):
    # przygotowanie dodatkowych danych z BMPHeader
    additional_header_data = BMPService.bmp_header_to_bites(header)

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


@router.post("/header/extract-bmp-header/")
async def extract_bmp_header_route(file: UploadFile = File(...)):
    try:
        # odczyt BMPHeader z pliku
        bmp_header = BMPService.extract_bmp_header_from_file(file.file)
        
        # zwrot BMPHeader jako JSON
        return bmp_header
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/header/inject-wav/")
async def inject_wav_route(header: WAVHeader = Depends(parse_wav_header), file: UploadFile = File(...)):
    # Przygotowanie danych (8 bajtów)
    additional_header_data = WAVService.wav_header_to_bites(header)

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
    
@router.post("/header/extract-wav-header/")
async def extract_wav_header_route(file: UploadFile = File(...)):
    try:
        # odczyt WAVHeader z pliku
        wav_header = WAVService.extract_wav_header_from_file(file.file)
        
        # zwrot WAVHeader jako JSON
        return wav_header
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

"""
!!!KONIEC TYMCZASOWYCH ENDPOINTÓW!!!
"""