from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import app  # noqa: E402

client = TestClient(app)


def test_xor_encrypt_and_decrypt_endpoints_roundtrip():
    # Testuje standardowe endpointy szyfrujące i deszyfrujące.
    original_text = "Sekretny Tekst API"
    key = "KluczAPI"

    # Szyfrowanie
    encrypt_response = client.post(
        "/encrypt/xor",
        json={"text": original_text, "key": key}
    )
    assert encrypt_response.status_code == 200
    encrypted_text = encrypt_response.json()["output"]
    assert encrypted_text != original_text

    # Deszyfrowanie
    decrypt_response = client.post(
        "/decrypt/xor",
        json={"text": encrypted_text, "key": key}
    )
    assert decrypt_response.status_code == 200
    assert decrypt_response.json()["output"] == original_text


def test_xor_encrypt_and_decrypt_file_endpoints_roundtrip():
    # Używamy danych, które po operacji XOR nie tworzą znaków nowej linii (\n, \r)
    original_text = "12345"
    key = "ABCDE"
    file_content = f"{original_text}\n{key}".encode("latin1")

    # Szyfrowanie przez plik
    encrypt_response = client.post(
        "/encrypt/xor/file",
        files={"file": ("input.txt", file_content, "text/plain")}
    )
    assert encrypt_response.status_code == 200
    encrypted_text = encrypt_response.json()["output"]

    # Deszyfrowanie przez plik z użyciem tego samego klucza
    decrypt_file_content = f"{encrypted_text}\n{key}".encode("latin1")
    decrypt_response = client.post(
        "/decrypt/xor/file",
        files={"file": ("encrypted.txt", decrypt_file_content, "text/plain")}
    )

    assert decrypt_response.status_code == 200
    assert decrypt_response.json()["output"] == original_text


def test_xor_file_endpoint_rejects_wrong_content_type():
    # Endpoint powinien wymuszać typ pliku text/plain.
    response = client.post(
        "/encrypt/xor/file",
        files={"file": ("input.pdf", b"not a text file", "application/pdf")}
    )

    assert response.status_code == 400
    assert "Plik musi być typu .txt" in response.json()["detail"]


def test_xor_file_endpoint_rejects_missing_lines():
    # Plik z jedną linijką (brak klucza) powinien spowodować błąd 400.
    response = client.post(
        "/encrypt/xor/file",
        files={"file": ("input.txt", b"Tylko jedna linia", "text/plain")}
    )

    assert response.status_code == 400
    assert "Plik musi zawierać dwie linie" in response.json()["detail"]