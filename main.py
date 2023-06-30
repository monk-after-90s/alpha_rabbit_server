import uvicorn
from fastapi import FastAPI
from smart_predict import router as smart_predict_router
from pattern_recognize import router as pattern_recognize_router
from orm import engine

app = FastAPI()


@app.on_event("shutdown")
async def shutdown_event():
    # 关闭数据库连接
    await engine.dispose()


app.include_router(pattern_recognize_router)
app.include_router(smart_predict_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
