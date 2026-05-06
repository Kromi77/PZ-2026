import io
import struct

from app.schemas.header_schema import BMPHeader, Cipher, DeploymentMode


def bmp_header_to_bites(header: BMPHeader) -> bytes:
    """Konwertuje BMPHeader na ciąg bitów reprezentowany jako bytes.
    
    Format bitów (43 bity razem, spakowane w 6 bajtów):
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


def bites_to_bmp_header(data: bytes) -> BMPHeader:
    """Konwertuje 43-bitowy ciąg bitów na BMPHeader.

    Oczekuje little-endianowego ciągu bajtów o długości co najmniej 6.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("data must be bytes or bytearray")
    if len(data) < 6:
        raise ValueError("data must contain at least 6 bytes")

    value = int.from_bytes(data[:6], byteorder='little')
    cipher_index = value & 0b111
    slider = (value >> 3) & 0b1111
    bites = (value >> 7) & ((1 << 35) - 1)
    deployment_mode_value = (value >> 42) & 0b1

    try:
        cipher = list(Cipher)[cipher_index]
    except IndexError as exc:
        raise ValueError(f"Invalid cipher index: {cipher_index}") from exc

    return BMPHeader(
        cipher=cipher,
        slider=slider,
        bites=bites,
        deployment_mode=DeploymentMode(deployment_mode_value),
    )


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