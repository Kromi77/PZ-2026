from pydantic import BaseModel, Field

class Rot13Request(BaseModel):
    """Schemat dla danych wejściowych ROT13 (szyfrowanie i deszyfrowanie)."""
    text: str = Field(
        ..., 
        title="Tekst Wejściowy", 
        description="Tekst do przetworzenia (zaszyfrowania lub odszyfrowania)",
        examples=["Projekt Zespolowy"]
    )

class Rot13Response(BaseModel):
    """Wspólny schemat odpowiedzi dla ROT13."""
    output: str = Field(..., title="Wynik operacji")

    class Config:
        json_schema_extra = {
            "example": {"output": "Cebwrxg Mrfcbobjl"}
        }