# AI Meeting Prep Bot

A production-ready bot that generates AI-powered meeting briefs by integrating Slack, Gmail, Linear, and HubSpot. Designed to save time and increase productivity by aggregating relevant meeting information into concise briefs.

---

## Features

* **Fetches latest emails, tasks, and CRM data**: Pulls information from Gmail, Linear, and HubSpot.
* **Summarizes into actionable meeting briefs**: Uses GPT-4 to generate summaries with key action items and insights.
* **Slack integration**: `/prepmeeting` command triggers brief generation and delivery.
* **Optional email delivery**: Automatically email generated briefs to participants.
* **Caching and logging**: Ensures efficiency, reduces redundant API calls, and logs activity for debugging.

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/sukanyaghosh74/meeting-bot.git
cd meeting-bot
```

### 2. Environment Variables

Copy `.env.example` to `.env` and populate with your API credentials.

```bash
cp .env.example .env
```

Required environment variables:

```dotenv
SLACK_BOT_TOKEN=your-slack-bot-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
OPENAI_API_KEY=your-openai-api-key
GMAIL_CLIENT_ID=your-gmail-client-id
GMAIL_CLIENT_SECRET=your-gmail-client-secret
LINEAR_API_KEY=your-linear-api-key
HUBSPOT_API_KEY=your-hubspot-api-key
```

### 3. Optional API Setup

* **Gmail API**: Enable Gmail API and generate OAuth credentials.
* **Linear API**: Create API token in Linear settings.
* **HubSpot API**: Generate API key for CRM access.

### 4. Build and Run with Docker

```bash
docker build -t meeting-prep-bot .
docker run --env-file .env -p 8000:8000 meeting-prep-bot
```

### 5. Slack Integration

* Expose `/slack/events` endpoint using ngrok or a cloud deployment.
* Configure a Slash Command `/prepmeeting` in your Slack App pointing to the endpoint.

---

## File Structure

```
meeting-bot/
├── main.py            # FastAPI app entry
├── slack_bot.py       # Slack event handling logic
├── gpt_summary.py     # GPT-4 summarization logic
├── fetchers/          # Fetchers for Gmail, Linear, HubSpot
│   ├── gmail_fetcher.py
│   ├── linear_fetcher.py
│   └── hubspot_fetcher.py
├── cache/             # Caching utilities
├── logs/              # Log files
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Usage

### Trigger via Slack

In any Slack channel:

```text
/prepmeeting
```

The bot fetches latest emails, tasks, and CRM metrics, then posts a concise, actionable meeting brief.

### Direct API Call (Optional)

```python
from main import app
import requests

response = requests.post('http://localhost:8000/generate_brief', json={'meeting_topic': 'Q4 Planning'})
print(response.json())
```

---

## Code Snippets

### Slack Bot Event Handling (slack_bot.py)

```python
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from fastapi import FastAPI, Request
from gpt_summary import generate_meeting_brief

app = App(token=os.environ['SLACK_BOT_TOKEN'], signing_secret=os.environ['SLACK_SIGNING_SECRET'])
fastapi_app = FastAPI()
handler = SlackRequestHandler(app)

@app.command("/prepmeeting")
def handle_prepmeeting(ack, body, client):
    ack("Generating meeting brief...")
    topic = body['text']
    brief = generate_meeting_brief(topic)
    client.chat_postMessage(channel=body['channel_id'], text=brief)

@fastapi_app.post("/slack/events")
async def slack_events(req: Request):
    return await handler.handle(req)
```

### GPT Summarization Logic (gpt_summary.py)

```python
import openai

def generate_meeting_brief(topic: str) -> str:
    """Fetches data from sources and generates a concise meeting brief"""
    emails_summary = fetch_emails_summary(topic)
    tasks_summary = fetch_linear_tasks(topic)
    crm_summary = fetch_hubspot_metrics(topic)
    combined_text = f"Emails:\n{emails_summary}\nTasks:\n{tasks_summary}\nCRM Metrics:\n{crm_summary}"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Summarize the following into actionable meeting brief."},
                  {"role": "user", "content": combined_text}]
    )
    return response.choices[0].message.content
```

### Example Fetcher (fetchers/gmail_fetcher.py)

```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def fetch_emails_summary(topic: str) -> str:
    creds = Credentials.from_authorized_user_file('token.json')
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', q=topic, maxResults=5).execute()
    messages = results.get('messages', [])
    summaries = []
    for msg in messages:
        message = service.users().messages().get(userId='me', id=msg['id']).execute()
        summaries.append(message['snippet'])
    return '\n'.join(summaries)
```

---

## Customization

* Add additional fetchers in `fetchers/` for your own data sources.
* Modify GPT prompt in `gpt_summary.py` for custom brief formats.
* Extend caching in `cache/` and logging in `logs/` for better performance and traceability.
* Enable email delivery by integrating `smtplib` or any transactional email service.

---

## License

MIT License
