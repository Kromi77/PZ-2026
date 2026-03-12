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

| Nr | Metoda szyfrowania | Opis zadania | Osoba 1 | Osoba 2 |
|:---|:---|:---|:---:|:---:|
| **1** | **Szyfr Cezara** | Przesunięcie znaków o stałą wartość klucza. | | |
| **2** | **Szyfr Vigenère’a** | Szyfr polialfabetyczny wykorzystujący słowo-klucz. | | |
| **3** | **Szyfr XOR** | Operacja logiczna bitowego XOR na znakach tekstu z wykorzystaniem klucza. | | |
| **4** | **Szyfr Atbash** | Prosty szyfr podstawieniowy polegający na odwróceniu alfabetu (A↔Z, B↔Y). | | |
| **5** | **ROT13** | Specyficzny wariant szyfru Cezara z przesunięciem o 13 pozycji. | | |
| **6** | **Szyfr płotkowy (Rail Fence)**| Szyfr transpozycyjny polegający na zygzakowatym zapisie tekstu. | | |
| **7** | **Szyfr kolumnowy** | Transpozycja tekstu na podstawie klucza ustalającego kolejność kolumn w macierzy. | | |

### 2.2 Moduł Kodera (Steganografia)
* **Parametryzacja obrazu (BMP):** Suwaki dla kanałów R, G, B określające liczbę bitów (0–8) użytych do zapisu w każdym pikselu.
* **Parametryzacja dźwięku (WAV):** Suwak określający liczbę bitów LSB w każdej próbce dźwięku.
* **Rozmieszczenie danych:**
    * *Ciągłe:* Zapis od początku pliku.
    * *Równomierne:* Rozłożenie bitów informacji w całej objętości pliku (dynamiczny krok).
* **Wizualizacja:** Porównanie graficzne (obraz) i dźwiękowe (oscylogram/waveform) nośnika przed i po procesie kodowania.

### 2.3 Moduł Dekodera
* **Analiza pliku:** Automatyczne sprawdzanie, czy plik zawiera ukrytą wiadomość.
* **Identyfikacja parametrów:** Odczyt trybu rozmieszczenia, liczby bitów na kanał/próbkę oraz identyfikacja użytego algorytmu szyfrowania.
* **Deszyfrowanie:** Automatyczne odkodowanie i odszyfrowanie wiadomości do pierwotnej postaci tekstowej.

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
* Poprawność matematyczna zaimplementowanych szyfrów.
* Jakość wizualna/akustyczna nośnika po ukryciu danych (wpływ suwaków na artefakty).
* Niezawodność dekodera w automatycznym rozpoznawaniu parametrów.
* Czytelność i ergonomia interfejsu użytkownika.
