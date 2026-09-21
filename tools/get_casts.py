from langchain.tools import tool
import connect
import requests
from collections import defaultdict

@tool
def get_casts(encounters):
    """
    Returns all cast sequences from all fights. Fights are generated from "find_most_relevant_log"

    There can be more than one fight. If this is asked then you can take all fights.
    """

    token = connect.return_token()

    graphql_query = """
    query getCasts($code: String!, $actorID: Int!, $fightIDs: [Int!]){
        reportData {
            report(code: $code) {
            events(fightIDs: $fightIDs, useActorIDs: true, sourceID: $actorID, useAbilityIDs: true) {
                data
                }
            }
        }
    }
    """

    casts_by_fight = defaultdict(list)

    for encounter in encounters:

        try:
            actor = encounters[encounter]['actor_id']
            fight_ids = encounters[encounter]['fight_ids']
        except TypeError as e:
            print(encounter)
            continue

        variables = {
            "code": encounter,
            "actorID": actor,
            "fightIDs": fight_ids
        }

        response = requests.post(
            url = "https://www.warcraftlogs.com/api/v2/client",
            json={"query": graphql_query, "variables": variables},
            headers={"Authorization": f"Bearer {token}"},
        )

        data = response.json()

        all_events = data['data']['reportData']['report']['events']['data']

        for event in all_events:
            if event['sourceID'] == actor:
                casts_by_fight[f"{encounter}_{event['fight']}"].append(event)

    return casts_by_fight