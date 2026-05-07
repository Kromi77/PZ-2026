"""
Schematy (modele) dla steganografii - definiują strukturę żądań i odpowiedzi API.
"""

from pydantic import BaseModel, Field
from typing import Literal


class SteganographyHideRequest(BaseModel):
    """Schemat dla żądania ukrycia wiadomości w pliku multimedialnym."""
    
    media_type: Literal["bmp", "wav"] = Field(
        ...,
        title="Typ Pliku",
        description="Typ nośnika, w którym ukryć wiadomość",
        examples=["bmp"]
    )
    encrypted_message: str = Field(
        ...,
        title="Zaszyfrowana Wiadomość",
        description="Wiadomość (wcześniej zaszyfrowana jednym z szyfrów) do ukrycia",
        examples=["qwerty123"]
    )
    # Note: Plik binarny będzie przesyłany jako upload w multipart form-data


class SteganographyExtractRequest(BaseModel):
    """Schemat dla żądania ekstraktowania wiadomości z pliku."""
    
    media_type: Literal["bmp", "wav"] = Field(
        ...,
        title="Typ Pliku",
        description="Typ nośnika, z którego ekstraktować wiadomość",
        examples=["bmp"]
    )
    # Note: Plik binarny będzie przesyłany jako upload


class SteganographyHideResponse(BaseModel):
    """Schemat dla odpowiedzi przy ukrywaniu wiadomości."""
    
    status: str = Field(
        "success",
        title="Status",
        description="Status operacji"
    )
    message: str = Field(
        ...,
        title="Komunikat",
        description="Opis wyniku operacji",
        examples=["Wiadomość została ukryta w pliku BMP"]
    )
    file_size: int = Field(
        ...,
        title="Rozmiar Pliku",
        description="Rozmiar wygenerowanego pliku z ukrytą wiadomością (w bajtach)"
    )


class SteganographyExtractResponse(BaseModel):
    """Schemat dla odpowiedzi przy ekstraktowaniu wiadomości."""
    
    status: str = Field(
        "success",
        title="Status",
        description="Status operacji"
    )
    message: str = Field(
        ...,
        title="Wyekstraktowana Wiadomość",
        description="Zaszyfrowana wiadomość wyekstraktowana z pliku",
        examples=["qwerty123"]
    )


class SteganographyInfoResponse(BaseModel):
    """Schemat dla informacji o steganografii."""
    
    status: str = Field("success", title="Status")
    technique: str = Field(
        "LSB (Least Significant Bit)",
        title="Technika",
        description="Używana technika steganografii"
    )
    supported_formats: list = Field(
        ["BMP", "WAV"],
        title="Obsługiwane Formaty",
        description="Formaty plików wspierane przez moduł"
    )
    description: str = Field(
        title="Opis",
        default="Ukrywanie zaszyfrowanej wiadomości w najmniej znaczących bitach pikseli/próbek dźwięku"
    )
    max_message_size: str = Field(
        "Równa rozmiarowi pikseli (BMP) lub próbek dźwięku (WAV)",
        title="Maksymalny Rozmiar Wiadomości"
    )
