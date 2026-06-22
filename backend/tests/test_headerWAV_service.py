from __future__ import annotations

import io
import sys
import wave
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))


from app.schemas.header_schema import Cipher, DeploymentMode, WAVHeader  # noqa: E402
from app.services.headerWAV_service import (  # noqa: E402
	bits_to_wav_header,
	check_wav_header_hash,
	extract_wav_header_from_file,
	generate_wav_header_hash,
	inject_data_to_wav_header,
	remove_data_from_wav_header,
	wav_header_to_bits,
	wav_header_to_bits_without_hash,
)


def build_base_wav(sample_count: int = 4096) -> bytes:
	# Prosty WAV z jednym kanałem i stałą próbką, żeby test był deterministyczny.
	buffer = io.BytesIO()

	with wave.open(buffer, "wb") as wav_file:
		wav_file.setnchannels(1)
		wav_file.setsampwidth(1)
		wav_file.setframerate(8000)
		wav_file.writeframes(bytes([128] * sample_count))

	return buffer.getvalue()


def make_wav_header() -> WAVHeader:
	# Jedna, stała konfiguracja dla testów kodowania i hasha.
	return WAVHeader(
		cipher=Cipher.XOR,
		slider=5,
		bits=987654,
		deployment_mode=DeploymentMode.UNIFORM,
	)


def test_wav_header_to_bits_roundtrip_preserves_values():
	# Sprawdza zgodność kodowania i dekodowania nagłówka WAV.
	header = make_wav_header()

	# Najważniejszy test: kodowanie i dekodowanie muszą zachować dane.
	core_bytes = wav_header_to_bits_without_hash(header)
	full_bytes = wav_header_to_bits(header)

	assert len(core_bytes) == 6
	assert len(full_bytes) == 7

	roundtrip_header = bits_to_wav_header(full_bytes)

	assert roundtrip_header.cipher == header.cipher
	assert roundtrip_header.slider == header.slider
	assert roundtrip_header.bits == header.bits
	assert roundtrip_header.deployment_mode == header.deployment_mode


def test_wav_header_hash_helpers_match():
	# Weryfikuje, czy hash z nagłówka i hash w polu dodatkowym są takie same.
	header = make_wav_header()
	full_bytes = wav_header_to_bits(header)
	hash_value = (int.from_bytes(full_bytes, byteorder="little") >> 43) & 0x1FFF
	hash_bytes = hash_value.to_bytes(2, byteorder="little")

	assert generate_wav_header_hash(header) == hash_value
	assert check_wav_header_hash(header, hash_bytes) is True


def test_wav_header_hash_helpers_reject_wrong_hash():
	# Błędny hash albo zły typ wejścia powinny zostać odrzucone.
	header = make_wav_header()

	assert check_wav_header_hash(header, b"\x00\x00") is False

	with pytest.raises(TypeError, match="hash_bytes must be bytes or bytearray"):
		check_wav_header_hash(header, "invalid")


def test_wav_header_inject_and_remove_roundtrip():
	# Sprawdza, czy modyfikacja pliku WAV jest odwracalna.
	header = make_wav_header()
	original_wav = build_base_wav()
	additional_data = wav_header_to_bits(header)

	# Jeśli usuwanie działa poprawnie, dostaniemy z powrotem pierwotny plik.
	injected_wav = inject_data_to_wav_header(io.BytesIO(original_wav), additional_data).getvalue()
	restored_wav = remove_data_from_wav_header(io.BytesIO(injected_wav)).getvalue()

	assert injected_wav != original_wav
	assert restored_wav == original_wav


def test_extract_wav_header_from_file_roundtrip():
	# Odczyt nagłówka po wstrzyknięciu danych powinien zwrócić te same wartości.
	header = make_wav_header()
	original_wav = build_base_wav()
	injected_wav = inject_data_to_wav_header(io.BytesIO(original_wav), wav_header_to_bits(header)).getvalue()

	extracted_header = extract_wav_header_from_file(io.BytesIO(injected_wav))

	assert extracted_header.cipher == header.cipher
	assert extracted_header.slider == header.slider
	assert extracted_header.bits == header.bits
	assert extracted_header.deployment_mode == header.deployment_mode


def test_extract_wav_header_from_file_rejects_invalid_magic():
	# Nieprawidłowy plik WAV ma zakończyć się błędem walidacji.
	with pytest.raises(ValueError, match="not a valid WAV format"):
		extract_wav_header_from_file(io.BytesIO(b"not-a-wav"))
