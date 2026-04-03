from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router

app = FastAPI(title="Paytm Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return {"status": "Paytm Agent is live"}

@app.get("/health")
async def health():
    return {"status": "ok"}