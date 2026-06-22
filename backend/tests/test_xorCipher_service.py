from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.xorCipher_service import (  # noqa: E402
    xor_cipher,
    _unescape_unicode_escapes,
)


def test_xor_cipher_roundtrip():
    # Podwójne zastosowanie operacji XOR z tym samym kluczem musi zwrócić tekst wyjściowy (P ^ K ^ K = P).
    original_text = "Tajna Wiadomość 123!"
    key = "super_tajny_klucz"

    encrypted = xor_cipher(original_text, key)
    decrypted = xor_cipher(encrypted, key)

    assert encrypted != original_text
    assert decrypted == original_text


def test_xor_cipher_empty_key_returns_original_text():
    # Jeśli klucz jest pusty, funkcja powinna zwrócić nienaruszony tekst.
    text = "Wiadomość"

    result = xor_cipher(text, "")

    assert result == text


def test_xor_cipher_key_longer_than_text():
    # Algorytm musi działać poprawnie również w sytuacji, gdy klucz jest dłuższy niż sam tekst.
    text = "Krótki"
    key = "BardzoDlugiKluczSzyfrujacy"

    encrypted = xor_cipher(text, key)
    decrypted = xor_cipher(encrypted, key)

    assert decrypted == text


def test_unescape_unicode_escapes_with_escaped_chars():
    # Sprawdza poprawne dekodowanie znaków zapisanych jako literały unicode.
    escaped_text = r"\u0015\x16"

    result = _unescape_unicode_escapes(escaped_text)

    assert len(result) == 2
    assert result[0] == chr(0x15)
    assert result[1] == chr(0x16)


def test_unescape_unicode_escapes_with_normal_text():
    # Jeśli w tekście nie ma sekwencji ucieczki, funkcja ma zwrócić go bez zmian.
    normal_text = "Zwykły tekst bez escapowania"

    result = _unescape_unicode_escapes(normal_text)

    assert result == normal_text