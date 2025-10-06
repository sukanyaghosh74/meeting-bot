import os
import logging
from fastapi import Request, HTTPException
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.signature import SignatureVerifier
from gpt_summary import generate_meeting_brief
from fetchers.gmail_fetcher import fetch_gmail_emails
from fetchers.linear_fetcher import fetch_linear_tasks
from fetchers.hubspot_fetcher import fetch_hubspot_data
import aiosmtplib
from email.message import EmailMessage

slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
client = AsyncWebClient(token=slack_bot_token)
signature_verifier = SignatureVerifier(slack_signing_secret)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("meeting-prep-bot")

async def send_email_brief(subject, body, recipients):
    """
    Send the meeting brief to the given recipients via SMTP (Gmail).
    """
    smtp_host = "smtp.gmail.com"
    smtp_port = 587
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_PASSWORD")
    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        await aiosmtplib.send(
            msg,
            hostname=smtp_host,
            port=smtp_port,
            start_tls=True,
            username=user,
            password=password,
        )
        logger.info(f"Meeting brief emailed to: {recipients}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

async def handle_slack_event(request: Request):
    try:
        if not signature_verifier.is_valid_request(
            await request.body(), request.headers
        ):
            logger.warning("Invalid Slack signature")
            raise HTTPException(status_code=400, detail="Invalid Slack signature")
        data = await request.json()
        # Slack URL verification
        if data.get("type") == "url_verification":
            return {"challenge": data["challenge"]}
        # Slash command (from /prepmeeting)
        if "command" in data and data["command"] == "/prepmeeting":
            # Usage: /prepmeeting <meeting_name> [email1,email2,...]
            text = data.get("text", "General")
            parts = text.split()
            meeting_name = parts[0] if parts else "General"
            emails = []
            if len(parts) > 1:
                emails = [e.strip() for e in parts[1].split(",") if "@" in e]
            channel_id = data.get("channel_id")
            user_id = data.get("user_id")
            logger.info(f"/prepmeeting invoked by {user_id} for {meeting_name}")
            try:
                emails_data = await fetch_gmail_emails(meeting_name)
                tasks = await fetch_linear_tasks(meeting_name)
                crm_data = await fetch_hubspot_data(meeting_name)
                brief = await generate_meeting_brief(meeting_name, emails_data, tasks, crm_data)
                await client.chat_postMessage(channel=channel_id, text=brief)
                if emails:
                    await send_email_brief(f"Meeting Brief: {meeting_name}", brief, emails)
            except Exception as e:
                logger.error(f"Error generating brief: {e}")
                await client.chat_postMessage(channel=channel_id, text=f":x: Failed to generate meeting brief: {e}")
            return ""
        # App mention (e.g., @bot prepmeeting ...)
        if data.get("event", {}).get("type") == "app_mention":
            event = data["event"]
            user = event["user"]
            channel = event["channel"]
            text = event["text"]
            meeting_name = text.split(" ", 1)[-1] if " " in text else "General"
            logger.info(f"App mention by {user} for {meeting_name}")
            try:
                emails_data = await fetch_gmail_emails(meeting_name)
                tasks = await fetch_linear_tasks(meeting_name)
                crm_data = await fetch_hubspot_data(meeting_name)
                brief = await generate_meeting_brief(meeting_name, emails_data, tasks, crm_data)
                await client.chat_postMessage(channel=channel, text=brief)
            except Exception as e:
                logger.error(f"Error generating brief: {e}")
                await client.chat_postMessage(channel=channel, text=f":x: Failed to generate meeting brief: {e}")
        return {"ok": True}
    except Exception as e:
        logger.error(f"Slack event error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
