import requests
import json
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

load_dotenv()

url = "https://api.start.gg/gql/alpha"; 
token = os.getenv("STARTGG_KEY")

queryNewest = '''query GetUser($slug: String!) {
    user(slug: $slug) {
        player {
            id
            gamerTag
        }
    }
}'''



variablesNew = '''{
  "slug": "user/2658abe7"
}'''

response = requests.post(url=url, json={"query": queryNewest, "variables": variablesNew}, headers={"Authorization": 'Bearer ' + token})

userId = json.loads(response.text)["data"]["user"]["player"]["id"]
gamerTag = json.loads(response.text)["data"]["user"]["player"]["gamerTag"]

query = '''query Sets($userId: ID!, $pageId: Int) {
  player(id: $userId) {
    id
    gamerTag
    sets(perPage: 50, page: $pageId) {
      nodes {
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

variables = '{"userId":' + str(userId) + ', "pageId":' + str(pageId) + '}'

eventDict = {}


while True:
    variables = '{"userId":' + str(userId) + ', "pageId":' + str(pageId) + '}'
    response = requests.post(url=url, json={"query": query, "variables": variables}, headers={"Authorization": 'Bearer ' + token})
    responseJson = json.loads(response.text)["data"]["player"]["sets"]["nodes"]

    if responseJson == []:
        break
    else:
        for item in responseJson:
            if item["displayScore"] != "DQ" and len(item["slots"][0]["entrant"]["participants"]) == 1:
                if item["slots"][0]["entrant"]["participants"][0]["player"]["id"] == userId:
                    playerEntrantId = item["slots"][0]["entrant"]["id"]
                else:
                    playerEntrantId = item["slots"][1]["entrant"]["id"]
                if item["winnerId"] == playerEntrantId:
                    if item["event"]["id"] in eventDict.keys():
                        eventDict[item["event"]["id"]][0] += 1
                    else:
                        eventDict[item["event"]["id"]] = [1, 0]
                else:
                    if item["event"]["id"] in eventDict.keys():
                        eventDict[item["event"]["id"]][1] += 1
                    else:
                        eventDict[item["event"]["id"]] = [0, 1]
        pageId += 1
                    

xArr = []
yArr = []

totalSetWins = 0
totalSetLosses = 0
count = 0

for item in sorted(eventDict.keys()):
    xArr.append(count)
    totalSetWins += eventDict[item][0]
    totalSetLosses += eventDict[item][1]
    yArr.append(totalSetWins/(totalSetWins + totalSetLosses))
    count += 1

plt.plot(xArr, yArr)
plt.title(gamerTag + "'s Winrate Graph")
plt.show()





