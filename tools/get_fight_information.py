from langchain.tools import tool
import json

@tool
def get_fight_information():
    """
    Get the fight name and difficulty needed for cast history. This information
    will be fed to "find_most_relevant_log".
    """

    with open("fights.json", 'r') as f:
        return json.load(f)