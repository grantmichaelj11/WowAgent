from langchain.tools import tool
import connect
import requests

@tool
def extract_top_logs(encounter: int, difficulty: int, class_name: str, spec_name: str):
    """
    Take the top log for the class/spec and use it for comparison.
    """

    token = connect.return_token()
    
    graphql_query = """
    query TopLogs {
        worldData {
            encounter(id: $encounterId) {
            name
            characterRankings(
                className: $className
                specName: $specName
                metric: dps
                difficulty: $difficulty
                page: 1
            )
            }
        }
    }
    """

    variables = {
        "encounterId": encounter,
        "difficulty": difficulty,
        "className": class_name,
        "specName": spec_name
    }

    response = requests.post(
        url = "https://www.warcraftlogs.com/api/v2/client",
        json={"query": graphql_query, "variables": variables},
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()

    return data

