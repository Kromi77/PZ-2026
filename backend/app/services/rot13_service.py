def process_rot13(text: str) -> str:
    """
    Szyfruje i deszyfruje tekst algorytmem ROT13.
    Podmienia tylko standardowe litery alfabetu łacińskiego (A-Z, a-z),
    pozostawiając polskie znaki, cyfry i znaki specjalne bez zmian.
    Ponieważ alfabet ma 26 znaków, ta sama funkcja działa w obie strony.
    """
    result = []
    for char in text:
        # Sprawdzamy małe litery
        if 'a' <= char <= 'z':
            new_char = chr(((ord(char) - ord('a') + 13) % 26) + ord('a'))
            result.append(new_char)
        # Sprawdzamy wielkie litery
        elif 'A' <= char <= 'Z':
            new_char = chr(((ord(char) - ord('A') + 13) % 26) + ord('A'))
            result.append(new_char)
        # Reszta znaków (w tym polskie 'ą', 'ę' czy spacje)
        else:
            result.append(char)
            
    return "".join(result)
