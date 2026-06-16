"""
Router dla steganografii - definiuje API endpointy do ukrywania i ekstraktowania wiadomości.
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import io
import tempfile
import os

from app.services import steganography_service as service
from app.schemas import steganography_schema as schema

router = APIRouter(prefix="/steganography", tags=["Steganography"])


@router.get("/info", response_model=schema.SteganographyInfoResponse)
async def get_steganography_info():
    """
    Zwraca informacje o module steganografii.
    
    Steganografia = ukrywanie tajnych wiadomości w plikach multimedialnych
    w taki sposób, że nikt nie podejrzewa ich obecności.
    """
    return schema.SteganographyInfoResponse(
        description="Ukrywanie zaszyfrowanej wiadomości w najmniej znaczących bitach pikseli/próbek dźwięku"
    )


@router.post("/hide", response_class=FileResponse)
async def hide_message(
    file: UploadFile = File(...),
    encrypted_message: str = Form(...),
    media_type: str = Form(...),
    deployment_mode: int = Form(0)
):
    """
    Ukrywa zaszyfrowaną wiadomość w pliku multimedialnym (BMP lub WAV).
    
    Proces:
    1. Użytkownik szyfruuje wiadomość (np. szyfrem Cezara)
    2. Zaszyfrowana wiadomość jest ukrywana w BMP/WAV przy użyciu LSB
    3. Zwracany jest plik z ukrytą wiadomością
    
    Parametry:
    - file: Plik BMP lub WAV
    - encrypted_message: Zaszyfrowana wiadomość do ukrycia
    - media_type: Typ pliku ("bmp" lub "wav")
    
    Zwraca: Plik binarny z ukrytą wiadomością
    """
    try:
        # Walidacja typu pliku
        if media_type.lower() not in ["bmp", "wav"]:
            raise HTTPException(
                status_code=400,
                detail=f"Nieobsługiwany typ pliku: {media_type}. Obsługiwane: bmp, wav"
            )
        
        # Odczyt zawartości pliku
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="Plik jest pusty"
            )
        
        is_uniform = int(deployment_mode) == 1

        # Ukryj wiadomość w zależności od typu pliku
        if media_type.lower() == "bmp":
            result_content = service.hide_message_in_bmp(
                file_content,
                encrypted_message,
                uniform=is_uniform,
            )
            output_filename = "steganography_output.bmp"
        else:  # wav
            result_content = service.hide_message_in_wav(
                file_content,
                encrypted_message,
                uniform=is_uniform,
            )
            output_filename = "steganography_output.wav"
        
        # Zapisz wynik do pliku tymczasowego
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{media_type}") as tmp:
            tmp.write(result_content)
            tmp_path = tmp.name
        
        # Zwróć plik jako odpowiedź
        return FileResponse(
            tmp_path,
            media_type=f"application/{media_type}",
            filename=output_filename,
            headers={"Content-Disposition": f"attachment; filename={output_filename}"}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas ukrywania wiadomości: {str(e)}")


@router.post("/extract", response_model=schema.SteganographyExtractResponse)
async def extract_message(
    file: UploadFile = File(...),
    media_type: str = Form(...)
):
    """
    Ekstraktuje ukrytą wiadomość z pliku multimedialnego.
    
    Proces:
    1. Plik BMP/WAV jest przesyłany na serwer
    2. Ukryta wiadomość jest wyekstraktowana z LSB
    3. Zwracana jest zaszyfrowana wiadomość
    
    Parametry:
    - file: Plik BMP lub WAV zawierający ukrytą wiadomość
    - media_type: Typ pliku ("bmp" lub "wav")
    
    Zwraca: Wyekstraktowaną (zaszyfrowaną) wiadomość
    """
    try:
        # Walidacja typu pliku
        if media_type.lower() not in ["bmp", "wav"]:
            raise HTTPException(
                status_code=400,
                detail=f"Nieobsługiwany typ pliku: {media_type}. Obsługiwane: bmp, wav"
            )
        
        # Odczyt zawartości pliku
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="Plik jest pusty"
            )
        
        # Ekstraktuj wiadomość w zależności od typu pliku
        if media_type.lower() == "bmp":
            extracted_message = service.extract_message_from_bmp(file_content)
        else:  # wav
            extracted_message = service.extract_message_from_wav(file_content)
        
        if not extracted_message:
            raise HTTPException(
                status_code=400,
                detail="Nie znaleziono ukrytej wiadomości w pliku"
            )
        
        return schema.SteganographyExtractResponse(
            message=extracted_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Błąd podczas ekstraktowania wiadomości: {str(e)}"
        )
