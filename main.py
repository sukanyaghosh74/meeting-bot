from fastapi import FastAPI, Request, HTTPException
from slack_bot import handle_slack_event
import uvicorn
import os

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/slack/events")
async def slack_events(request: Request):
    return await handle_slack_event(request)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
