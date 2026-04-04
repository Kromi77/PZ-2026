def rail_fence_encrypt(text: str, rails: int) -> str:
    """
    Szyfruje tekst szyfrem płotkowym (Rail Fence).
    Zapisuje znaki zygzakiem na 'rails' szynach, następnie
    odczytuje je wiersz po wierszu.

    Przykład dla rails=3, tekst="WEAREISCOVERED":
      Szyna 0: W . . . E . . . O . . . E .
      Szyna 1: . E . R . I . C . V . R . D
      Szyna 2: . . A . . . S . . . E . . .
      Wynik:   WOEE + ERICVRD + ASE = WOEEERICVRDDASE
    """
    if rails >= len(text):
        return text

    fence = [[] for _ in range(rails)]
    rail = 0
    direction = 1

    for char in text:
        fence[rail].append(char)
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction

    return "".join("".join(row) for row in fence)


def rail_fence_decrypt(text: str, rails: int) -> str:
    """
    Deszyfruje tekst zaszyfrowany szyfrem płotkowym.
    Odtwarza wzorzec zygzaka, wyznacza które pozycje należą
    do każdej szyny, a następnie wstawia znaki na właściwe miejsca.
    """
    n = len(text)
    if rails >= n:
        return text

    # Wyznacz wzorzec: która szyna obsługuje każdą pozycję
    pattern = []
    rail = 0
    direction = 1
    for _ in range(n):
        pattern.append(rail)
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction

    # Sortuj indeksy według szyny — tak jak czytamy przy szyfrowaniu
    indices = sorted(range(n), key=lambda i: pattern[i])

    # Wstaw znaki z tekstu na oryginalne pozycje
    result = [""] * n
    for pos, char in zip(indices, text):
        result[pos] = char

    return "".join(result)
