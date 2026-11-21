import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.classifier import Classifier
from app.nutrition_table import NutritionTable
from app.uncertainty_gate import UncertaintyGate

BASE_DIR = Path(__file__).resolve().parent.parent
WEIGHTS_PATH = os.getenv("WEIGHTS_PATH", str(BASE_DIR / "models" / "fitqual.weights.h5"))
CLASS_NAMES_PATH = os.getenv("CLASS_NAMES_PATH", str(BASE_DIR / "models" / "class_names.txt"))
NUTRITION_CSV = os.getenv("NUTRITION_CSV", str(BASE_DIR / "data" / "nutrition.csv"))
DEFAULT_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"


def get_allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", DEFAULT_ORIGINS)
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    if "*" in origins:
        raise ValueError("ALLOWED_ORIGINS no puede contener '*'.")
    return origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.classifier = Classifier(WEIGHTS_PATH, CLASS_NAMES_PATH)
    app.state.gate = UncertaintyGate()
    app.state.nutrition = NutritionTable(NUTRITION_CSV)
    yield


class EstimateRequest(BaseModel):
    class_name: str
    grams: float | None = None


app = FastAPI(title="FitQual AI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    # El contrato pide 400 con {"detail": "..."} en español, no el 422 por defecto.
    return JSONResponse(status_code=400,
                        content={"detail": "Solicitud inválida: revisa los datos enviados."})


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


@app.post("/api/estimate")
def estimate(body: EstimateRequest):
    try:
        return app.state.nutrition.estimate(body.class_name, body.grams)
    except KeyError:
        raise HTTPException(status_code=404,
                            detail=f"No hay datos nutricionales para '{body.class_name}'.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
