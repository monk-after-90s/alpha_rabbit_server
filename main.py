from fastapi import FastAPI
from smart_predict import router
from utilities import init_symbol_mapping

app = FastAPI()


@app.on_event("startup")
def startup():
    init_symbol_mapping()


app.include_router(router)
