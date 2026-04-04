from pydantic import BaseModel, Field


class RailFenceEncryptRequest(BaseModel):
    """Schemat dla danych wejściowych szyfrowania szyfrem płotkowym."""
    text: str = Field(
        ...,
        title="Tekst Jawny",
        description="Tekst do zaszyfrowania",
        examples=["WEAREISCOVERED"]
    )
    rails: int = Field(
        ...,
        ge=2,
        title="Liczba szyn",
        description="Liczba poziomów zygzaka (min. 2)",
        examples=[3]
    )


class RailFenceDecryptRequest(BaseModel):
    """Schemat dla danych wejściowych deszyfrowania szyfrem płotkowym."""
    text: str = Field(
        ...,
        title="Tekst Zaszyfrowany",
        description="Tekst do odszyfrowania",
        examples=["WOEERICVRDASE"]
    )
    rails: int = Field(
        ...,
        ge=2,
        title="Liczba szyn",
        description="Liczba szyn użyta przy szyfrowaniu",
        examples=[3]
    )


class RailFenceResponse(BaseModel):
    """Wspólny schemat odpowiedzi."""
    output: str = Field(..., title="Wynik operacji")

    class Config:
        json_schema_extra = {
            "example": {"output": "WOEERICVRDASE"}
        }
