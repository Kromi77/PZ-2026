from pydantic import BaseModel, Field

class CaesarEncryptRequest(BaseModel):
    """Schemat dla danych wejściowych szyfrowania Cezara."""
    text: str = Field(
        ..., 
        title="Tekst Jawny", 
        description="Tekst do zaszyfrowania",
        examples=["Projekt Zespołowy"]
    )
    shift: int = Field(
        ..., 
        title="Przesunięcie", 
        description="Klucz liczbowy (ile pozycji przesunąć)",
        examples=[3]
    )

class CaesarDecryptRequest(BaseModel):
    """Schemat dla danych wejściowych deszyfrowania Cezara."""
    text: str = Field(
        ..., 
        title="Tekst Zaszyfrowany", 
        description="Tekst do odszyfrowania",
        examples=["Surmhnw#]hvsrŅrz|"]
    )
    shift: int = Field(
        ..., 
        title="Przesunięcie", 
        description="Klucz użyty przy szyfrowaniu",
        examples=[3]
    )

class CaesarResponse(BaseModel):
    """Wspólny schemat odpowiedzi."""
    output: str = Field(..., title="Wynik operacji")

    class Config:
        json_schema_extra = {
            "example": {"output": "Surmhnw#Chvsółrz|"}
        }