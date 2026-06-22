from __future__ import annotations

import io
import struct
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))


from app.schemas.header_schema import BMPHeader, Cipher, DeploymentMode  # noqa: E402
from app.services.headerBMP_service import (  # noqa: E402
	bmp_header_to_bits,
	bmp_header_to_bits_without_hash,
	bits_to_bmp_header,
	check_bmp_header_hash,
	extract_bmp_header_from_file,
	generate_bmp_header_hash,
	inject_data_to_bmp_header,
	remove_data_from_bmp_header,
)


def build_base_bmp(pixel_data_size: int = 4096) -> bytes:
	# Minimalny poprawny BMP potrzebny do testów round-trip.
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


def make_bmp_header() -> BMPHeader:
	# Stały nagłówek ułatwia porównywanie wyników między testami.
	return BMPHeader(
		cipher=Cipher.CEZAR,
		sliders=[2, 4, 6],
		bits=123456,
		deployment_mode=DeploymentMode.CONTINUOUS,
	)


def test_bmp_header_to_bits_roundtrip_preserves_values():
	# Sprawdza zgodność kodowania i dekodowania nagłówka BMP.
	header = make_bmp_header()

	# Sprawdzamy, czy serializacja i deserializacja dają ten sam obiekt.
	core_bytes = bmp_header_to_bits_without_hash(header)
	full_bytes = bmp_header_to_bits(header)

	assert len(core_bytes) == 7
	assert len(full_bytes) == 8

	roundtrip_header = bits_to_bmp_header(full_bytes)

	assert roundtrip_header.cipher == header.cipher
	assert roundtrip_header.sliders == header.sliders
	assert roundtrip_header.bits == header.bits
	assert roundtrip_header.deployment_mode == header.deployment_mode


def test_bmp_header_hash_helpers_match():
	# Weryfikuje, czy hash liczony z nagłówka jest zgodny z zakodowanym hashem.
	header = make_bmp_header()
	full_bytes = bmp_header_to_bits(header)
	hash_value = (int.from_bytes(full_bytes, byteorder="little") >> 51) & 0x1FFF
	hash_bytes = hash_value.to_bytes(2, byteorder="little")

	assert generate_bmp_header_hash(header) == hash_value
	assert check_bmp_header_hash(header, hash_bytes) is True


def test_bmp_header_hash_helpers_reject_wrong_hash():
	# Sprawdza reakcję na błędny hash oraz niepoprawny typ danych.
	header = make_bmp_header()

	assert check_bmp_header_hash(header, b"\x00\x00") is False

	with pytest.raises(TypeError, match="hash_bytes must be bytes or bytearray"):
		check_bmp_header_hash(header, "invalid")


def test_bmp_header_inject_and_remove_roundtrip():
	# Potwierdza, że wstrzyknięcie i usunięcie danych nie psuje pliku BMP.
	header = make_bmp_header()
	original_bmp = build_base_bmp()
	additional_data = bmp_header_to_bits(header)

	# Wstawienie danych do pliku ma być odwracalne bez utraty treści.
	injected_bmp = inject_data_to_bmp_header(io.BytesIO(original_bmp), additional_data).getvalue()
	restored_bmp = remove_data_from_bmp_header(io.BytesIO(injected_bmp)).getvalue()

	assert injected_bmp != original_bmp
	assert restored_bmp == original_bmp


def test_extract_bmp_header_from_file_roundtrip():
	# Sprawdza odczyt nagłówka z pliku po wcześniejszym wstrzyknięciu danych.
	header = make_bmp_header()
	original_bmp = build_base_bmp()
	injected_bmp = inject_data_to_bmp_header(io.BytesIO(original_bmp), bmp_header_to_bits(header)).getvalue()

	extracted_header = extract_bmp_header_from_file(io.BytesIO(injected_bmp))

	assert extracted_header.cipher == header.cipher
	assert extracted_header.sliders == header.sliders
	assert extracted_header.bits == header.bits
	assert extracted_header.deployment_mode == header.deployment_mode


def test_extract_bmp_header_from_file_rejects_invalid_magic():
	# Plik bez sygnatury BMP ma zostać odrzucony.
	with pytest.raises(ValueError, match="not a valid BMP format"):
		extract_bmp_header_from_file(io.BytesIO(b"not-a-bmp"))
