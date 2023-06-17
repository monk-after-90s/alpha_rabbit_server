from fastapi import FastAPI
from smart_predict import router

app = FastAPI()
app.include_router(router)
