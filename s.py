import json
with open('j.json', 'r') as f:
    a = json.loads(f.read())

print(a)
