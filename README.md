### Podział Zadań: Moduł Szyfrowania (Kryptografia)

# PZ-2026

Projekt zespołowy

# Zadanie Projektowe – Projekt Zespołowy

**Temat: Implementacja koder-dekodera steganograficznego z modułem wielometodowego szyfrowania danych**

---

## 1. Cel projektu

Celem projektu jest stworzenie aplikacji umożliwiającej ukrywanie informacji tekstowych w plikach BMP i WAV. System musi zapewniać dwustopniowe zabezpieczenie danych: najpierw poprzez proces szyfrowania tekstu jednym z wybranych algorytmów, a następnie poprzez proces steganograficznego ukrycia zaszyfrowanej wiadomości w nośniku multimedialnym.

---

## 2. Wymagania funkcjonalne

### 2.1 Moduł Szyfrowania (Kryptografia)

Aplikacja musi umożliwiać zaszyfrowanie tekstu wejściowego przed jego ukryciem. Zespół zobowiązany jest do implementacji minimum 7 następujących metod szyfrowania. Poniższa tabela przedstawia podział zadań w zespole:

| Nr    | Metoda szyfrowania              | Opis zadania                                                                      |       Osoba 1        |        Osoba 2        | Status |
| :---- | :------------------------------ | :-------------------------------------------------------------------------------- | :------------------: | :-------------------: | :----: |
| **1** | **Szyfr Cezara**                | Przesunięcie znaków o stałą wartość klucza.                                       |    Bogumił Wójcik    |    Kamil Urbański     |   ✅   |
| **2** | **Szyfr Vigenère’a**            | Szyfr polialfabetyczny wykorzystujący słowo-klucz.                                |    Rafał Leszczyk    |                       |        |
| **3** | **Szyfr XOR**                   | Operacja logiczna bitowego XOR na znakach tekstu z wykorzystaniem klucza.         |      Michał Bej      |    Krzysztof Guzik    |        |
| **4** | **Szyfr Atbash**                | Prosty szyfr podstawieniowy polegający na odwróceniu alfabetu (A↔Z, B↔Y).         | Karolina Oleśniewicz | Włodzimierz Palazanov |        |
| **5** | **ROT13**                       | Specyficzny wariant szyfru Cezara z przesunięciem o 13 pozycji.                   |    Michał Wojtala    |   Kacper Mielańczyk   |        |
| **6** | **Szyfr płotkowy (Rail Fence)** | Szyfr transpozycyjny polegający na zygzakowatym zapisie tekstu.                   |    Adam Zadrożny     |                       |        |
| **7** | **Szyfr kolumnowy**             | Transpozycja tekstu na podstawie klucza ustalającego kolejność kolumn w macierzy. |  Oktawian Majerczak  |      Michał Krok      |        |

### 2.2 Moduł Kodera (Steganografia)

- **Parametryzacja obrazu (BMP):** Suwaki dla kanałów R, G, B określające liczbę bitów (0–8) użytych do zapisu w każdym pikselu.
- **Parametryzacja dźwięku (WAV):** Suwak określający liczbę bitów LSB w każdej próbce dźwięku.
- **Rozmieszczenie danych:**
  - _Ciągłe:_ Zapis od początku pliku.
  - _Równomierne:_ Rozłożenie bitów informacji w całej objętości pliku (dynamiczny krok).
- **Wizualizacja:** Porównanie graficzne (obraz) i dźwiękowe (oscylogram/waveform) nośnika przed i po procesie kodowania.

### 2.3 Moduł Dekodera

- **Analiza pliku:** Automatyczne sprawdzanie, czy plik zawiera ukrytą wiadomość.
- **Identyfikacja parametrów:** Odczyt trybu rozmieszczenia, liczby bitów na kanał/próbkę oraz identyfikacja użytego algorytmu szyfrowania.
- **Deszyfrowanie:** Automatyczne odkodowanie i odszyfrowanie wiadomości do pierwotnej postaci tekstowej.

---

## 3. Etapy realizacji projektu

1.  **Etap 1: Logika Kryptograficzna** Implementacja 7 algorytmów szyfrowania i deszyfrowania tekstów `.txt`.
2.  **Etap 2: Silnik Steganograficzny (Media)** Obsługa formatów BMP i WAV. Implementacja suwaków bitów i mechanizmu zapisu bitowego w strukturze plików.
3.  **Etap 3: Algorytmy Rozmieszczenia** Opracowanie matematycznego modelu równomiernego rozpraszania danych w pliku.
4.  **Etap 4: Metadane i Nagłówek** Zaprojektowanie struktury nagłówka, który pozwoli dekoderowi rozpoznać parametry (metoda szyfrowania, liczba bitów, tryb rozmieszczenia).
5.  **Etap 5: Integracja i GUI** Budowa interfejsu z suwakami, podglądem mediów "przed i po" oraz panelem wyboru szyfrów.
6.  **Etap 6: Testy końcowe** Weryfikacja poprawności deszyfrowania przy różnych kombinacjach parametrów i dużych plikach tekstowych.

---

## 4. Kryteria oceny

- Poprawność matematyczna zaimplementowanych szyfrów.
- Jakość wizualna/akustyczna nośnika po ukryciu danych (wpływ suwaków na artefakty).
-

## 5. Wykorzystane technologie

Mając na uwadze dobre praktyki inżynierii oprogramowania, architektura projektu opiera się na separacji logiki biznesowej (Core) od interfejsu użytkownika (GUI).

### Warstwa Prezentacji (GUI)

Odpowiada za interakcję z użytkownikiem, parametryzację steganografii (suwaki) oraz wizualizację nośników przed i po modyfikacji.

- **Język i Framework:**
- **Wizualizacja danych (oscylogramy/obrazy):**

### Logika Biznesowa (Core)

Odpowiada za bezstratne manipulacje na bitach (steganografia) oraz operacje matematyczne (kryptografia).

- **Język programowania:** Python 3.10
- **Przetwarzanie multimediów:**
  - **Pliki BMP:**
  - **Pliki WAV:**
- **Kryptografia:** Autorska implementacja algorytmów szyfrujących (zgodnie z wymogami projektu, brak zewnętrznych bibliotek typu OpenSSL dla głównych zadań).

### Narzędzia Deweloperskie i Organizacja Pracy

- **System kontroli wersji:** Git (repozytorium na platformie GitHub)
- **Zarządzanie zależnościami:**
- Niezawodność dekodera w automatycznym rozpoznawaniu parametrów.
- Czytelność i ergonomia interfejsu użytkownika.

![DancingShrek](https://media.tenor.com/cFPFHbvs2yQAAAAM/shrek-shrek-dance.gif)
