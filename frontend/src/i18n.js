export const UI_TEXT = {
  app: {
    title: "PZ-2026",
  },

  tabs: {
    encode: "Kodowanie i ukrywanie",
    decode: "Odczyt i dekodowanie",
  },

  encoder: {
    title: "Koder",

    textToHide: "Tekst do ukrycia",
    textPlaceholder: "Wpisz tajną wiadomość...",

    cipherMethod: "Metoda szyfrowania",

    key: "Klucz",
    keyPlaceholder: "Wpisz klucz",

    carrierFile: "Plik nośnika (.bmp, .wav)",
    clickToUpload: "Kliknij, aby wybrać plik",
    allowedFiles: "Pliki .BMP lub .WAV",
    selectedFile: "Wybrano",

    bmpSliders: "Suwaki BMP (0–8 bitów na piksel)",
    wavSlider: "Suwak WAV (0–8 LSB)",
    sliderValue: "Wartość",

    deploymentMode: "Tryb rozmieszczenia",
    continuous: "Ciągłe",
    uniform: "Równomierne",

    encodeButton: "Zakoduj i ukryj",
    encoding: "Kodowanie...",

    originalMedia: "Oryginalny nośnik",
    encodedMedia: "Zakodowany nośnik",
    downloadEncodedFile: "Pobierz zakodowany plik",
  },

  decoder: {
    title: "Dekoder",

    encodedFile: "Zakodowany plik (.bmp, .wav)",
    clickToUpload: "Kliknij, aby wybrać plik",
    allowedFiles: "Pliki .BMP lub .WAV",
    selectedFile: "Wybrano",

    key: "Klucz",
    keyPlaceholder: "Wpisz klucz, jeśli jest wymagany",
    keyHint:
      "Wymagany dla szyfru Cezara, Vigenère’a, XOR, płotkowego i kolumnowego. Dla Atbash i ROT13 zostaw puste.",

    decodeButton: "Odczytaj i odszyfruj",
    decoding: "Odczytywanie...",

    selectedMedia: "Wybrany nośnik",

    results: "Wyniki",
    messageDetected: "Wykryto wiadomość:",
    cipherUsed: "Użyty szyfr:",
    deploymentMode: "Tryb rozmieszczenia:",
    bitsExtracted: "Odczytane bity:",
    decryptedText: "Odszyfrowana wiadomość:",

    uploadHint:
      "Prześlij zakodowany plik i kliknij przycisk odczytu, aby zobaczyć wyniki.",
  },

  mediaPreview: {
    audioNotSupported: "Twoja przeglądarka nie obsługuje elementu audio.",
  },

  common: {
    yes: "Tak",
    no: "Nie",
  },

  errors: {
    missingText: "Wpisz tekst do zaszyfrowania.",
    missingFile: "Wybierz plik.",
    encodingFailed: "Wystąpił błąd podczas kodowania.",
    decodingFailed: "Wystąpił błąd podczas odczytywania.",
  },
};