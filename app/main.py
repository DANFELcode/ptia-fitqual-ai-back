import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

DEFAULT_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"


def get_allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", DEFAULT_ORIGINS)
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    if "*" in origins:
        raise ValueError("ALLOWED_ORIGINS no puede contener '*'.")
    return origins


app = FastAPI(title="FitQual AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}
