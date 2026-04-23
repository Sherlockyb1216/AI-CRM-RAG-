import requests

url = "http://127.0.0.1:5000/chat"
data = {"phone_number": "13800001111", "query": "退货"}

response = requests.post(url, json=data)  # 先不用流式
print("状态码:", response.status_code)
print("响应内容:", repr(response.text))   # repr 可以看到隐藏字符