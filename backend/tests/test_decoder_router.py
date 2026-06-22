from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import app

from tests.test_decoder_service import build_test_bmp_pipeline

client = TestClient(app)

def test_decoder_api_rejects_invalid_media_type():
    response = client.post(
        "/decoder/process",
        files={"file": ("test.png", b"dummy content", "image/png")},
        data={"media_type": "png", "key": "3"}
    )
    
    assert response.status_code == 400
    assert "Nieobsługiwany format" in response.json()["detail"] or "Analiza pliku wykazała brak" in response.json()["detail"]

def test_decoder_api_bmp_success():
    final_bmp = build_test_bmp_pipeline(sliders=[2, 0, 1])
    
    response = client.post(
        "/decoder/process",
        files={"file": ("test.bmp", final_bmp, "image/bmp")},
        data={
            "media_type": "bmp",
            "key": "3"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message_detected"] is True
    assert data["cipher_used"] == "Szyfr Cezara"
    assert data["decrypted_text"] == "TEST"

def test_decoder_api_bmp_missing_key():
    final_bmp = build_test_bmp_pipeline()
    
    response = client.post(
        "/decoder/process",
        files={"file": ("test.bmp", final_bmp, "image/bmp")},
        data={
            "media_type": "bmp",
            "key": ""
        }
    )
    
    assert response.status_code == 400
    assert "wymaga podania klucza" in response.json()["detail"]

def test_decoder_api_rejects_empty_file():
    response = client.post(
        "/decoder/process",
        files={"file": ("pusty.bmp", b"", "image/bmp")},
        data={"media_type": "bmp", "key": "3"}
    )
    
    assert response.status_code == 400
    assert "Analiza pliku wykazała brak" in response.json()["detail"]

def test_decoder_api_rejects_corrupted_file():
    response = client.post(
        "/decoder/process",
        files={"file": ("smieci.bmp", b"To nie jest poprawny obraz BMP", "image/bmp")},
        data={"media_type": "bmp", "key": "3"}
    )
    
    assert response.status_code == 400
    assert "uszkodzenie" in response.json()["detail"].lower() or "nie jest" in response.json()["detail"].lower()