from typing import List
from langchain.tools import tool
import connect
import requests

API_URL = "https://www.warcraftlogs.com/api/v2/client"

PLAYER_DETAILS_QUERY = """
query GetPlayerDetails($code: String!, $fightIDs: [Int]) {
    reportData {
        report(code: $code) {
            playerDetails(fightIDs: $fightIDs)
        }
    }
}
"""


@tool
def get_player_class_and_spec(report_code: str, fight_ids: List[int], character_name: str):
    """
    Look up a player's class and spec(s) in a specific Warcraft Logs report.
    Use the report code and fight IDs returned by find_most_relevant_log.
    Returns the class, role, and every spec the player used across those fights
    (with how many fights on each), since players can switch specs mid-report.
    """

    try:
        token = connect.return_token()
    except Exception as e:
        return f"Error: could not authenticate with Warcraft Logs ({e})."

    if not token:
        return "Error: no auth token returned. Check API credentials."

    try:
        response = requests.post(
            url=API_URL,
            json={
                "query": PLAYER_DETAILS_QUERY,
                "variables": {"code": report_code, "fightIDs": fight_ids},
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        return "Error: request timed out."
    except requests.exceptions.HTTPError as e:
        return f"Error: HTTP {response.status_code}: {e}"
    except requests.exceptions.RequestException as e:
        return f"Error: network error: {e}"
    except ValueError:
        return "Error: response was not valid JSON."

    if "errors" in data:
        return f"Error: GraphQL error: {data['errors']}"

    report = data.get("data", {}).get("reportData", {}).get("report")
    if report is None:
        return f"Error: report '{report_code}' not found (may be expired, private, or mistyped)."

    # playerDetails is a JSON scalar, so the payload is nested one level deeper:
    # report.playerDetails -> {"data": {"playerDetails": {"tanks": [], "healers": [], "dps": []}}}
    details = (
        (report.get("playerDetails") or {})
        .get("data", {})
        .get("playerDetails", {})
    )

    roles = {"tanks": "tank", "healers": "healer", "dps": "dps"}
    for key, role in roles.items():
        for player in details.get(key, []):
            if player.get("name") == character_name:
                return {
                    "name": player.get("name"),
                    "class": player.get("type"),
                    "role": role,
                    "specs": player.get("specs", []),  # e.g. [{"spec": "Arms", "count": 3}]
                    "report_code": report_code,
                }

    available = sorted(
        p.get("name")
        for key in roles
        for p in details.get(key, [])
        if p.get("name")
    )
    return (
        f"Character '{character_name}' not found in playerDetails for the given fights. "
        f"Players found: {available[:15]}"
    )