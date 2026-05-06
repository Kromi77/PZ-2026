import hashlib
import io
import struct

from app.schemas.header_schema import WAVHeader, Cipher, DeploymentMode


def wav_header_to_bites_without_hash(header: WAVHeader) -> bytes:
    """Konwertuje WAVHeader na ciąg bitów reprezentowany jako bytes, bez pola hash.
    
    Format bitów (43 bitów razem, spakowanych w 6 bajtów):
    - bity 0-2: cipher (3 bity)
    - bity 3-6: slider (4 bity)
    - bity 7-41: bites (35 bitów)
    - bit 42: deployment_mode (1 bit)
    """
    # Zakoduj cipher (3 bity, potrzebne do zakodowania 7 enum wartości)
    cipher_index = list(Cipher).index(header.cipher)
    
    # Zakoduj slider (4 bity, zakres 0-8)
    slider = header.slider
    
    # Zakoduj bites (35 bitów)
    bites = header.bites
    
    # Zakoduj deployment_mode (1 bit, wartość 0 lub 1)
    deployment_mode = int(header.deployment_mode)
    
    # Połącz wszystkie bity w jeden integer
    result = 0
    result |= cipher_index              # 3 bity na pozycji 0-2
    result |= (slider << 3)             # 4 bity na pozycji 3-6
    result |= (bites << 7)              # 35 bitów na pozycji 7-41
    result |= (deployment_mode << 42)   # 1 bit na pozycji 42
    
    # Konwertuj na bytes (6 bajtów, little-endian)
    return result.to_bytes(6, byteorder='little')


def wav_header_to_bites(header: WAVHeader) -> bytes:
    """Konwertuje WAVHeader na ciąg bitów reprezentowany jako bytes.

    Format bitów (56 bity razem, spakowanych w 7 bajtów):
    - bity 0-2: cipher (3 bity)
    - bity 3-6: slider (4 bity)
    - bity 7-41: bites (35 bitów)
    - bit 42: deployment_mode (1 bit)
    - bity 43-56: hash (13 bitów)
    """
    core_bytes = wav_header_to_bites_without_hash(header)
    hash_bits = generate_wav_header_hash(header)
    core_value = int.from_bytes(core_bytes, byteorder='little')
    full_value = core_value | (hash_bits << 43)
    return full_value.to_bytes(7, byteorder='little')

def bites_to_wav_header(data: bytes) -> WAVHeader:
    """Konwertuje 51-bitowy ciąg bitów na WAVHeader.

    Oczekuje little-endianowego ciągu bajtów o długości co najmniej 7.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("data must be bytes or bytearray")
    if len(data) < 7:
        raise ValueError("data must contain at least 7 bytes")

    value = int.from_bytes(data[:7], byteorder='little')
    cipher_index = value & 0b111
    slider = (value >> 3) & 0b1111
    bites = (value >> 7) & ((1 << 35) - 1)
    deployment_mode_value = (value >> 42) & 0b1

    try:
        cipher = list(Cipher)[cipher_index]
    except IndexError as exc:
        raise ValueError(f"Invalid cipher index: {cipher_index}") from exc

    return WAVHeader(
        cipher=cipher,
        slider=slider,
        bites=bites,
        deployment_mode=DeploymentMode(deployment_mode_value),
    )


def generate_wav_header_hash(header: WAVHeader) -> int:
    """Oblicza 13-bitowy hash MD5 dla WAVHeader.
    
    Konwertuje header na bity (bez hash), oblicza MD5, i zwraca pierwsze 13 bitów jako integer.
    """
    # Konwertuj header na bity
    header_bytes = wav_header_to_bites_without_hash(header)
    
    # Oblicz MD5 hash
    md5_hash = hashlib.md5(header_bytes).digest()
    
    # Wez pierwsze 2 bajty (16 bitów) i wyodrębnij 13 bitów
    hash_value = int.from_bytes(md5_hash[:2], byteorder='big')
    hash_13_bits = hash_value & 0x1FFF  # Maska na 13 bitów (0x1FFF = 0001111111111111)
    
    return hash_13_bits


def check_wav_header_hash(header: WAVHeader, hash_bytes: bytes) -> bool:
    """Sprawdza czy hash WAVHeader jest zgodny z podanym 13-bitowym hashem.
    
    Args:
        header: WAVHeader do weryfikacji
        hash_bytes: 13 bitów do porównania (jako bytes)
        
    Returns:
        True jeśli hash się zgadza, False w przeciwnym razie
    """
    if not isinstance(hash_bytes, (bytes, bytearray)):
        raise TypeError("hash_bytes must be bytes or bytearray")
    
    # Oblicz hash dla podanego headera
    computed_hash = generate_wav_header_hash(header)
    
    # Konwertuj podane bity na integer
    provided_hash = int.from_bytes(hash_bytes[:2], byteorder='little')
    # Zastosuj maskę na 13 bitów aby mieć pewność
    provided_hash = provided_hash & 0x1FFF
    
    # Porównaj
    return computed_hash == provided_hash


def inject_data_to_wav_header(input_file: io.BytesIO, additional_header_data: bytes) -> io.BytesIO:
    # ustawienie wskaźnika i odczyt danych
    input_file.seek(0)
    content = input_file.read()

    # weryfikacja czy to format RIFF/WAVE (pobieramy identyfikator dynamicznie)
    riff_id = content[:4]  # Zazwyczaj b'RIFF'
    if riff_id not in [b'RIFF', b'RIFX'] or content[8:12] != b'WAVE':
        raise ValueError("Provided file is not a valid WAV format.")

    # szukanie sekcji 'data'
    data_chunk_pos = content.find(b'data')
    if data_chunk_pos == -1:
        raise ValueError("Could not find 'data' chunk.")

    # przygotowanie nowego bloku 'adhr'
    chunk_id = b'adhr'
    chunk_size = len(additional_header_data)
    custom_chunk = chunk_id + struct.pack('<I', chunk_size) + additional_header_data

    # obliczenie nowego rozmiaru RIFF (oryginalny rozmiar z nagłówka + nasz nowy chunk)
    original_riff_size = struct.unpack('<I', content[4:8])[0]
    new_riff_size = original_riff_size + len(custom_chunk)

    output_file = io.BytesIO()

    # zapis oryginalnego identyfikatora (RIFF/RIFX) i nowego rozmiaru
    output_file.write(riff_id)
    output_file.write(struct.pack('<I', new_riff_size))

    # zapis metadanych aż do miejsca wstawienia
    output_file.write(content[8:data_chunk_pos])

    # wstawienie nowych danych
    output_file.write(custom_chunk)

    # zapis reszty pliku (audio)
    output_file.write(content[data_chunk_pos:])

    output_file.seek(0)
    return output_file


def remove_data_from_wav_header(input_file: io.BytesIO) -> io.BytesIO:
    # odczyt danych z pliku
    input_file.seek(0)
    content = input_file.read()

    # znalezienie bloku 'adhr'
    adhr_pos = content.find(b'adhr')
    if adhr_pos == -1:
        # jeśli nie znaleziono, zwracamy plik bez zmian
        input_file.seek(0)
        return input_file

    # odczyt rozmiaru danych w naszym bloku
    chunk_data_size = struct.unpack('<I', content[adhr_pos + 4: adhr_pos + 8])[0]
    total_chunk_len = 8 + chunk_data_size  # ID + Size field + Data

    # obliczenie zredukowanego rozmiaru RIFF
    riff_id = content[:4]
    original_riff_size = struct.unpack('<I', content[4:8])[0]
    new_riff_size = original_riff_size - total_chunk_len

    output_file = io.BytesIO()

    # zapis nagłówka z poprawionym rozmiarem
    output_file.write(riff_id)
    output_file.write(struct.pack('<I', new_riff_size))

    # zapis danych przed blokiem 'adhr'
    output_file.write(content[8:adhr_pos])

    # pominięcie bloku 'adhr' i zapis reszty pliku
    output_file.write(content[adhr_pos + total_chunk_len:])

    output_file.seek(0)
    return output_file