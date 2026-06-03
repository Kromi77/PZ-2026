from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from app.schemas.decoder_schema import DecoderResponse
from app.services import decoder_service

router = APIRouter(prefix="/decoder", tags=["Decoder Module"])

@router.post("/process", response_model=DecoderResponse)
async def decode_file(
    file: UploadFile = File(...),
    media_type: str = Form(..., description="Typ pliku: 'bmp' lub 'wav'")
):
    """
    Kompletny proces dekodowania:
    - Sprawdza czy w pliku jest wiadomość.
    - Identyfikuje parametry (szyfr, bity, tryb).
    - Odszyfrowuje wiadomość.
    """
    try:
        content = await file.read()
        
        # Wywołanie głównej logiki
        result = decoder_service.process_file(content, media_type)
        
        return DecoderResponse(
            status="success",
            message_detected=True,
            cipher_used=result["cipher_used"],
            deployment_mode=result["deployment_mode"],
            bits_extracted=result["bits_extracted"],
            decrypted_text=result["decrypted_text"]
        )
        
    except ValueError as e:
        # Błąd wyrzucany, gdy plik jest "czysty" (brak wiadomości)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd wewnętrzny dekodera: {str(e)}")
