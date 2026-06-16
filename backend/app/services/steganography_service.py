"""
Moduł steganografii - ukrywanie oraz ekstraktowanie zaszyfrowanych wiadomości w mediach.

Technika: LSB (Least Significant Bit) - ukrywa dane w najmniej znaczących bitach pikseli (BMP)
lub próbek dźwięku (WAV).
"""

import struct


class LSBSteganography:
    """Steganografia wykorzystująca metodę LSB (Least Significant Bit)."""
    
    @staticmethod
    def text_to_binary(text: str) -> str:
        """Konwertuje tekst na binarny ciąg bitów z prefiksem długości.
        
        Format: [4 bajty: długość][wiadomość]
        """
        # Konwertuj tekst na bajty (UTF-8)
        text_bytes = text.encode('utf-8')
        length = len(text_bytes)
        
        # Prefiks: 4 bajty (32 bity) na długość
        binary = format(length, '032b')
        
        # Dodaj bity wiadomości
        for byte_val in text_bytes:
            binary += format(byte_val, '08b')
        
        return binary
    
    @staticmethod
    def binary_to_text(binary: str) -> str:
        """Konwertuje binarny ciąg bitów z powrotem na tekst.
        
        Czyta 4 bajty (32 bity) na długość, potem dokładnie tyle bajtów.
        Prawidłowo obsługuje UTF-8 bez double-encoding.
        """
        if len(binary) < 32:
            return ""
        
        # Odczytaj prefiks długości (4 bajty = 32 bity)
        length_binary = binary[:32]
        length = int(length_binary, 2)
        
        # Sprawdź czy mamy wystarczająco bitów
        required_bits = 32 + (length * 8)
        if len(binary) < required_bits:
            return ""
        
        # Odczytaj dokładnie 'length' bajtów
        text_binary = binary[32:32 + (length * 8)]
        
        # Konwertuj bity na bajty (nie znaki!)
        text_bytes = bytearray()
        for i in range(0, len(text_binary), 8):
            byte = text_binary[i:i+8]
            if len(byte) == 8:
                text_bytes.append(int(byte, 2))
        
        # Dekoduj bajty jako UTF-8
        try:
            return text_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback na latin-1 jeśli UTF-8 nie działa
            return text_bytes.decode('latin-1', errors='replace')

    @staticmethod
    def calculate_message_bits(message: str) -> int:
        """Zwraca liczbę bitów potrzebnych do ukrycia wiadomości (prefiks 32-bit + dane)."""
        return len(LSBSteganography.text_to_binary(message))
    
    @staticmethod
    def hide_in_bmp(bmp_data: bytes, secret_message: str, uniform: bool = False) -> bytes:
        """
        Ukrywa zaszyfrowaną wiadomość w pliku BMP.

        Tryb ciągły (uniform=False): bity zapisywane kolejno od bajtu 0.
        Tryb równomierny (uniform=True): bity rozłożone równomiernie w całym
        obszarze pikseli wg wzoru: pozycja[i] = floor(i * krok),
        gdzie krok = pojemność_nośnika / liczba_bitów_wiadomości.

        Args:
            bmp_data: Zawartość pliku BMP
            secret_message: Zaszyfrowana wiadomość do ukrycia
            uniform: Czy użyć równomiernego rozmieszczenia

        Returns:
            Zmodyfikowana zawartość BMP z ukrytą wiadomością
        """
        # Odczytaj offset danych pikseli z nagłówka BMP (bajty 10-13)
        pixel_offset = struct.unpack('<I', bmp_data[10:14])[0]

        header = bmp_data[:pixel_offset]
        pixel_data = bytearray(bmp_data[pixel_offset:])
        
        header = bmp_data[:pixel_offset]
        pixel_data = bytearray(bmp_data[pixel_offset:])

        secret_bits = LSBSteganography.text_to_binary(secret_message)
        
        n_bits = len(secret_bits)
        n_carrier = len(pixel_data)

        # Sprawdź czy jest wystarczająco miejsca
        if n_bits > n_carrier:
            raise ValueError(
                f"Wiadomość zbyt długa. Maksimum bitów: {n_carrier}, "
                f"potrzeba: {n_bits}"
            )

        if uniform:
            # Model równomiernego rozpraszania: krok = pojemność / liczba_bitów
            step = n_carrier / n_bits
            for i, bit in enumerate(secret_bits):
                pos = int(i * step)
                pixel_data[pos] = (pixel_data[pos] & 0xFE) | int(bit)
        else:
            # Ukryj bity w LSB pikseli (tryb ciągły)
            for i, bit in enumerate(secret_bits):
                pixel_data[i] = (pixel_data[i] & 0xFE) | int(bit)
        
        return header + bytes(pixel_data)

    @staticmethod
    def extract_from_bmp(
        bmp_data: bytes,
        message_length: int = None,
        uniform: bool = False,
        total_bits: int = None,
    ) -> str:
        """
        Ekstraktuje ukrytą wiadomość z pliku BMP.

        W trybie równomiernym (uniform=True) wymagany jest parametr total_bits
        (liczba bitów wiadomości zapisana wcześniej w nagłówku BMPHeader.bits),
        aby odtworzyć ten sam krok rozpraszania co przy ukrywaniu.

        Args:
            bmp_data: Zawartość pliku BMP
            message_length: Nieużywane, zachowane dla kompatybilności
            uniform: Czy wiadomość była ukryta trybem równomiernym
            total_bits: Całkowita liczba ukrytych bitów (z nagłówka BMPHeader.bits)

        Returns:
            Wyekstraktowana zaszyfrowana wiadomość
        """
        # Odczytaj offset danych pikseli z nagłówka BMP (bajty 10-13)
        pixel_offset = struct.unpack('<I', bmp_data[10:14])[0]
        pixel_data = bmp_data[pixel_offset:]

        if uniform and total_bits:
            # Odczyt z tych samych pozycji co przy ukrywaniu
            step = len(pixel_data) / total_bits
            secret_bits = ''.join(
                str(pixel_data[int(i * step)] & 1) for i in range(total_bits)
            )
        else:
            # Ekstrakcja bitów ciągła
            secret_bits = ''.join(str(byte_val & 1) for byte_val in pixel_data)
        
        # Konwertuj bity na tekst (binary_to_text sam obsługuje separator)
        return LSBSteganography.binary_to_text(secret_bits)
    
    @staticmethod
    def hide_in_wav(wav_data: bytes, secret_message: str, uniform: bool = False) -> bytes:
        """
        Ukrywa zaszyfrowaną wiadomość w pliku WAV.

        Tryb ciągły (uniform=False): bity zapisywane kolejno od pierwszej próbki.
        Tryb równomierny (uniform=True): bity rozłożone równomiernie w całym
        obszarze danych audio wg wzoru: pozycja[i] = floor(i * krok),
        gdzie krok = pojemność_nośnika / liczba_bitów_wiadomości.

        Args:
            wav_data: Zawartość pliku WAV
            secret_message: Zaszyfrowana wiadomość do ukrycia
            uniform: Czy użyć równomiernego rozmieszczenia

        Returns:
            Zmodyfikowana zawartość WAV z ukrytą wiadomością
        """
        # Znajdź gdzie zaczynają się dane dźwiękowe (zwykle byte 44)
        # Szukamy znacznika 'data'
        data_chunk_pos = wav_data.find(b'data')
        if data_chunk_pos == -1:
            raise ValueError("Nie znaleziono sekcji 'data' w pliku WAV")

        data_size_pos = data_chunk_pos + 4
        data_size = struct.unpack('<I', wav_data[data_size_pos:data_size_pos + 4])[0]

        audio_data_start = data_chunk_pos + 8
        audio_data = bytearray(wav_data[audio_data_start:audio_data_start + data_size])

        secret_bits = LSBSteganography.text_to_binary(secret_message)
        
        n_bits = len(secret_bits)
        n_carrier = len(audio_data)

        # Sprawdź czy jest wystarczająco miejsca
        if n_bits > n_carrier:
            raise ValueError(
                f"Wiadomość zbyt długa. Maksimum bitów: {n_carrier}, "
                f"potrzeba: {n_bits}"
            )

        if uniform:
            # Model równomiernego rozpraszania: krok = pojemność / liczba_bitów
            step = n_carrier / n_bits
            for i, bit in enumerate(secret_bits):
                pos = int(i * step)
                audio_data[pos] = (audio_data[pos] & 0xFE) | int(bit)
        else:
            # Ukryj bity w LSB próbek dźwięku (tryb ciągły)
            for i, bit in enumerate(secret_bits):
                audio_data[i] = (audio_data[i] & 0xFE) | int(bit)
        
        # Rekonstruuj plik WAV
        result = bytearray(wav_data)
        result[audio_data_start:audio_data_start + data_size] = audio_data
        return bytes(result)

    @staticmethod
    def extract_from_wav(
        wav_data: bytes,
        uniform: bool = False,
        total_bits: int = None,
    ) -> str:
        """
        Ekstraktuje ukrytą wiadomość z pliku WAV.

        W trybie równomiernym (uniform=True) wymagany jest parametr total_bits
        (liczba bitów wiadomości zapisana wcześniej w nagłówku WAVHeader.bits),
        aby odtworzyć ten sam krok rozpraszania co przy ukrywaniu.

        Args:
            wav_data: Zawartość pliku WAV
            uniform: Czy wiadomość była ukryta trybem równomiernym
            total_bits: Całkowita liczba ukrytych bitów (z nagłówka WAVHeader.bits)

        Returns:
            Wyekstraktowana zaszyfrowana wiadomość
        """
        data_chunk_pos = wav_data.find(b'data')
        if data_chunk_pos == -1:
            raise ValueError("Nie znaleziono sekcji 'data' w pliku WAV")

        data_size_pos = data_chunk_pos + 4
        data_size = struct.unpack('<I', wav_data[data_size_pos:data_size_pos + 4])[0]

        audio_data_start = data_chunk_pos + 8
        audio_data = wav_data[audio_data_start:audio_data_start + data_size]
        
        if uniform and total_bits:
            # Odczyt z tych samych pozycji co przy ukrywaniu
            step = len(audio_data) / total_bits
            secret_bits = ''.join(
                str(audio_data[int(i * step)] & 1) for i in range(total_bits)
            )
        else:
            # Ekstrakcja bitów ciągła
            secret_bits = ''.join(str(byte_val & 1) for byte_val in audio_data)
        
        # Konwertuj bity na tekst (binary_to_text sam obsługuje separator)
        return LSBSteganography.binary_to_text(secret_bits)


# Funkcje do użytku w routerze
def hide_message_in_bmp(
    bmp_file_content: bytes,
    encrypted_message: str,
    uniform: bool = False,
) -> bytes:
    """Wrapper - ukrywa wiadomość w BMP (tryb ciągły lub równomierny)."""
    return LSBSteganography.hide_in_bmp(bmp_file_content, encrypted_message, uniform)


def extract_message_from_bmp(
    bmp_file_content: bytes,
    uniform: bool = False,
    total_bits: int = None,
) -> str:
    """Wrapper - ekstraktuje wiadomość z BMP (tryb ciągły lub równomierny)."""
    return LSBSteganography.extract_from_bmp(
        bmp_file_content,
        uniform=uniform,
        total_bits=total_bits,
    )


def calculate_message_bits(message: str) -> int:
    """Zwraca liczbę bitów potrzebnych do ukrycia wiadomości — do zapisu w nagłówku."""
    return LSBSteganography.calculate_message_bits(message)


def hide_message_in_wav(
    wav_file_content: bytes,
    encrypted_message: str,
    uniform: bool = False,
) -> bytes:
    """Wrapper - ukrywa wiadomość w WAV (tryb ciągły lub równomierny)."""
    return LSBSteganography.hide_in_wav(wav_file_content, encrypted_message, uniform)


def extract_message_from_wav(
    wav_file_content: bytes,
    uniform: bool = False,
    total_bits: int = None,
) -> str:
    """Wrapper - ekstraktuje wiadomość z WAV (tryb ciągły lub równomierny)."""
    return LSBSteganography.extract_from_wav(
        wav_file_content,
        uniform=uniform,
        total_bits=total_bits,
    )
