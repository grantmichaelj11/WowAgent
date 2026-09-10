from langchain.tools import tool
import connect
import requests

GRAPHQL_ENDPOINT = "https://www.warcraftlogs.com/api/v2/client"

def get_user_data(character_name, server, region):
    token = connect.return_token()

    graphql_query = """
    query GetCharacterReports($name: String!, $serverSlug: String!, $serverRegion: String!) {
        characterData {
            character(name: $name, serverSlug: $serverSlug, serverRegion: $serverRegion) {
                id
                name
                classID
                recentReports(limit: 10) {
                    data {
                        code
                        title
                        startTime
                        endTime
                    }
                }
            }
        }
    }
    """

    variables = {
        "name": character_name,
        "serverSlug": server,
        "serverRegion": region,
    }

    response = requests.post(
        url = "https://www.warcraftlogs.com/api/v2/client",
        json={"query": graphql_query, "variables": variables},
        headers={"Authorization": f"Bearer {token}"},
    )

    return response.json()

def find_most_relevant_log(fight_ids, encounterID, target_difficulty):
    token = connect.return_token()

    graphql_query = """
    query GetReport($code: String!, $encounterID: Int!, $difficulty: Int!) {
        reportData {
            report(code: $code) {
            code
            title
            startTime
            endTime
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

    encounters = []

    for code in fight_ids:
        variables = {"code": code['code'], "encounterID": encounterID, "difficulty": target_difficulty}

        response = requests.post(
            url = "https://www.warcraftlogs.com/api/v2/client",
            json={"query": graphql_query, "variables": variables},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Need to match fight name and difficulty:
        data = response.json()

        all_fights = data['data']['reportData']['report']['fights']

        if all_fights is not []:
            encounters.append(code['code'])

    return encounters

def get_actor_id():
    pass

def get_casts():
    pass



############# ACTUAL TOOL CALLS HERE
@tool
def spell_casting_context():
    """
    Uses get_user_data(), find_most_relevant_log(), get_actor_id(), get_casts
    """
    pass

@tool
def get_top_logs():
    """
    Extracts the logs of the best players
    """
    token = connect.return_token()

