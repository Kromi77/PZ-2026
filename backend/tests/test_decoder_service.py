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

from app.services import steganography_service, headerBMP_service, headerWAV_service
from app.schemas.header_schema import BMPHeader, WAVHeader, Cipher, DeploymentMode
from app.services.decoder_service import process_file, _prepare_user_key

def build_test_bmp_pipeline(sliders: list[int] = [1, 1, 1]) -> bytes:
    encrypted_msg = "WHVW" 
    
    pixel_data_size = 4096
    pixel_offset = 54
    file_size = pixel_offset + pixel_data_size
    header_bytes = bytearray(pixel_offset)
    header_bytes[0:2] = b"BM"
    header_bytes[2:6] = struct.pack("<I", file_size)
    header_bytes[10:14] = struct.pack("<I", pixel_offset)
    header_bytes[14:18] = struct.pack("<I", 40)
    header_bytes[18:22] = struct.pack("<I", 32)
    header_bytes[22:26] = struct.pack("<I", 32)
    header_bytes[26:28] = struct.pack("<H", 1)
    header_bytes[28:30] = struct.pack("<H", 24)
    bmp_data = bytes(header_bytes) + bytes([170] * pixel_data_size)

    bits = steganography_service.calculate_message_bits(encrypted_msg)
    bmp_header_obj = BMPHeader(
        cipher=Cipher.CEZAR,
        sliders=sliders,
        bits=bits,
        deployment_mode=DeploymentMode.CONTINUOUS
    )
    additional_data = headerBMP_service.bmp_header_to_bits(bmp_header_obj)
    buffer = io.BytesIO(bmp_data)
    modified_bmp = headerBMP_service.inject_data_to_bmp_header(buffer, additional_data).getvalue()

    final_bmp = steganography_service.hide_message_in_bmp(
        bmp_file_content=modified_bmp, 
        encrypted_message=encrypted_msg, 
        uniform=False, 
        sliders=sliders
    )
    return final_bmp

def build_test_wav_pipeline(slider: int = 1) -> bytes:
    encrypted_msg = "WHVW" 
    
    sample_count = 4096
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(1)
        wav_file.setframerate(8000)
        wav_file.writeframes(bytes([128] * sample_count))
    wav_data = buffer.getvalue()

    bits = steganography_service.calculate_message_bits(encrypted_msg)
    wav_header_obj = WAVHeader(
        cipher=Cipher.CEZAR,
        slider=slider,
        bits=bits,
        deployment_mode=DeploymentMode.CONTINUOUS
    )
    additional_data = headerWAV_service.wav_header_to_bits(wav_header_obj)
    wav_buffer = io.BytesIO(wav_data)
    modified_wav = headerWAV_service.inject_data_to_wav_header(wav_buffer, additional_data).getvalue()

    final_wav = steganography_service.hide_message_in_wav(
        wav_file_content=modified_wav, 
        encrypted_message=encrypted_msg, 
        uniform=False, 
        slider=slider
    )
    return final_wav

def test_prepare_user_key_caesar_valid():
    assert _prepare_user_key(Cipher.CEZAR, "5") == 5

def test_prepare_user_key_caesar_invalid():
    with pytest.raises(ValueError, match="musi być liczbą całkowitą"):
        _prepare_user_key(Cipher.CEZAR, "abc")

def test_prepare_user_key_rail_fence_invalid_value():
    with pytest.raises(ValueError, match="większy lub równy 2"):
        _prepare_user_key(Cipher.RAIL_FENCE, "1")

def test_prepare_user_key_missing_required_key():
    with pytest.raises(ValueError, match="wymaga podania klucza"):
        _prepare_user_key(Cipher.VIGENERE, "")

def test_prepare_user_key_no_key_required():
    assert _prepare_user_key(Cipher.ATBASH, "jakis_klucz") is None
    assert _prepare_user_key(Cipher.ROT13, "") is None

def test_process_file_bmp_success():
    final_bmp = build_test_bmp_pipeline(sliders=[1, 1, 1])
    result = process_file(final_bmp, media_type="bmp", key="3")

    assert result["cipher_used"] == Cipher.CEZAR.value
    assert result["deployment_mode"] == "Ciągłe"
    assert result["decrypted_text"] == "TEST" 

def test_process_file_wav_success():
    final_wav = build_test_wav_pipeline(slider=2)
    result = process_file(final_wav, media_type="wav", key="3")

    assert result["cipher_used"] == Cipher.CEZAR.value
    assert result["deployment_mode"] == "Ciągłe"
    assert result["decrypted_text"] == "TEST"

def test_process_file_missing_key_raises_error():
    final_bmp = build_test_bmp_pipeline()

    with pytest.raises(ValueError, match="wymaga podania klucza deszyfrowania"):
        process_file(final_bmp, media_type="bmp", key="")