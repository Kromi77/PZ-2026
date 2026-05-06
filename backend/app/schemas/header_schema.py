from enum import Enum, IntEnum
from typing import Annotated, List

from pydantic import BaseModel, Field, conint


class Cipher(str, Enum):
    """Dostępne algorytmy szyfrowania BMP."""
    CEZAR = "Szyfr Cezara"
    VIGENERE = "Szyfr Vigenere'a"
    XOR = "Szyfr XOR"
    ATBASH = "Szyfr Atbash"
    ROT13 = "ROT13"
    RAIL_FENCE = "Szyfr płotkowy"
    COLUMNAR = "Szyfr kolumnowy"


class DeploymentMode(IntEnum):
    """Tryby rozmieszczenia danych w nagłówku BMP."""
    CONTINUOUS = 0
    UNIFORM = 1


class BMPHeader(BaseModel):
    """Schemat dla nagłówka BMP."""
    cipher: Cipher = Field(
        ..., 
        title="Cipher",
        description="Wybrany algorytm szyfrowania.",
        examples=[Cipher.CEZAR]
    )
    slider: List[Annotated[int, Field(ge=0, le=8)]] = Field(
        ..., 
        min_length=3,
        max_length=3,
        title="Slider",
        description="Tablica trzech wartości suwaków RGB w zakresie 0–8.",
        examples=[[0, 4, 8]]
    )
    """Bites to liczba bitów, które będą używane do ukrywania danych w nagłówku BMP.
    Zakres 0–35 bitów wynika z faktu, że nagłówek BMP ma pole na długość danych w bajtach długości 4 bajty. My      przedstawiamy długość danych w bitach, więc maksymalna wartość 0xFFFFFF * 8 = 34359738360.""" 
    bites: Annotated[int, Field(ge=0, le=34359738360)] = Field(
        ..., 
        title="Bites",
        description="Długość zaszyfrowanych danych w bitach (maksymalnie 35 bitów).",
        examples=[123456789]
    )
    deployment_mode: DeploymentMode = Field(
        ..., 
        title="DeploymentMode",
        description="Tryb rozmieszczenia danych: Ciągłe lub Równomierne.",
        examples=[DeploymentMode.CONTINUOUS]
    )


class WAVHeader(BaseModel):
    """Schemat dla nagłówka WAV."""
    cipher: Cipher = Field(
        ..., 
        title="Cipher",
        description="Wybrany algorytm szyfrowania.",
        examples=[Cipher.CEZAR]
    )
    slider: Annotated[int, Field(ge=0, le=8)] = Field(
        ..., 
        title="Slider",
        description="Wartość suwaka w zakresie 0–8.",
        examples=[8]
    )
    """Bites to liczba bitów, które będą używane do ukrywania danych w nagłówku WAV.
    Zakres 0–35 bitów wynika z faktu, że nagłówek WAV ma pole na długość danych w bajtach długości 4 bajty. My      przedstawiamy długość danych w bitach, więc maksymalna wartość 0xFFFFFF * 8 = 34359738360.""" 
    bites: Annotated[int, Field(ge=0, le=34359738360)] = Field(
        ..., 
        title="Bites",
        description="Długość zaszyfrowanych danych w bitach (maksymalnie 35 bitów).",
        examples=[123456789]
    )
    deployment_mode: DeploymentMode = Field(
        ..., 
        title="DeploymentMode",
        description="Tryb rozmieszczenia danych: Ciągłe lub Równomierne.",
        examples=[DeploymentMode.CONTINUOUS]
    )

