# AI Meeting Prep Bot

A production-ready bot that generates AI-powered meeting briefs by integrating Slack, Gmail, Linear, and HubSpot.

## Features
- Fetches latest emails, tasks, and CRM data
- Summarizes into actionable meeting briefs using GPT-4
- Slack integration with `/prepmeeting` command
- Optional email delivery of briefs
- Caching and logging for efficiency

## Setup
1. Clone the repo and `cd` into the folder.
2. Copy `.env.example` to `.env` and fill in your API keys.
3. (Optional) Set up Google/Gmail, Linear, and HubSpot API access.
4. Build and run with Docker:
   ```
   docker build -t meeting-prep-bot .
   docker run --env-file .env -p 8000:8000 meeting-prep-bot
   ```
5. Expose `/slack/events` endpoint to Slack (e.g., via ngrok or cloud deploy).
6. Add the slash command `/prepmeeting` in your Slack app settings.

## File Structure
- `main.py` - FastAPI app entry
- `slack_bot.py` - Slack event handling
- `gpt_summary.py` - AI summarization logic
- `fetchers/` - Data fetchers for Gmail, Linear, HubSpot

## Customization
- Implement fetchers for your data sources in `fetchers/`
- Extend caching, logging, and email features as needed

## License
MIT
