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
    deployment_mode: int = Form(0, description="0 - ciągły, 1 - równomierny"),
    sliderR: int = Form(1, description="Liczba bitów dla kanału R (BMP)"),
    sliderG: int = Form(1, description="Liczba bitów dla kanału G (BMP)"),
    sliderB: int = Form(1, description="Liczba bitów dla kanału B (BMP)"),
    slider: int = Form(1, description="Liczba bitów dla próbek (WAV)"),
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
        
        if deployment_mode not in (0, 1):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Nieobsługiwany tryb rozmieszczenia: {deployment_mode}. "
                    "Dozwolone: 0 (ciągłe), 1 (równomierne)"
                ),
            )

        is_uniform = deployment_mode == 1

        # Ukryj wiadomość w zależności od typu pliku
        if media_type.lower() == "bmp":
            result_content = service.hide_message_in_bmp(
                file_content,
                encrypted_message,
                uniform=is_uniform,
                sliders=[sliderR, sliderG, sliderB],
            )
            output_filename = "steganography_output.bmp"
        else:  # wav
            result_content = service.hide_message_in_wav(
                file_content,
                encrypted_message,
                uniform=is_uniform,
                slider=slider,
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
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas ukrywania wiadomości: {str(e)}")


@router.post("/extract", response_model=schema.SteganographyExtractResponse)
async def extract_message(
    file: UploadFile = File(...),
    media_type: str = Form(...),
    deployment_mode: int = Form(0, description="0 - ciągły, 1 - równomierny"),
    total_bits: int = Form(None, description="Całkowita liczba bitów (wymagane przy trybie równomiernym)"),
    sliderR: int = Form(1, description="Liczba bitów dla kanału R (BMP)"),
    sliderG: int = Form(1, description="Liczba bitów dla kanału G (BMP)"),
    sliderB: int = Form(1, description="Liczba bitów dla kanału B (BMP)"),
    slider: int = Form(1, description="Liczba bitów dla próbek (WAV)"),
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
            
        is_uniform = deployment_mode == 1
        
        # Ekstraktuj wiadomość w zależności od typu pliku
        if media_type.lower() == "bmp":
            extracted_message = service.extract_message_from_bmp(
                file_content, uniform=is_uniform, total_bits=total_bits, sliders=[sliderR, sliderG, sliderB]
            )
        else:  # wav
            extracted_message = service.extract_message_from_wav(
                file_content, uniform=is_uniform, total_bits=total_bits, slider=slider
            )
        
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
