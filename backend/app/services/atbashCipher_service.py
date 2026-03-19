def atbash_cipher(text: str) -> str:
    """
    Szyfruje i deszyfruje tekst przy użyciu szyfru Atbash.
    Zastępuje literę z początku alfabetu literą z końca (A<->Z, a<->z).
    Znaki niebędące literami standardowego alfabetu (spacje, cyfry, polskie znaki)
    pozostają bez zmian.
    """
    result = []
    for char in text:
        if 'A' <= char <= 'Z':
            # Odwrócenie dla wielkich liter (ASCII 65-90)
            new_char = chr(90 - (ord(char) - 65))
            result.append(new_char)
        elif 'a' <= char <= 'z':
            # Odwrócenie dla małych liter (ASCII 97-122)
            new_char = chr(122 - (ord(char) - 97))
            result.append(new_char)
        else:
            # Pozostaw inne znaki bez zmian
            result.append(char)
            
    return "".join(result)