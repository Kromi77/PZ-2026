import uvicorn
from fastapi import FastAPI
from app.routers import xorCipher_router as xor
from app.routers import cezarCipher_router as cezar
from app.routers import atbashCipher_router as atbash
from app.routers import rot13_router as rot13
from app.routers import railFenceCipher_router as railfence
from app.routers import vigenereCipher_router as vinegre

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

app.include_router(xor.router)
app.include_router(cezar.router)
app.include_router(atbash.router)
app.include_router(rot13.router)
app.include_router(railfence.router)
app.include_router(vinegre.router)

#should be at the end of file
if __name__ == "__main__":
    host = "127.0.0.1"
    port = 3000

    print("\n" + "=" * 50)
    print("FASTAPI SERVER STARTING")
    print("=" * 50)
    print(f"Base URL:    http://{host}:{port}")
    print(f"Swagger UI:  http://{host}:{port}/docs")
    print(f"ReDoc:       http://{host}:{port}/redoc")
    print("=" * 50 + "\n")

    uvicorn.run("main:app", host=host, port=port, reload=True)