import io
import struct

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