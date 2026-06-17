from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from main import app  # noqa: E402


client = TestClient(app)


def test_hide_rejects_invalid_deployment_mode():
    response = client.post(
        "/steganography/hide",
        files={"file": ("dummy.bmp", b"not-empty", "application/octet-stream")},
        data={
            "encrypted_message": "abc",
            "media_type": "bmp",
            "deployment_mode": "2",
        },
    )

    assert response.status_code == 400
    assert "Nieobsługiwany tryb rozmieszczenia" in response.json()["detail"]


def test_hide_rejects_unsupported_media_type_with_400():
    response = client.post(
        "/steganography/hide",
        files={"file": ("dummy.bin", b"not-empty", "application/octet-stream")},
        data={
            "encrypted_message": "abc",
            "media_type": "png",
            "deployment_mode": "0",
        },
    )

    assert response.status_code == 400
    assert "Nieobsługiwany typ pliku" in response.json()["detail"]
