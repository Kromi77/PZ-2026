from __future__ import annotations

import io
import struct
import sys
import wave
from pathlib import Path

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))


from app.schemas.header_schema import Cipher  # noqa: E402
from main import app  # noqa: E402


client = TestClient(app)


def build_base_bmp(pixel_data_size: int = 4096) -> bytes:
	# Bazowy plik BMP do testowania endpointów API.
	pixel_offset = 54
	file_size = pixel_offset + pixel_data_size

	header = bytearray(pixel_offset)
	header[0:2] = b"BM"
	header[2:6] = struct.pack("<I", file_size)
	header[10:14] = struct.pack("<I", pixel_offset)
	header[14:18] = struct.pack("<I", 40)
	header[18:22] = struct.pack("<I", 32)
	header[22:26] = struct.pack("<I", 32)
	header[26:28] = struct.pack("<H", 1)
	header[28:30] = struct.pack("<H", 24)

	return bytes(header) + bytes([170] * pixel_data_size)


def build_base_wav(sample_count: int = 4096) -> bytes:
	# Bazowy plik WAV do testowania endpointów API.
	buffer = io.BytesIO()

	with wave.open(buffer, "wb") as wav_file:
		wav_file.setnchannels(1)
		wav_file.setsampwidth(1)
		wav_file.setframerate(8000)
		wav_file.writeframes(bytes([128] * sample_count))

	return buffer.getvalue()


def test_header_api_inject_and_extract_bmp_roundtrip():
	# Pełny scenariusz API dla BMP: zapis, odczyt i przywrócenie pliku.
	original_bmp = build_base_bmp()
	header_data = {
		"cipher": Cipher.CEZAR.value,
		"sliderR": 2,
		"sliderG": 4,
		"sliderB": 6,
		"bits": 123456,
		"deployment_mode": 0,
	}

	inject_response = client.post(
		"/header/inject-bmp/",
		files={"file": ("input.bmp", original_bmp, "image/bmp")},
		data=header_data,
	)

	# Endpoint powinien zwrócić zmodyfikowany plik, który da się potem odczytać.
	assert inject_response.status_code == 200
	assert inject_response.headers["content-disposition"].startswith("attachment; filename=modified_")

	injected_bmp = inject_response.content

	extract_header_response = client.post(
		"/header/extract-bmp-header/",
		files={"file": ("input.bmp", injected_bmp, "image/bmp")},
	)

	assert extract_header_response.status_code == 200
	assert extract_header_response.json() == {
		"cipher": Cipher.CEZAR.value,
		"sliders": [2, 4, 6],
		"bits": 123456,
		"deployment_mode": 0,
	}

	restore_response = client.post(
		"/header/extract-bmp/",
		files={"file": ("input.bmp", injected_bmp, "image/bmp")},
	)

	assert restore_response.status_code == 200
	assert restore_response.content == original_bmp


def test_header_api_inject_and_extract_wav_roundtrip():
	# Pełny scenariusz API dla WAV: zapis, odczyt i przywrócenie pliku.
	original_wav = build_base_wav()
	header_data = {
		"cipher": Cipher.XOR.value,
		"slider": 5,
		"bits": 987654,
		"deployment_mode": 1,
	}

	inject_response = client.post(
		"/header/inject-wav/",
		files={"file": ("input.wav", original_wav, "audio/wav")},
		data=header_data,
	)

	# Sprawdzamy ten sam scenariusz dla WAV: zapis, odczyt i przywrócenie pliku.
	assert inject_response.status_code == 200
	assert inject_response.headers["content-disposition"].startswith("attachment; filename=modified_")

	injected_wav = inject_response.content

	extract_header_response = client.post(
		"/header/extract-wav-header/",
		files={"file": ("input.wav", injected_wav, "audio/wav")},
	)

	assert extract_header_response.status_code == 200
	assert extract_header_response.json() == {
		"cipher": Cipher.XOR.value,
		"slider": 5,
		"bits": 987654,
		"deployment_mode": 1,
	}

	restore_response = client.post(
		"/header/extract-wav/",
		files={"file": ("input.wav", injected_wav, "audio/wav")},
	)

	assert restore_response.status_code == 200
	assert restore_response.content == original_wav


def test_header_api_rejects_invalid_bmp_file():
	# Endpoint BMP ma zwrócić błąd dla niepoprawnych danych wejściowych.
	response = client.post(
		"/header/inject-bmp/",
		files={"file": ("input.bmp", b"not-a-bmp", "image/bmp")},
		data={
			"cipher": Cipher.CEZAR.value,
			"sliderR": 1,
			"sliderG": 1,
			"sliderB": 1,
			"bits": 1,
			"deployment_mode": 0,
		},
	)

	assert response.status_code == 400
	assert "not a valid BMP format" in response.json()["detail"]


def test_header_api_rejects_invalid_wav_file():
	# Endpoint WAV ma zwrócić błąd dla niepoprawnych danych wejściowych.
	response = client.post(
		"/header/inject-wav/",
		files={"file": ("input.wav", b"not-a-wav", "audio/wav")},
		data={
			"cipher": Cipher.CEZAR.value,
			"slider": 1,
			"bits": 1,
			"deployment_mode": 0,
		},
	)

	assert response.status_code == 400
	assert "not a valid WAV format" in response.json()["detail"]
