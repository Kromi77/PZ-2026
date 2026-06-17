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
    def hide_in_bmp(bmp_data: bytes, secret_message: str, uniform: bool = False, sliders: list[int] = None) -> bytes:
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
            sliders: Liczba bitów do wykorzystania na kanał [R, G, B]

        Returns:
            Zmodyfikowana zawartość BMP z ukrytą wiadomością
        """
        if sliders is None:
            sliders = [1, 1, 1]
            
        # Odczytaj offset danych pikseli z nagłówka BMP (bajty 10-13)
        pixel_offset = struct.unpack('<I', bmp_data[10:14])[0]

        header = bmp_data[:pixel_offset]
        pixel_data = bytearray(bmp_data[pixel_offset:])

        secret_bits = LSBSteganography.text_to_binary(secret_message)
        n_bits = len(secret_bits)

        slider_r, slider_g, slider_b = sliders[0], sliders[1], sliders[2]
        pattern = [slider_b, slider_g, slider_r] # Kolejność BGR dla typowego BMP
        bits_per_group = sum(pattern)
        
        if bits_per_group == 0:
            raise ValueError("Pojemność nośnika wynosi 0 (wszystkie suwaki = 0).")

        group_size = 3
        mapping = []
        for byte_offset in range(group_size):
            for bit_offset in range(pattern[byte_offset]):
                mapping.append((byte_offset, bit_offset))

        def get_bit_position(idx):
            group_idx = idx // bits_per_group
            bit_idx_in_group = idx % bits_per_group
            byte_offset, bit_in_byte = mapping[bit_idx_in_group]
            return group_idx * group_size + byte_offset, bit_in_byte

        num_complete_groups = len(pixel_data) // group_size
        remainder_bytes = len(pixel_data) % group_size
        total_capacity = num_complete_groups * bits_per_group
        for i in range(remainder_bytes):
            total_capacity += pattern[i]

        # Sprawdź czy jest wystarczająco miejsca
        if n_bits > total_capacity:
            raise ValueError(
                f"Wiadomość zbyt długa. Maksimum bitów: {total_capacity}, "
                f"potrzeba: {n_bits}"
            )

        step = (total_capacity / n_bits) if uniform else 1
        for i, bit in enumerate(secret_bits):
            pos_idx = int(i * step)
            byte_idx, b_offset = get_bit_position(pos_idx)
            val = int(bit)
            mask = ~(1 << b_offset) & 0xFF
            pixel_data[byte_idx] = (pixel_data[byte_idx] & mask) | (val << b_offset)
        
        return header + bytes(pixel_data)

    @staticmethod
    def extract_from_bmp(
        bmp_data: bytes,
        message_length: int = None,
        uniform: bool = False,
        total_bits: int = None,
        sliders: list[int] = None,
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
            sliders: Liczba bitów wykorzystana na kanał [R, G, B]

        Returns:
            Wyekstraktowana zaszyfrowana wiadomość
        """
        if sliders is None:
            sliders = [1, 1, 1]
            
        # Odczytaj offset danych pikseli z nagłówka BMP (bajty 10-13)
        pixel_offset = struct.unpack('<I', bmp_data[10:14])[0]
        pixel_data = bmp_data[pixel_offset:]

        slider_r, slider_g, slider_b = sliders[0], sliders[1], sliders[2]
        pattern = [slider_b, slider_g, slider_r]
        bits_per_group = sum(pattern)
        
        if bits_per_group == 0:
            return ""

        group_size = 3
        mapping = []
        for byte_offset in range(group_size):
            for bit_offset in range(pattern[byte_offset]):
                mapping.append((byte_offset, bit_offset))

        def get_bit_position(idx):
            group_idx = idx // bits_per_group
            bit_idx_in_group = idx % bits_per_group
            byte_offset, bit_in_byte = mapping[bit_idx_in_group]
            return group_idx * group_size + byte_offset, bit_in_byte

        num_complete_groups = len(pixel_data) // group_size
        remainder_bytes = len(pixel_data) % group_size
        total_capacity = num_complete_groups * bits_per_group
        for i in range(remainder_bytes):
            total_capacity += pattern[i]

        if uniform and total_bits:
            step = total_capacity / total_bits
            secret_bits_list = []
            for i in range(total_bits):
                pos_idx = int(i * step)
                byte_idx, b_offset = get_bit_position(pos_idx)
                extracted_bit = (pixel_data[byte_idx] >> b_offset) & 1
                secret_bits_list.append(str(extracted_bit))
            secret_bits = ''.join(secret_bits_list)
        else:
            secret_bits_list = []
            expected_bits = None  # W trybie ciągłym zawsze ignorujemy total_bits i polegamy na prefiksie 32-bit
            
            for pos_idx in range(total_capacity):
                if expected_bits is not None and pos_idx >= expected_bits:
                    break
                    
                byte_idx, b_offset = get_bit_position(pos_idx)
                extracted_bit = (pixel_data[byte_idx] >> b_offset) & 1
                secret_bits_list.append(str(extracted_bit))
                
                if expected_bits is None and len(secret_bits_list) == 32:
                    length_binary = ''.join(secret_bits_list[:32])
                    length = int(length_binary, 2)
                    expected_bits = 32 + (length * 8)
                    if expected_bits > total_capacity:
                        expected_bits = total_capacity
                        
            secret_bits = ''.join(secret_bits_list)
        
        # Konwertuj bity na tekst (binary_to_text sam obsługuje separator)
        return LSBSteganography.binary_to_text(secret_bits)
    
    @staticmethod
    def hide_in_wav(wav_data: bytes, secret_message: str, uniform: bool = False, slider: int = 1) -> bytes:
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
            slider: Liczba bitów używana do ukrycia w każdej próbce (0-8)

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

        bits_per_group = slider
        if bits_per_group == 0:
            raise ValueError("Pojemność nośnika wynosi 0 (suwak = 0).")
            
        total_capacity = len(audio_data) * slider
        
        def get_bit_position(idx):
            byte_idx = idx // bits_per_group
            bit_in_byte = idx % bits_per_group
            return byte_idx, bit_in_byte

        # Sprawdź czy jest wystarczająco miejsca
        if n_bits > total_capacity:
            raise ValueError(
                f"Wiadomość zbyt długa. Maksimum bitów: {total_capacity}, "
                f"potrzeba: {n_bits}"
            )

        step = (total_capacity / n_bits) if uniform else 1
        for i, bit in enumerate(secret_bits):
            pos_idx = int(i * step)
            byte_idx, b_offset = get_bit_position(pos_idx)
            val = int(bit)
            mask = ~(1 << b_offset) & 0xFF
            audio_data[byte_idx] = (audio_data[byte_idx] & mask) | (val << b_offset)
        
        # Rekonstruuj plik WAV
        result = bytearray(wav_data)
        result[audio_data_start:audio_data_start + data_size] = audio_data
        return bytes(result)

    @staticmethod
    def extract_from_wav(
        wav_data: bytes,
        uniform: bool = False,
        total_bits: int = None,
        slider: int = 1,
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
            slider: Liczba bitów per próbka (0-8)

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
        
        bits_per_group = slider
        if bits_per_group == 0:
            return ""
            
        total_capacity = len(audio_data) * slider
        
        def get_bit_position(idx):
            byte_idx = idx // bits_per_group
            bit_in_byte = idx % bits_per_group
            return byte_idx, bit_in_byte
        
        if uniform and total_bits:
            step = total_capacity / total_bits
            secret_bits_list = []
            for i in range(total_bits):
                pos_idx = int(i * step)
                byte_idx, b_offset = get_bit_position(pos_idx)
                extracted_bit = (audio_data[byte_idx] >> b_offset) & 1
                secret_bits_list.append(str(extracted_bit))
            secret_bits = ''.join(secret_bits_list)
        else:
            secret_bits_list = []
            expected_bits = None  # W trybie ciągłym zawsze ignorujemy total_bits i polegamy na prefiksie 32-bit
            
            for pos_idx in range(total_capacity):
                if expected_bits is not None and pos_idx >= expected_bits:
                    break
                    
                byte_idx, b_offset = get_bit_position(pos_idx)
                extracted_bit = (audio_data[byte_idx] >> b_offset) & 1
                secret_bits_list.append(str(extracted_bit))
                
                if expected_bits is None and len(secret_bits_list) == 32:
                    length_binary = ''.join(secret_bits_list[:32])
                    length = int(length_binary, 2)
                    expected_bits = 32 + (length * 8)
                    if expected_bits > total_capacity:
                        expected_bits = total_capacity
                        
            secret_bits = ''.join(secret_bits_list)
        
        # Konwertuj bity na tekst (binary_to_text sam obsługuje separator)
        return LSBSteganography.binary_to_text(secret_bits)


# Funkcje do użytku w routerze
def hide_message_in_bmp(
    bmp_file_content: bytes,
    encrypted_message: str,
    uniform: bool = False,
    sliders: list[int] = None,
) -> bytes:
    """Wrapper - ukrywa wiadomość w BMP (tryb ciągły lub równomierny)."""
    print(f"Hiding message in BMP: uniform={uniform}, sliders={sliders}")
    return LSBSteganography.hide_in_bmp(bmp_file_content, encrypted_message, uniform, sliders)


def extract_message_from_bmp(
    bmp_file_content: bytes,
    uniform: bool = False,
    total_bits: int = None,
    sliders: list[int] = None,
) -> str:
    """Wrapper - ekstraktuje wiadomość z BMP (tryb ciągły lub równomierny)."""
    return LSBSteganography.extract_from_bmp(
        bmp_file_content,
        uniform=uniform,
        total_bits=total_bits,
        sliders=sliders,
    )


def calculate_message_bits(message: str) -> int:
    """Zwraca liczbę bitów potrzebnych do ukrycia wiadomości — do zapisu w nagłówku."""
    return LSBSteganography.calculate_message_bits(message)


def hide_message_in_wav(
    wav_file_content: bytes,
    encrypted_message: str,
    uniform: bool = False,
    slider: int = 1,
) -> bytes:
    """Wrapper - ukrywa wiadomość w WAV (tryb ciągły lub równomierny)."""
    return LSBSteganography.hide_in_wav(wav_file_content, encrypted_message, uniform, slider)


def extract_message_from_wav(
    wav_file_content: bytes,
    uniform: bool = False,
    total_bits: int = None,
    slider: int = 1,
) -> str:
    """Wrapper - ekstraktuje wiadomość z WAV (tryb ciągły lub równomierny)."""
    return LSBSteganography.extract_from_wav(
        wav_file_content,
        uniform=uniform,
        total_bits=total_bits,
        slider=slider,
    )
