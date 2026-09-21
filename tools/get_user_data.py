from langchain.tools import tool
import connect
import requests

@tool
def get_user_data(character_name, server, region):
    """
    Get the player's character data Warcraft logs. Returns 50.
    """
    token = connect.return_token()

    graphql_query = """
    query GetCharacterReports($name: String!, $serverSlug: String!, $serverRegion: String!) {
        characterData {
            character(name: $name, serverSlug: $serverSlug, serverRegion: $serverRegion) {
                id
                name
                classID
                recentReports(limit: 50) {
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

    try:
        response = requests.post(
            url = "https://www.warcraftlogs.com/api/v2/client",
            json={"query": graphql_query, "variables": variables},
            headers={"Authorization": f"Bearer {token}"},
        )
        return response.json()

    except Exception as e:
        return f"Error looking up character: {str(e)}. This might be a spelling issue with the name or server."