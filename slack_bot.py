import os
from fastapi import Request
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.signature import SignatureVerifier
from gpt_summary import generate_meeting_brief
from fetchers.gmail_fetcher import fetch_gmail_emails
from fetchers.linear_fetcher import fetch_linear_tasks
from fetchers.hubspot_fetcher import fetch_hubspot_data

slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
client = AsyncWebClient(token=slack_bot_token)
signature_verifier = SignatureVerifier(slack_signing_secret)

async def handle_slack_event(request: Request):
    if not signature_verifier.is_valid_request(
        await request.body(), request.headers
    ):
        raise Exception("Invalid Slack signature")
    data = await request.json()
    if data.get("type") == "url_verification":
        return {"challenge": data["challenge"]}
    if data.get("event", {}).get("type") == "app_mention":
        event = data["event"]
        user = event["user"]
        channel = event["channel"]
        text = event["text"]
        # Extract meeting context from text
        meeting_name = text.split(" ", 1)[-1] if " " in text else "General"
        # Fetch data
        emails = await fetch_gmail_emails(meeting_name)
        tasks = await fetch_linear_tasks(meeting_name)
        crm_data = await fetch_hubspot_data(meeting_name)
        # Generate summary
        brief = await generate_meeting_brief(meeting_name, emails, tasks, crm_data)
        # Post to Slack
        await client.chat_postMessage(channel=channel, text=brief)
    return {"ok": True}
