from pydantic import BaseModel, Field

class AtbashEncryptRequest(BaseModel):
    """Schemat dla danych wejściowych szyfrowania Atbash."""
    text: str = Field(
        ..., 
        title="Tekst Jawny", 
        description="Tekst do zaszyfrowania",
        examples=["Projekt Zespolowy"]
    )

class AtbashDecryptRequest(BaseModel):
    """Schemat dla danych wejściowych deszyfrowania Atbash."""
    text: str = Field(
        ..., 
        title="Tekst Zaszyfrowany", 
        description="Tekst do odszyfrowania",
        examples=["Kilyvpg Hvhkvorbd"]
    )

class AtbashEncryptResponse(BaseModel):
    """Schemat dla danych wyjściowych po szyfrowaniu Atbash."""
    output: str = Field(
        ..., 
        title="Wynik operacji",
        examples=["Kilyvpg Hvhkvorbd"]
    )

class AtbashDecryptResponse(BaseModel):
    """Schemat dla danych wyjściowych po deszyfrowaniu Atbash."""
    output: str = Field(
        ..., 
        title="Wynik operacji",
        examples=["Projekt Zespolowy"]
    )