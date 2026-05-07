"""
Moduł steganografii - ukrywanie oraz ekstraktowanie zaszyfrowanych wiadomości w mediach.

Technika: LSB (Least Significant Bit) - ukrywa dane w najmniej znaczących bitach pikseli (BMP)
lub próbek dźwięku (WAV).
"""

import struct
import io
from typing import Tuple, Optional


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
    def hide_in_bmp(bmp_data: bytes, secret_message: str) -> bytes:
        """
        Ukrywa zaszyfrowaną wiadomość w pliku BMP.
        
        Metoda: Modyfikuje najmniej znaczący bit (LSB) każdego bajtu piksela.
        Każdy bajt BMP może ukryć 1 bit wiadomości.
        
        Args:
            bmp_data: Zawartość pliku BMP
            secret_message: Zaszyfrowana wiadomość do ukrycia
            
        Returns:
            Zmodyfikowana zawartość BMP z ukrytą wiadomością
        """
        # BMP header ma 54 bajty, dane pikseli zaczynają się od bajtu 54
        header = bmp_data[:54]
        pixel_data = bytearray(bmp_data[54:])
        
        # Konwertuj wiadomość na bity
        secret_bits = LSBSteganography.text_to_binary(secret_message)
        
        # Sprawdź czy jest wystarczająco miejsca
        if len(secret_bits) > len(pixel_data):
            raise ValueError(
                f"Wiadomość zbyt długa. Maksimum bitów: {len(pixel_data)}, "
                f"potrzeba: {len(secret_bits)}"
            )
        
        # Ukryj bity w LSB pikseli
        for i, bit in enumerate(secret_bits):
            # Usuń LSB i wstaw tajny bit
            pixel_data[i] = (pixel_data[i] & 0xFE) | int(bit)
        
        return header + bytes(pixel_data)
    
    @staticmethod
    def extract_from_bmp(bmp_data: bytes, message_length: int = None) -> str:
        """
        Ekstraktuje ukrytą wiadomość z pliku BMP.
        
        Args:
            bmp_data: Zawartość pliku BMP
            message_length: Długość wiadomości (jeśli znana)
            
        Returns:
            Wyekstraktowana zaszyfrowana wiadomość
        """
        # BMP header ma 54 bajty
        pixel_data = bmp_data[54:]
        
        # Ekstrakcja bitów
        secret_bits = ''
        for byte_val in pixel_data:
            secret_bits += str(byte_val & 1)  # Weź LSB
        
        # Konwertuj bity na tekst (binary_to_text sam obsługuje separator)
        return LSBSteganography.binary_to_text(secret_bits)
    
    @staticmethod
    def hide_in_wav(wav_data: bytes, secret_message: str) -> bytes:
        """
        Ukrywa zaszyfrowaną wiadomość w pliku WAV.
        
        Metoda: Modyfikuje najmniej znaczący bit każdej próbki dźwięku.
        WAV zawiera nagłówek (zwykle 44 bajty) i dane dźwiękowe.
        
        Args:
            wav_data: Zawartość pliku WAV
            secret_message: Zaszyfrowana wiadomość do ukrycia
            
        Returns:
            Zmodyfikowana zawartość WAV z ukrytą wiadomością
        """
        # Znajdź gdzie zaczynają się dane dźwiękowe (zwykle byte 44)
        # Szukamy znacznika 'data'
        header = wav_data
        data_chunk_pos = wav_data.find(b'data')
        
        if data_chunk_pos == -1:
            raise ValueError("Nie znaleziono sekcji 'data' w pliku WAV")
        
        # Wielkość danych audio znajduje się 4 bajty po 'data'
        data_size_pos = data_chunk_pos + 4
        data_size = struct.unpack('<I', wav_data[data_size_pos:data_size_pos + 4])[0]
        
        # Dane dźwiękowe zaczynają się 8 bajtów po 'data'
        audio_data_start = data_chunk_pos + 8
        audio_data = bytearray(wav_data[audio_data_start:audio_data_start + data_size])
        
        # Konwertuj wiadomość na bity
        secret_bits = LSBSteganography.text_to_binary(secret_message)
        
        # Sprawdź czy jest wystarczająco miejsca
        if len(secret_bits) > len(audio_data):
            raise ValueError(
                f"Wiadomość zbyt długa. Maksimum bitów: {len(audio_data)}, "
                f"potrzeba: {len(secret_bits)}"
            )
        
        # Ukryj bity w LSB próbek dźwięku
        for i, bit in enumerate(secret_bits):
            audio_data[i] = (audio_data[i] & 0xFE) | int(bit)
        
        # Rekonstruuj plik WAV
        result = bytearray(wav_data)
        result[audio_data_start:audio_data_start + data_size] = audio_data
        
        return bytes(result)
    
    @staticmethod
    def extract_from_wav(wav_data: bytes) -> str:
        """
        Ekstraktuje ukrytą wiadomość z pliku WAV.
        
        Args:
            wav_data: Zawartość pliku WAV
            
        Returns:
            Wyekstraktowana zaszyfrowana wiadomość
        """
        # Znajdź sekcję 'data'
        data_chunk_pos = wav_data.find(b'data')
        
        if data_chunk_pos == -1:
            raise ValueError("Nie znaleziono sekcji 'data' w pliku WAV")
        
        # Wielkość danych audio
        data_size_pos = data_chunk_pos + 4
        data_size = struct.unpack('<I', wav_data[data_size_pos:data_size_pos + 4])[0]
        
        # Dane dźwiękowe
        audio_data_start = data_chunk_pos + 8
        audio_data = wav_data[audio_data_start:audio_data_start + data_size]
        
        # Ekstrakcja bitów
        secret_bits = ''
        for byte_val in audio_data:
            secret_bits += str(byte_val & 1)
        
        # Konwertuj bity na tekst (binary_to_text sam obsługuje separator)
        return LSBSteganography.binary_to_text(secret_bits)


# Funkcje do użytku w routerze
def hide_message_in_bmp(bmp_file_content: bytes, encrypted_message: str) -> bytes:
    """Wrapper - ukrywa wiadomość w BMP."""
    return LSBSteganography.hide_in_bmp(bmp_file_content, encrypted_message)


def extract_message_from_bmp(bmp_file_content: bytes) -> str:
    """Wrapper - ekstraktuje wiadomość z BMP."""
    return LSBSteganography.extract_from_bmp(bmp_file_content)


def hide_message_in_wav(wav_file_content: bytes, encrypted_message: str) -> bytes:
    """Wrapper - ukrywa wiadomość w WAV."""
    return LSBSteganography.hide_in_wav(wav_file_content, encrypted_message)


def extract_message_from_wav(wav_file_content: bytes) -> str:
    """Wrapper - ekstraktuje wiadomość z WAV."""
    return LSBSteganography.extract_from_wav(wav_file_content)
