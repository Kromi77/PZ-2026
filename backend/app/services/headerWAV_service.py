import io
import struct

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