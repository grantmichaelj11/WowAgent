from langchain.tools import tool
import connect
import requests

@tool
def find_most_relevant_log(fight_ids, encounterID: int, target_difficulty: int, character_name: str):
    """
    Retrieve all relevant logs that will be used to analyze a players performance. Data is gathered from "get_user_data.py"
    Before running the tool you should inquire about the specific fight the user wants
    Look through every encounter to find the relevant logs. Do not skip any.
    """

    try:
        token = connect.return_token()
    except Exception as e:
        return f"Error: could not authenticate with Warcraft Logs ({e}). Cannot proceed with lookup."

    if not token:
        return "Error: no auth token returned. Check API credentials."

    graphql_query = """
    query GetReport($code: String!, $encounterID: Int!, $difficulty: Int!) {
        reportData {
            report(code: $code) {
            code
            title
            startTime
            endTime
            masterData {
                actors(type: null) {
                    id
                    name
                }
            }
            fights(encounterID: $encounterID, difficulty: $difficulty) {
                id
                name
                difficulty
                kill
                startTime
                endTime
                encounterID
                }
            }
        }
    }
    """

    encounters = {}
    errors = {}

    for code in fight_ids:
        report_code = code.get('code') if isinstance(code, dict) else code

        if not report_code:
            errors[str(code)] = "Missing 'code' field in fight_ids entry."
            continue

        variables = {"code": report_code, "encounterID": encounterID, "difficulty": target_difficulty}

        try:
            response = requests.post(
                url="https://www.warcraftlogs.com/api/v2/client",
                json={"query": graphql_query, "variables": variables},
                headers={"Authorization": f"Bearer {token}"},
                timeout=15,
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            errors[report_code] = "Request timed out."
            continue
        except requests.exceptions.HTTPError as e:
            errors[report_code] = f"HTTP error {response.status_code}: {e}"
            continue
        except requests.exceptions.RequestException as e:
            errors[report_code] = f"Network error: {e}"
            continue

        try:
            data = response.json()
        except ValueError:
            errors[report_code] = "Response was not valid JSON."
            continue

        # GraphQL can return 200 OK but still carry an "errors" field
        if "errors" in data:
            errors[report_code] = f"GraphQL error: {data['errors']}"
            continue

        report = (
            data.get('data', {})
                .get('reportData', {})
                .get('report')
        )

        if report is None:
            errors[report_code] = f"Report code '{report_code}' not found (may be expired, private, or mistyped)."
            continue

        all_fights = report.get('fights', [])
        all_actors = report.get('masterData', {}).get('actors', [])

        if len(all_fights) == 0:
            errors[report_code] = f"No fights found for encounterID={encounterID}, difficulty={target_difficulty} in this report."
            continue

        actor_ids_to_upload = [actor['id'] for actor in all_actors if actor.get('name') == character_name]

        if not actor_ids_to_upload:
            available_names = sorted({a.get('name') for a in all_actors if a.get('name')})
            errors[report_code] = (
                f"Character '{character_name}' not found in this report's roster. "
                f"Similar/available names: {available_names[:15]}"
            )
            continue

        fight_ids_to_upload = [fight['id'] for fight in all_fights]
        encounters[report_code] = {'actor_id': actor_ids_to_upload[0], 'fight_ids': fight_ids_to_upload}

    if not encounters and errors:
        return f"No usable logs found. Errors encountered: {errors}"

    return {"encounters": encounters, "errors": errors}