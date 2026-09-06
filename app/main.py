from fastapi import FastAPI

from app.routes.jd import router as jd_router
from app.routes.tailor import router as tailor_router
from app.routes.upload import router as upload_router

app = FastAPI()

app.include_router(upload_router)
app.include_router(jd_router)
app.include_router(tailor_router)