from fastapi import FastAPI
from app.api.routes.transactions import router

app = FastAPI()
app.include_router(router)

@app.get("/")
def root():
    return {"message": "API running"}

