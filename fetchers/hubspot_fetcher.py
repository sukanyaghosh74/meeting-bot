import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("meeting-prep-bot")

HUBSPOT_API_URL = "https://api.hubapi.com/crm/v3/objects/contacts/search"

async def fetch_hubspot_data(meeting_name):
    """
    Fetch relevant CRM/client data from HubSpot filtered by meeting_name (contact or company name).
    Returns a string summary of relevant CRM data.
    """
    api_key = os.getenv("HUBSPOT_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    query = {
        "filterGroups": [
            {"filters": [{"propertyName": "name", "operator": "CONTAINS_TOKEN", "value": meeting_name}]}
        ],
        "properties": ["firstname", "lastname", "email", "company", "phone"],
        "limit": 5
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(HUBSPOT_API_URL, json=query, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            if not results:
                return "No relevant CRM data found."
            summaries = [
                f"- {r['properties'].get('firstname', '')} {r['properties'].get('lastname', '')} | {r['properties'].get('email', '')} | {r['properties'].get('company', '')} | {r['properties'].get('phone', '')}"
                for r in results
            ]
            return "\n".join(summaries)
    except Exception as e:
        logger.error(f"HubSpot fetch error: {e}")
        return "[Error fetching CRM data]"
