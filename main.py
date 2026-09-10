import tools

def agentic_workflow():
    user_data = tools.get_user_data('Xorbdruid', "area-52", "US")

    print(user_data)

    recentReports = user_data['data']['characterData']['character']['recentReports']['data']

    fight = tools.find_most_relevant_log(recentReports, 3429, 4)

    print(fight)

def run():

    agentic_workflow()
    

run()