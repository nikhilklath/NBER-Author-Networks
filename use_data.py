import json
out = r"D:\Spring 2022"
with open(out + '/data.json', mode='r', encoding='utf-8') as feedsjson:
    feeds = json.load(feedsjson)

print(feeds)