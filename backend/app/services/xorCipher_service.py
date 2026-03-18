def xor_cipher(text, key):
    """
    Szyfruje lub deszyfruje tekst przy użyciu algorytmu XOR.

    Logika opiera się na operacji bitowej XOR:
    $P \oplus K = C$ oraz $C \oplus K = P$
    gdzie P to tekst jawny, K to klucz, a C to szyfrogram.
    """
    if not key:
        return text

    # 1. Dopasowanie długości klucza do długości tekstu
    # Powtarzamy klucz tyle razy, by był co najmniej tak długi jak tekst,
    # a następnie przycinamy go do dokładnej liczby znaków.
    full_key = (key * (len(text) // len(key) + 1))[:len(text)]

    # 2. Proces szyfrowania/deszyfrowania
    # ord(t) - pobiera kod Unicode znaku tekstu
    # ord(k) - pobiera kod Unicode znaku klucza
    # ^      - wykonuje operację bitową XOR
    # chr(...) - zamienia wynikowy kod z powrotem na znak
    encrypted_chars = [
        chr(ord(t) ^ ord(k)) for t, k in zip(text, full_key)
    ]

    # 3. Złożenie listy znaków w jeden ciąg tekstowy
    return "".join(encrypted_chars)