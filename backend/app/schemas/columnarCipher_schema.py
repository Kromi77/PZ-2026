from pydantic import BaseModel, Field

class ColumnarEncryptRequest(BaseModel):
    """Schemat dla danych wejściowych szyfrowania szyfrem kolumnowym."""
    text: str = Field(
        ..., 
        title="Tekst Jawny", 
        description="Tekst do zaszyfrowania",
        examples=["Projekt Zespołowy"]
    )
    key: str = Field(
        ..., 
        title="Klucz", 
        description="Słowo będące kluczem (litery określają kolejność kolumn)",
        examples=["SECRET"]
    )

class ColumnarDecryptRequest(BaseModel):
    """Schemat dla danych wejściowych deszyfrowania szyfrem kolumnowym."""
    text: str = Field(
        ..., 
        title="Tekst Zaszyfrowany", 
        description="Tekst do odszyfrowania",
        examples=["tEjPrZokrewmSoódy"]
    )
    key: str = Field(
        ..., 
        title="Klucz", 
        description="Słowo będące kluczem (musi być takie samo co przy szyfrowaniu)",
        examples=["SECRET"]
    )

class ColumnarResponse(BaseModel):
    """Wspólny schemat odpowiedzi."""
    output: str = Field(..., title="Wynik operacji")
