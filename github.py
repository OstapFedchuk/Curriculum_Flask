import requests
import json

token = "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"

query = '{user(login: "OstapFedchuk"){contributionsCollection {contributionCalendar {totalContributions weeks {contributionDays {contributionCount date}}}}}}'

url = "https://api.github.com/graphql"

x = requests.post(url, json={'query':query}, headers={"Authorization": "Bearer " + token})

print(x)
#print(x.json())

json_data = x.json()
print(json_data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"])
save_file = open("savedata.json", "w")
json.dump(json_data,save_file,indent=6)
save_file.close()

