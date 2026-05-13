from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import io
from typing import Literal
from app.services import headerBMP_service as BMPService
from app.services import headerWAV_service as WAVService
from app.schemas.header_schema import BMPHeader, WAVHeader, Cipher, DeploymentMode

router = APIRouter(tags=["Header"])

def parse_bmp_header(
    cipher: Cipher = Form(...),
    sliderR: int = Form(..., ge=0, le=8),
    sliderG: int = Form(..., ge=0, le=8),
    sliderB: int = Form(..., ge=0, le=8),
    bits: int = Form(..., ge=0, le=34359738367),
    deployment_mode_str: Literal["Ciagłe", "Równomierne"] = Form(..., alias="deployment_mode"),
) -> BMPHeader:
    mode_val = DeploymentMode(0) if deployment_mode_str == "Ciagłe" else DeploymentMode(1)
    return BMPHeader(
        cipher=cipher,
        sliders=[sliderR, sliderG, sliderB],
        bits=bits,
        deployment_mode=mode_val,
    )


def parse_wav_header(
    cipher: Cipher = Form(...),
    slider: int = Form(..., ge=0, le=8),
    bits: int = Form(..., ge=0, le=34359738367),
    deployment_mode_str: Literal["Ciagłe", "Równomierne"] = Form(..., alias="deployment_mode"),
) -> WAVHeader:
    mode_val = DeploymentMode(0) if deployment_mode_str == "Ciagłe" else DeploymentMode(1)
    return WAVHeader(
        cipher=cipher,
        slider=slider,
        bits=bits,
        deployment_mode=mode_val,
    )


@router.post(
    "/header/inject-bmp/",
    response_class=StreamingResponse,
    summary="Inject BMP Header",
    description="Wstrzykuje dodatkowe dane do nagłówka pliku BMP i zwraca zmodyfikowany plik obrazu."
)
async def inject_bmp_route(header: BMPHeader = Depends(parse_bmp_header), file: UploadFile = File(...)):
    # przygotowanie dodatkowych danych z BMPHeader
    additional_header_data = BMPService.bmp_header_to_bits(header)

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


@router.post(
    "/header/extract-bmp/",
    response_class=StreamingResponse,
    summary="Extract and Restore BMP",
    description="Usuwa wcześniej dodane dane z nagłówka pliku BMP i przywraca jego oryginalną postać."
)
async def extract_bmp_route(file: UploadFile = File(...)):
    # długość wcześniej dodanych danych
    data_length_to_remove = 8

    try:
        # wywołanie funkcji przywracającej oryginalny plik
        restored_bmp = BMPService.remove_data_from_bmp_header(file.file)

        # zwrot przywróconego pliku
        return StreamingResponse(
            restored_bmp,
            media_type="image/bmp",
            headers={"Content-Disposition": f"attachment; filename=restored_{file.filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/header/extract-bmp-header/",
    response_model=BMPHeader,
    summary="Extract BMP Header Info",
    description="Odczytuje parametry ukryte w nagłówku pliku BMP (szyfr, wartości suwaków, bity, tryb) i zwraca je w formacie JSON."
)
async def extract_bmp_header_route(file: UploadFile = File(...)):
    try:
        # odczyt BMPHeader z pliku
        bmp_header = BMPService.extract_bmp_header_from_file(file.file)
        
        # zwrot BMPHeader jako JSON
        return bmp_header
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/header/inject-wav/",
    response_class=StreamingResponse,
    summary="Inject WAV Header",
    description="Wstrzykuje dodatkowe dane do nagłówka pliku audio WAV i zwraca zmodyfikowany plik."
)
async def inject_wav_route(header: WAVHeader = Depends(parse_wav_header), file: UploadFile = File(...)):
    # Przygotowanie danych (8 bajtów)
    additional_header_data = WAVService.wav_header_to_bits(header)

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


@router.post(
    "/header/extract-wav/",
    response_class=StreamingResponse,
    summary="Extract and Restore WAV",
    description="Usuwa wcześniej dodane dane z nagłówka pliku audio WAV i przywraca jego oryginalną postać."
)
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


@router.post(
    "/header/extract-wav-header/",
    response_model=WAVHeader,
    summary="Extract WAV Header Info",
    description="Odczytuje parametry ukryte w nagłówku pliku WAV (szyfr, wartość suwaka, bity, tryb) i zwraca je w formacie JSON."
)
async def extract_wav_header_route(file: UploadFile = File(...)):
    try:
        # odczyt WAVHeader z pliku
        wav_header = WAVService.extract_wav_header_from_file(file.file)
        
        # zwrot WAVHeader jako JSON
        return wav_header
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))