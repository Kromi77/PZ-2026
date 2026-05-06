import hashlib
import io
import struct

from app.schemas.header_schema import BMPHeader, Cipher, DeploymentMode


def bmp_header_to_bites_without_hash(header: BMPHeader) -> bytes:
    """Konwertuje BMPHeader na ciąg bitów reprezentowany jako bytes, bez pola hash.

    Format bitów (51 bitów razem, spakowanych w 7 bajtów):
    - bity 0-2: cipher (3 bity)
    - bity 3-14: slider[0], slider[1], slider[2] (4 bity każdy = 12 bitów razem)
    - bity 15-49: bites (35 bitów)
    - bit 50: deployment_mode (1 bit)
    """
    # Zakoduj cipher (3 bity, potrzebne do zakodowania 7 enum wartości)
    cipher_index = list(Cipher).index(header.cipher)
    
    # Zakoduj trzy wartości slider (4 bity każda)
    slider_values = header.slider
    if len(slider_values) != 3:
        raise ValueError("slider must contain exactly 3 values")
    for val in slider_values:
        if not (0 <= val <= 8):
            raise ValueError(f"slider value {val} out of range 0-8")
    
    # Zakoduj bites (35 bitów)
    bites = header.bites
    
    # Zakoduj deployment_mode (1 bit, wartość 0 lub 1)
    deployment_mode = int(header.deployment_mode)
    
    # Połącz wszystkie bity w jeden integer
    result = 0
    result |= cipher_index                      # 3 bity na pozycji 0-2
    result |= (slider_values[0] << 3)           # 4 bity na pozycji 3-6
    result |= (slider_values[1] << 7)           # 4 bity na pozycji 7-10
    result |= (slider_values[2] << 11)          # 4 bity na pozycji 11-14
    result |= (bites << 15)                     # 35 bitów na pozycji 15-49
    result |= (deployment_mode << 50)           # 1 bit na pozycji 50
    
    # Konwertuj na bytes (7 bajtów, little-endian)
    return result.to_bytes(7, byteorder='little')


def bmp_header_to_bites(header: BMPHeader) -> bytes:
    """Konwertuje BMPHeader na ciąg bitów reprezentowany jako bytes.

    Format bitów (64 bity razem, spakowanych w 8 bajtów):
    - bity 0-2: cipher (3 bity)
    - bity 3-14: slider[0], slider[1], slider[2] (4 bity każdy = 12 bitów razem)
    - bity 15-49: bites (35 bitów)
    - bit 50: deployment_mode (1 bit)
    - bity 51-63: hash (13 bitów)
    """
    core_bytes = bmp_header_to_bites_without_hash(header)
    hash_bits = generate_bmp_header_hash(header)
    core_value = int.from_bytes(core_bytes, byteorder='little')
    full_value = core_value | (hash_bits << 51)
    return full_value.to_bytes(8, byteorder='little')


def bites_to_bmp_header(data: bytes) -> BMPHeader:
    """Konwertuje ciąg bitów na BMPHeader, ignorując pole hash.

    Oczekuje little-endianowego ciągu bajtów o długości co najmniej 7.
    Jeśli podany jest pełny wynik z bmp_header_to_bites(), dodatkowe bity hash zostaną zignorowane.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("data must be bytes or bytearray")
    if len(data) < 7:
        raise ValueError("data must contain at least 7 bytes")

    value = int.from_bytes(data[:7], byteorder='little')
    cipher_index = value & 0b111
    slider_0 = (value >> 3) & 0b1111
    slider_1 = (value >> 7) & 0b1111
    slider_2 = (value >> 11) & 0b1111
    bites = (value >> 15) & ((1 << 35) - 1)
    deployment_mode_value = (value >> 50) & 0b1

    try:
        cipher = list(Cipher)[cipher_index]
    except IndexError as exc:
        raise ValueError(f"Invalid cipher index: {cipher_index}") from exc

    return BMPHeader(
        cipher=cipher,
        slider=[slider_0, slider_1, slider_2],
        bites=bites,
        deployment_mode=DeploymentMode(deployment_mode_value),
    )


def generate_bmp_header_hash(header: BMPHeader) -> int:
    """Oblicza 13-bitowy hash MD5 dla BMPHeader.
    
    Konwertuje header na bity (bez hash), oblicza MD5, i zwraca pierwsze 13 bitów jako integer.
    """
    # Konwertuj header na bity
    header_bytes = bmp_header_to_bites_without_hash(header)
    
    # Oblicz MD5 hash
    md5_hash = hashlib.md5(header_bytes).digest()
    
    # Wez pierwsze 2 bajty (16 bitów) i wyodrębnij 13 bitów
    hash_value = int.from_bytes(md5_hash[:2], byteorder='big')
    hash_13_bits = hash_value & 0x1FFF  # Maska na 13 bitów (0x1FFF = 0001111111111111)
    
    return hash_13_bits


def check_bmp_header_hash(header: BMPHeader, hash_bytes: bytes) -> bool:
    """Sprawdza czy hash BMPHeader jest zgodny z podanym 13-bitowym hashem.
    
    Args:
        header: BMPHeader do weryfikacji
        hash_bytes: 13 bitów do porównania (jako bytes)
        
    Returns:
        True jeśli hash się zgadza, False w przeciwnym razie
    """
    if not isinstance(hash_bytes, (bytes, bytearray)):
        raise TypeError("hash_bytes must be bytes or bytearray")
    
    # Oblicz hash dla podanego headera
    computed_hash = generate_bmp_header_hash(header)
    
    # Konwertuj podane bity na integer
    provided_hash = int.from_bytes(hash_bytes[:2], byteorder='little')
    # Zastosuj maskę na 13 bitów aby mieć pewność
    provided_hash = provided_hash & 0x1FFF
    
    # Porównaj
    return computed_hash == provided_hash


def inject_data_to_bmp_header(input_file: io.BytesIO, additional_header_data: bytes) -> io.BytesIO:
    # odczyt danych z pliku
    input_file.seek(0)
    file_content = input_file.read()

    # weryfikacja nagłówka BMP
    if file_content[:2] != b'BM':
        raise ValueError("Provided file is not a valid BMP format.")

    # pobranie oryginalnego rozmiaru pliku i offsetu (w formacie little-endian)
    original_file_size = struct.unpack('<I', file_content[2:6])[0]
    original_offset = struct.unpack('<I', file_content[10:14])[0]

    # obliczenie nowych wartości po dodaniu bajtów
    data_length = len(additional_header_data)
    new_file_size = original_file_size + data_length
    new_offset = original_offset + data_length

    # tworzenie nowego pliku w pamięci
    output_file = io.BytesIO()

    # zapis nagłówka BMP (z nowym rozmiarem i offsetem)
    output_file.write(b'BM')
    output_file.write(struct.pack('<I', new_file_size))
    output_file.write(file_content[6:10]) # zarezerwowane bajty
    output_file.write(struct.pack('<I', new_offset))

    # zapis oryginalnej struktury DIB i palety kolorów aż do miejsca pikseli
    output_file.write(file_content[14:original_offset])

    # wstawienie dodatkowych danych tuż przed danymi obrazu
    output_file.write(additional_header_data)

    # zapis danych obrazu (pikseli)
    output_file.write(file_content[original_offset:])

    # powrót na początek pliku przed jego zwróceniem
    output_file.seek(0)
    return output_file


def remove_data_from_bmp_header(input_file: io.BytesIO, data_length_to_remove: int) -> io.BytesIO:
    # odczyt danych z pliku
    input_file.seek(0)
    file_content = input_file.read()

    # weryfikacja nagłówka BMP
    if file_content[:2] != b'BM':
        raise ValueError("Provided file is not a valid BMP format.")

    # pobranie obecnego rozmiaru pliku i offsetu
    current_file_size = struct.unpack('<I', file_content[2:6])[0]
    current_offset = struct.unpack('<I', file_content[10:14])[0]

    # obliczenie zredukowanych wartości
    new_file_size = current_file_size - data_length_to_remove
    new_offset = current_offset - data_length_to_remove

    # tworzenie nowego pliku w pamięci
    output_file = io.BytesIO()

    # zapis zaktualizowanego nagłówka BMP
    output_file.write(b'BM')
    output_file.write(struct.pack('<I', new_file_size))
    output_file.write(file_content[6:10]) # zarezerwowane bajty
    output_file.write(struct.pack('<I', new_offset))

    # zapis struktury DIB i palety kolorów
    output_file.write(file_content[14:new_offset])

    # pominięcie ukrytych danych i zapis oryginalnych danych obrazu
    output_file.write(file_content[current_offset:])

    # powrót na początek pliku przed jego zwróceniem
    output_file.seek(0)
    return output_file


def extract_bmp_header_from_file(input_file: io.BytesIO) -> BMPHeader:
    """Odczytuje BMPHeader z pliku BMP (8 bajtów tuż przed danymi obrazu).
    
    Funkcja:
    1. Odczytuje 8 bajtów znajdujących się przed danymi obrazu
    2. Wyciąga pierwsze 51 bitów i konwertuje na BMPHeader
    3. Wyciąga ostatnie 13 bitów (hash)
    4. Weryfikuje hash za pomocą check_bmp_header_hash
    5. Zwraca BMPHeader lub błąd jeśli hash się nie zgadza
    
    Args:
        input_file: BytesIO zawierającego zawartość pliku BMP
        
    Returns:
        BMPHeader jeśli hash jest prawidłowy
        
    Raises:
        ValueError: jeśli plik nie jest prawidłowym BMP lub hash się nie zgadza
    """
    # odczyt danych z pliku
    input_file.seek(0)
    file_content = input_file.read()

    # weryfikacja nagłówka BMP
    if file_content[:2] != b'BM':
        raise ValueError("Provided file is not a valid BMP format.")

    # pobranie offsetu do danych obrazu
    image_offset = struct.unpack('<I', file_content[10:14])[0]

    # sprawdzenie, czy plik zawiera wystarczającą ilość danych
    if image_offset < 8 or len(file_content) < image_offset:
        raise ValueError("File does not contain encrypted information - not enough data before image offset.")

    # odczytanie 8 bajtów tuż przed danymi obrazu
    header_bytes = file_content[image_offset - 8:image_offset]
    
    if len(header_bytes) != 8:
        raise ValueError("File does not contain encrypted information - unable to read 8 bytes.")

    # wyciągnięcie pierwszych 51 bitów (7 bajtów) i konwersja na BMPHeader
    try:
        header = bites_to_bmp_header(header_bytes)
    except (ValueError, TypeError) as e:
        raise ValueError(f"File does not contain encrypted information - invalid header data: {str(e)}")

    # wyciągnięcie ostatnich 13 bitów (bity 51-63 z całych 8 bajtów)
    full_value = int.from_bytes(header_bytes, byteorder='little')
    hash_13_bits = (full_value >> 51) & 0x1FFF

    # konwersja 13 bitów na 2 bajty (little-endian) do porównania
    hash_bytes = hash_13_bits.to_bytes(2, byteorder='little')

    # weryfikacja hash
    if not check_bmp_header_hash(header, hash_bytes):
        raise ValueError("File does not contain encrypted information - hash verification failed.")

    return header