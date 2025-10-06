import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("meeting-prep-bot")

LINEAR_API_URL = "https://api.linear.app/graphql"

async def fetch_linear_tasks(meeting_name):
    """
    Fetch relevant tasks from Linear API filtered by meeting_name (project or label).
    Returns a string summary of relevant tasks.
    """
    api_key = os.getenv("LINEAR_API_KEY")
    headers = {"Authorization": api_key, "Content-Type": "application/json"}
    query = {
        "query": f"""
        query Tasks($search: String!) {{
          issues(filter: {{search: $search}}) {{
            nodes {{
              id
              title
              state {{ name }}
              assignee {{ name }}
            }}
          }}
        }}
        """,
        "variables": {"search": meeting_name}
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(LINEAR_API_URL, json=query, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            issues = data.get("data", {}).get("issues", {}).get("nodes", [])
            if not issues:
                return "No relevant tasks found."
            summaries = [
                f"- {i['title']} (State: {i['state']['name']}, Assignee: {i['assignee']['name'] if i['assignee'] else 'Unassigned'})"
                for i in issues
            ]
            return "\n".join(summaries)
    except Exception as e:
        logger.error(f"Linear fetch error: {e}")
        return "[Error fetching tasks]"
