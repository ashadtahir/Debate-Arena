import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai.api import DebateRespondRequest, DebateRespondResponse, ErrorResponse, debate_respond
from ai.config import get_settings

logging.basicConfig(level=get_settings().log_level)

app = FastAPI(
    title="DebateArena API",
    description="Backend API for DebateArena",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "DebateArena Backend Running",
    }


@app.post("/api/debate/respond", response_model=DebateRespondResponse, responses={400: {"model": ErrorResponse}})
async def respond(request: DebateRespondRequest):
    return await debate_respond(request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
