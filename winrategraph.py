import requests
import json
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import numpy as np
from datetime import datetime
from flask import Flask

load_dotenv()

url_users = "https://start.gg/api/-/gql"
url = "https://api.start.gg/gql/alpha"; 
token = os.getenv("STARTGG_KEY")

def get_chars(user_id, gamer_tag):
    query_newest = '''query GetPlayerInfo($userId: ID!, $pageId: Int) {
        player(id: $userId) {
            gamerTag
            sets(perPage: 25, page: $pageId) {
                pageInfo {
                    page
                    totalPages
                }
                nodes {
                    displayScore(mainEntrantId: $userId)
                    games {
                        selections {
                            character {
                                name
                            }
                            entrant {
                                participants {
                                    player {
                                        gamerTag
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }'''

    cur_user_id = user_id
    page_id = 1

    char_dict = {}
    char_dict['total'] = 0

    while True:
        variables = '{"userId":' + str(cur_user_id) + ', "pageId":' + str(page_id) + '}'
        response = requests.post(url=url, json={"query": query_newest, "variables": variables}, headers={"Authorization": 'Bearer ' + token})
        set_list = json.loads(response.text)["data"]["player"]["sets"]["nodes"]
        if set_list == []:
            break
        for i in set_list:
            if i['games'] is not None:
                for j in i['games']:
                    if j['selections'] is not None:
                        for k in j['selections']:
                            if len(k['entrant']['participants']) == 1 and k['entrant']['participants'][0]['player']['gamerTag'] == gamer_tag:
                                if k['character']['name'] in char_dict.keys():
                                    char_dict[k['character']['name']] += 1
                                else:
                                    char_dict[k['character']['name']] = 1
                        char_dict['total'] += 1

        page_id += 1

    if char_dict['total'] == 0:
        return "No character data"
    
    total = char_dict['total']

    del char_dict['total']

    char_dict = {k: v for k, v in sorted(char_dict.items(), key=lambda item: item[0])}
    if len(char_dict.keys()) >= 2:
        return list(char_dict.keys())[0] + ": " + str(char_dict[list(char_dict.keys())[0]]*100/total) + "%\n" + list(char_dict.keys())[1] + ": " + str(char_dict[list(char_dict.keys())[1]]*100/total) + "%"
    else:
        return list(char_dict.keys())[0] + ": " + str(char_dict[list(char_dict.keys())[0]]*100/total) + "%"
    




search_input = input("Search for a user\n")

query = """
query SearchByGamerTag($search: PlayerQuery!) {
  players(query: $search) {
    pageInfo {
      page
      totalPages
    }
    nodes {
      id
      gamerTag
    }
  }
}
"""

variables = {
    "search": {
        "filter": {
            "gamerTag": search_input,
            "isUser": True,
            "hideTest": True
        },
        "page": 1,
        "perPage": 50
    }
}

params = {
    "query": query,
    "variables": json.dumps(variables)
}

headers = {
    "User-Agent": "curl/8.9.1",
    "Accept": "*/*"
}

response = requests.get(url_users, params=params, headers=headers)
search_users = response.json()['data']['players']['nodes']

count = 1
print()
for user in search_users:
    print(str(count) + ". " + user['gamerTag'])
    print(get_chars(user['id'], user['gamerTag']))
    count += 1

user_sel = int(input("Pick user number"))

user_id = search_users[user_sel - 1]['id']
gamer_tag = search_users[user_sel - 1]['gamerTag']

query = '''query Sets($userId: ID!, $pageId: Int) {
  player(id: $userId) {
    id
    gamerTag
    sets(perPage: 50, page: $pageId) {
      nodes {
        createdAt
        displayScore(mainEntrantId: $userId)
        winnerId
        event {
            id
        }
        slots {
            entrant {
                id
                name
                participants {
                    player {
                        id
                    }
                }
            }
        }
      }
    }
  }
}'''

pageId = 1

variables = '{"userId":' + str(user_id) + ', "pageId":' + str(pageId) + '}'

event_dict = {}


while True:
    variables = '{"userId":' + str(user_id) + ', "pageId":' + str(pageId) + '}'
    response = requests.post(url=url, json={"query": query, "variables": variables}, headers={"Authorization": 'Bearer ' + token})
    response_json = json.loads(response.text)["data"]["player"]["sets"]["nodes"]

    if response_json == []:
        break
    else:
        for item in response_json:
            if item["displayScore"] != "DQ" and len(item["slots"][0]["entrant"]["participants"]) == 1:
                if item["slots"][0]["entrant"]["participants"][0]["player"]["id"] == user_id:
                    playerEntrantId = item["slots"][0]["entrant"]["id"]
                else:
                    playerEntrantId = item["slots"][1]["entrant"]["id"]
                if item["winnerId"] == playerEntrantId:
                    if int(item["createdAt"]) in event_dict.keys():
                        event_dict[int(item["createdAt"])][0] += 1
                    else:
                        event_dict[int(item["createdAt"])] = [1, 0]
                else:
                    if int(item["createdAt"]) in event_dict.keys():
                        event_dict[int(item["createdAt"])][1] += 1
                    else:
                        event_dict[int(item["createdAt"])] = [0, 1]
        pageId += 1
                    

y_arr = []
date_arr = []

total_set_wins = 0
total_set_losses = 0

for item in sorted(event_dict.keys()):
    date_arr.append(datetime.fromtimestamp(item))
    total_set_wins += event_dict[item][0]
    total_set_losses += event_dict[item][1]
    y_arr.append(total_set_wins * 100 /(total_set_wins + total_set_losses))

plt.plot(date_arr, y_arr)
plt.title(gamer_tag + "'s Winrate Graph")
plt.show()





