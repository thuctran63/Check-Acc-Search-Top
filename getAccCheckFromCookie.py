import json
import re

cookies = []
with open('cookie.txt', 'r') as f:
    cookies = f.read().splitlines()
data = []

for cookie in cookies:
    if not cookie.strip():
        continue
    
    match = re.search(r'ct0=([a-f0-9]+)', cookie)
    if match:
        ct0_value = match.group(1)
        
        data.append({
            "bearer_token": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
            "csrf_token": ct0_value,
            "cookie": cookie
        })

with open('acc_check.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)

print("Dữ liệu đã được lưu vào file data.json thành công.")
