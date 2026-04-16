def get_key_order(key: str) -> list:
    """
    Konwertuje klucz (słowo) na listę liczb określających kolejność kolumn.
    Litery są numerowane alfabetycznie: a=0, b=1, itd.
    
    Przykład: "KEY" -> 
    K=2, E=0, Y=1 -> [2, 0, 1]
    """
    # Utwórz listę (indeks, litera) i posortuj po literce
    indexed_key = [(i, char.lower()) for i, char in enumerate(key)]
    sorted_key = sorted(indexed_key, key=lambda x: x[1])
    
    # Utwórz listę kolejności
    key_order = [0] * len(key)
    for order, (original_index, _) in enumerate(sorted_key):
        key_order[original_index] = order
    
    return key_order


def columnar_encrypt(text: str, key: str) -> str:
    """
    Szyfruje tekst szyfrem kolumnowym (columnar transposition cipher).
    
    Proces:
    1. Tekst dzielimy na rzędy o długości równej długości klucza
    2. Czytamy kolumny w kolejności określonej przez klucz
    3. Konkatenujemy przeczytane kolumny
    
    Args:
        text: Tekst do zaszyfrowania
        key: Klucz (słowo određające kolejność kolumn)
    
    Returns:
        Tekst zaszyfrowany
    """
    if not text or not key:
        return text
    
    key_order = get_key_order(key)
    key_len = len(key)
    
    # Podzielić tekst na rzędy
    rows = []
    for i in range(0, len(text), key_len):
        row = text[i:i + key_len]
        # Jeśli ostatni rząd jest niekompletny, dopełnić spacjami
        if len(row) < key_len:
            row = row + ' ' * (key_len - len(row))
        rows.append(row)
    
    # Czytać kolumny w kolejności określonej przez klucz
    result = []
    for col_index in range(key_len):
        # Znaleźć oryginalny indeks kolumny
        original_col = key_order.index(col_index)
        # Przeczytać kolumnę w kolejności liczb w kluczu
        for row in rows:
            result.append(row[original_col])
    
    return "".join(result)


def columnar_decrypt(text: str, key: str) -> str:
    """
    Deszyfruje tekst zaszyfrowany szyfrem kolumnowym.
    
    Proces:
    1. Obliczamy długości kolumn (mogą się różnić o 1)
    2. Dzielimy tekst szyfru na segmenty odpowiadające kolumnom
    3. Rekonstruujemy macierz czytając kolumny w właściwej kolejności
    4. Odczytujemy wiersze
    
    Args:
        text: Tekst zaszyfrowany
        key: Klucz (takie samo słowo co przy szyfrowaniu)
    
    Returns:
        Tekst odszyfrowany
    """
    if not text or not key:
        return text
    
    key_order = get_key_order(key)
    key_len = len(key)
    num_rows = len(text) // key_len
    
    # Utworzył macierz do wstawienia deszyfrowanych danych
    matrix = [[''] * key_len for _ in range(num_rows)]
    
    # Wstawiać znaki z tekstu szyfrowanego do kolumn
    text_index = 0
    for col_index in range(key_len):
        # Znaleźć oryginalny indeks kolumny
        original_col = key_order.index(col_index)
        # Wstawić znaki w odpowiednią kolumnę
        for row in range(num_rows):
            matrix[row][original_col] = text[text_index]
            text_index += 1
    
    # Odczytać wiersze
    result = []
    for row in matrix:
        result.extend(row)
    
    return "".join(result).rstrip()  # Usunąć paddingowe spacje na końcu
