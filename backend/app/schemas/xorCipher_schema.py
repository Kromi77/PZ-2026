from fastapi import UploadFile
from pydantic import BaseModel, Field

class XOREncryptRequest(BaseModel):
    """Schema dla danych wejściowych szyfrowania XOR."""
    text: str = Field(
        ...,
        title="Tekst Jawny",
        description="Tekst, który chcesz zaszyfrować",
        examples=["Teskt nie zaszyfrowany"]
    )
    key: str = Field(
        ...,
        min_length=1,
        title="Klucz szyfrujący",
        description="Klucz użyty do operacji XOR. Nie może być pusty.",
        examples=["klucz"]
    )

class XORFileRequest(BaseModel):
    """Schema dla danych wejściowych przesyłanych jako plik (.txt)."""

    file: UploadFile = Field(
        ..., 
        title="Plik wejściowy",
        description="Plik .txt zawierający dwie linie: pierwsza to tekst, druga to klucz."
    )

class XORDecryptRequest(BaseModel):
    """Schema dla danych wejściowych deszyfrowania XOR."""
    text: str = Field(
        ...,
        title="Tekst Zaszyfrowany",
        description="Tekst, który chcesz odszyfrować",
        examples=["Tajne zaszyfrowany"]
    )
    key: str = Field(
        ...,
        min_length=1,
        title="Klucz szyfrujący",
        description="Klucz użyty do operacji XOR. Nie może być pusty.",
        examples=["klucz"]
    )

class XOREncryptResponse(BaseModel):
    """Schema dla danych wyjściowych XOR."""
    output: str = Field(
        ...,
        title="Wynik operacji",
        description="Przetworzony tekst po operacji XOR"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "output": "Qwsd#$1"
            }
        }

class XORDecryptResponse(BaseModel):
    """Schema dla danych wyjściowych XOR."""
    output: str = Field(
        ...,
        title="Wynik operacji",
        description="Przetworzony tekst po operacji XOR"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "output": "Wiadomość"
            }
        }