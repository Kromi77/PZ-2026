from pydantic import BaseModel, Field

class DecoderResponse(BaseModel):
    status: str = Field("success", description="Status operacji")
    message_detected: bool = Field(..., description="Czy plik zawierał ukrytą wiadomość (Analiza)")
    cipher_used: str = Field(..., description="Zidentyfikowany algorytm szyfrowania")
    deployment_mode: str = Field(..., description="Zidentyfikowany tryb rozmieszczenia (Ciągłe/Równomierne)")
    bits_extracted: int = Field(..., description="Liczba bitów odczytana z nagłówka")
    decrypted_text: str = Field(..., description="Ostateczna, odszyfrowana wiadomość")