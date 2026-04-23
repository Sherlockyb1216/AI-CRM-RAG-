import requests

url = "http://127.0.0.1:5000/chat"
data = {"phone_number": "13800001111", "query": "你好"}

response = requests.post(url, json=data, stream=True)

if response.status_code == 200:
    for chunk in response.iter_content(chunk_size=1, decode_unicode=True):
        if chunk:
            print(chunk, end='', flush=True)
    print()
else:
    print("Error:", response.text)