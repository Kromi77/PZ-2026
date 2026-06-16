export const UI_TEXT = {
  app: {
    title: 'PZ-2026',
    subtitle: 'Steganography Lab - szyfrowanie, ukrywanie i odczyt wiadomości w plikach BMP oraz WAV.',
    badge: 'Projekt laboratoryjny',
  },

  tabs: {
    encode: 'Kodowanie i ukrywanie',
    decode: 'Odczyt i dekodowanie',
  },

  encoder: {
    title: 'Koder wiadomości',
    eyebrow: 'Moduł kodowania',
    description: 'Zaszyfruj wiadomość, ukryj ją w nośniku i pobierz gotowy plik.',

    textToHide: 'Tekst do ukrycia',
    textPlaceholder: 'Wpisz tajną wiadomość...',

    cipherMethod: 'Metoda szyfrowania',

    key: 'Klucz',
    keyPlaceholder: 'Wpisz klucz',

    carrierFile: 'Plik nośnika',
    clickToUpload: 'Kliknij, aby wybrać plik',
    allowedFiles: 'Obsługiwane formaty: .BMP lub .WAV',
    selectedFile: 'Wybrano',

    bmpSliders: 'Kanały BMP',
    wavSlider: 'Głębia LSB dla WAV',
    sliderValue: 'Wartość',
    slidersHint: 'Ustaw liczbę bitów wykorzystywanych do ukrycia informacji.',

    deploymentMode: 'Tryb rozmieszczenia',
    continuous: 'Ciągłe',
    uniform: 'Równomierne',

    encodeButton: 'Zakoduj i ukryj wiadomość',
    encoding: 'Kodowanie...',

    originalMedia: 'Oryginalny nośnik',
    encodedMedia: 'Zakodowany nośnik',
    previewPanel: 'Podgląd i eksport',
    downloadEncodedFile: 'Pobierz zakodowany plik',
    noResult: 'Po zakończeniu kodowania pojawi się tutaj plik wynikowy.',
  },

  decoder: {
    title: 'Dekoder wiadomości',
    eyebrow: 'Moduł dekodowania',
    description: 'Wczytaj zakodowany nośnik i odczytaj ukrytą wiadomość.',

    encodedFile: 'Zakodowany plik',
    clickToUpload: 'Kliknij, aby wybrać plik',
    allowedFiles: 'Obsługiwane formaty: .BMP lub .WAV',
    selectedFile: 'Wybrano',

    key: 'Klucz',
    keyPlaceholder: 'Wpisz klucz, jeśli jest wymagany',
    keyHint:
      'Dla Atbash i ROT13 zostaw puste. Pozostałe szyfry wymagają klucza zgodnego z metodą szyfrowania.',

    decodeButton: 'Odczytaj i odszyfruj wiadomość',
    decoding: 'Odczytywanie...',

    selectedMedia: 'Wybrany nośnik',

    results: 'Wyniki odczytu',
    messageDetected: 'Wykryto wiadomość',
    cipherUsed: 'Użyty szyfr',
    deploymentMode: 'Tryb rozmieszczenia',
    bitsExtracted: 'Odczytane bity',
    decryptedText: 'Odszyfrowana wiadomość',

    uploadHint:
      'Prześlij zakodowany plik i uruchom dekodowanie, aby zobaczyć szczegóły odczytu.',
  },

  mediaPreview: {
    audioNotSupported: 'Twoja przeglądarka nie obsługuje elementu audio.',
    empty: 'Brak pliku do podglądu.',
  },

  common: {
    yes: 'Tak',
    no: 'Nie',
    file: 'Plik',
  },

  errors: {
    missingText: 'Wpisz tekst do zaszyfrowania.',
    missingFile: 'Wybierz plik.',
    missingKey: 'Podaj klucz dla wybranego szyfru.',
    invalidCaesarKey: 'Klucz dla szyfru Cezara musi być liczbą całkowitą.',
    invalidRailFenceKey:
      'Klucz dla szyfru płotkowego musi być liczbą całkowitą większą lub równą 2.',
    encodingFailed: 'Wystąpił błąd podczas kodowania.',
    encryptionFailed: 'Nie udało się zaszyfrować wiadomości.',
    hidingFailed: 'Nie udało się ukryć wiadomości w pliku.',
    headerInjectionFailed: 'Nie udało się dodać nagłówka.',
    decodingFailed: 'Wystąpił błąd podczas odczytywania.',
  },
}
