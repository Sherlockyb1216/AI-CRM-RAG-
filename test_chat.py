# test_chat.py
from chat import SeaChatInterview
from db import clear_history, fetch_chat_history

# 测试手机号
TEST_PHONE = "13800138000"

# 清空历史以重置
clear_history(TEST_PHONE)

# 模拟第一次对话（新用户）
print("=== 新用户测试 ===")
resp1 = SeaChatInterview(TEST_PHONE, "你好")
print("AI回复:", resp1)
print("当前历史长度:", len(fetch_chat_history(TEST_PHONE)))

# 模拟第二次对话（老用户，意图应为“提问”）
print("\n=== 第二次对话，意图为提问 ===")
resp2 = SeaChatInterview(TEST_PHONE, "方便的，你说吧")
print("AI回复:", resp2)
print("当前历史长度:", len(fetch_chat_history(TEST_PHONE)))

# 模拟第三次对话（老用户，意图应为“回答”）
print("\n=== 第三次对话，意图为回答 ===")
resp3 = SeaChatInterview(TEST_PHONE, "你们的产品支持七天无理由退货吗？")
print("AI回复:", resp3)
print("当前历史长度:", len(fetch_chat_history(TEST_PHONE)))