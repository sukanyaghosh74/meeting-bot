from fastapi import FastAPI, Request, HTTPException
from slack_bot import handle_slack_event
import uvicorn
import os
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("meeting-prep-bot")

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/slack/events")
async def slack_events(request: Request):
    """Slack event endpoint for slash commands and events."""
    return await handle_slack_event(request)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
