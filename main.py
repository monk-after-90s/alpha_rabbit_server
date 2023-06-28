from fastapi import FastAPI
from smart_predict import router as smart_predict_router
from pattern_recognize import router as pattern_recognize_router

app = FastAPI()

app.include_router(pattern_recognize_router)
app.include_router(smart_predict_router)
