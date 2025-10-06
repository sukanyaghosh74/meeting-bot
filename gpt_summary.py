import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_meeting_brief(meeting_name, emails, tasks, crm_data):
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
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()
