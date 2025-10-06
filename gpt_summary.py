import os
import openai
import logging

openai.api_key = os.getenv("OPENAI_API_KEY")
logger = logging.getLogger("meeting-prep-bot")

async def generate_meeting_brief(meeting_name, emails, tasks, crm_data):
    """
    Generate a structured meeting brief using OpenAI GPT-4 (fallback to GPT-3.5-turbo).
    Returns a formatted string summary.
    """
    prompt = f"""
You are an AI assistant. Summarize the following information for a meeting brief. Structure as:
- Key emails and updates
- Tasks pending or relevant
- CRM/client insights
- Suggested discussion points / next actions

Meeting: {meeting_name}

Emails:
{emails}

Tasks:
{tasks}

CRM Data:
{crm_data}
"""
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.5,
        )
        logger.info("Meeting brief generated with GPT-4.")
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"GPT-4 failed, falling back to GPT-3.5-turbo: {e}")
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.5,
            )
            logger.info("Meeting brief generated with GPT-3.5-turbo.")
            return response.choices[0].message.content.strip()
        except Exception as e2:
            logger.error(f"OpenAI API failed: {e2}")
            return ":x: Failed to generate meeting brief due to an internal error."
