from __future__ import annotations

import io
import struct
import sys
import wave
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.services.steganography_service import (  # noqa: E402
    LSBSteganography,
    extract_message_from_bmp,
    extract_message_from_wav,
    hide_message_in_bmp,
    hide_message_in_wav,
)


def build_test_bmp(pixel_data_size: int = 4096) -> bytes:
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


def build_test_wav(sample_count: int = 4096) -> bytes:
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(1)
        wav_file.setframerate(8000)
        wav_file.writeframes(bytes([128] * sample_count))

    return buffer.getvalue()


def test_text_to_binary_roundtrip_preserves_utf8():
    message = "Zażółć gęślą jaźń"

    binary = LSBSteganography.text_to_binary(message)

    assert len(binary) == 32 + len(message.encode("utf-8")) * 8
    assert LSBSteganography.binary_to_text(binary) == message


def test_bmp_hide_and_extract_continuous_roundtrip():
    bmp = build_test_bmp()
    message = "Hello BMP"

    encoded = hide_message_in_bmp(bmp, message, uniform=False)

    assert extract_message_from_bmp(encoded, uniform=False) == message


def test_bmp_hide_and_extract_uniform_roundtrip():
    bmp = build_test_bmp()
    message = "Uniform BMP"
    total_bits = LSBSteganography.calculate_message_bits(message)

    encoded = hide_message_in_bmp(bmp, message, uniform=True)

    assert extract_message_from_bmp(
        encoded,
        uniform=True,
        total_bits=total_bits,
    ) == message


def test_wav_hide_and_extract_continuous_roundtrip():
    wav = build_test_wav()
    message = "Hello WAV"

    encoded = hide_message_in_wav(wav, message, uniform=False)

    assert extract_message_from_wav(encoded, uniform=False) == message


def test_wav_hide_and_extract_uniform_roundtrip():
    wav = build_test_wav()
    message = "Uniform WAV"
    total_bits = LSBSteganography.calculate_message_bits(message)

    encoded = hide_message_in_wav(wav, message, uniform=True)

    assert extract_message_from_wav(
        encoded,
        uniform=True,
        total_bits=total_bits,
    ) == message


def test_hide_raises_when_message_does_not_fit_bmp():
    bmp = build_test_bmp(pixel_data_size=64)
    pixel_offset = struct.unpack('<I', bmp[10:14])[0]
    carrier_bytes = len(bmp[pixel_offset:])
    oversized_message = "x" * ((carrier_bytes // 8) + 1)

    with pytest.raises(ValueError, match="Wiadomość zbyt długa"):
        hide_message_in_bmp(bmp, oversized_message, uniform=False)


def test_hide_raises_when_message_does_not_fit_wav():
    wav = build_test_wav(sample_count=64)
    oversized_message = "x" * 32

    with pytest.raises(ValueError, match="Wiadomość zbyt długa"):
        hide_message_in_wav(wav, oversized_message, uniform=False)