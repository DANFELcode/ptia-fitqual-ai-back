import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.classifier import Classifier
from app.uncertainty_gate import UncertaintyGate

BASE_DIR = Path(__file__).resolve().parent.parent
WEIGHTS_PATH = os.getenv("WEIGHTS_PATH", str(BASE_DIR / "models" / "fitqual.weights.h5"))
CLASS_NAMES_PATH = os.getenv("CLASS_NAMES_PATH", str(BASE_DIR / "models" / "class_names.txt"))
DEFAULT_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"


def get_allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", DEFAULT_ORIGINS)
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    if "*" in origins:
        raise ValueError("ALLOWED_ORIGINS no puede contener '*'.")
    return origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Se ejecuta una sola vez al arrancar: carga el modelo y crea el umbral.
    app.state.classifier = Classifier(WEIGHTS_PATH, CLASS_NAMES_PATH)
    app.state.gate = UncertaintyGate()
    yield


app = FastAPI(title="FitQual AI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/predict")
def predict(file: UploadFile | None = File(default=None)):
    if file is None:
        raise HTTPException(status_code=400, detail="Falta la imagen en el campo 'file'.")
    data = file.file.read()
    try:
        top3 = app.state.classifier.predict(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return app.state.gate.evaluate(top3)
