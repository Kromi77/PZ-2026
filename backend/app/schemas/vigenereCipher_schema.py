from pydantic import BaseModel, Field

class VigenereEncryptRequest(BaseModel):
    """Schemat dla danych wejściowych szyfrowania Vigenere."""
    text: str = Field(
        ..., 
        title="Tekst Jawny", 
        description="Tekst do zaszyfrowania",
        examples=["Projekt Zespołowy"]
    )
    key: str = Field(
        ..., 
        title="Slowo klucz", 
        description=" Słowo klucz użyte do zaszyfrowania",
        examples=["kot"]
    )

class VigenereDecryptRequest(BaseModel):
    """Schemat dla danych wejściowych deszyfrowania Vigenere."""
    text: str = Field(
        ..., 
        title="Tekst Zaszyfrowany", 
        description="Tekst do odszyfrowania",
        examples=["mc ck hndoc bcuss"]
    )
    key: str = Field(
        ..., 
        title="Slowo klucz", 
        description="Klucz użyty przy szyfrowaniu",
        examples=["kot"]
    )

class VigenereResponse(BaseModel):
    """Wspólny schemat odpowiedzi."""
    output: str = Field(..., title="Wynik operacji")

    class Config:
        json_schema_extra = {
            "example": {"output": "mc ck hndoc bcuss|"}
        }