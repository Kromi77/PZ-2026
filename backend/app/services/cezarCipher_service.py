def caesar_cipher(text: str, shift: int) -> str:
    """
    Szyfruje lub deszyfruje tekst przesuwając kod każdego znaku o wartość shift.
    Działa na pełnym zakresie Unicode, co zapewnia obsługę polskich znaków.
    Dla deszyfrowania należy podać shift z wartością ujemną.
    """
    result = []
    for char in text:
        # Przesunięcie o n pozycji w tablicy znaków
        new_char = chr(ord(char) + shift)
        result.append(new_char)
    
    return "".join(result)