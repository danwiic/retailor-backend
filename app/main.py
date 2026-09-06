from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.jd import router as jd_router
from app.routes.tailor import router as tailor_router
from app.routes.upload import router as upload_router

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://retailor.danpirante.dev",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(jd_router)
app.include_router(tailor_router)