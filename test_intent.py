# test_intent.py
from intent import detect_intent_code

test_queries = [
    "你们的产品支持退货吗？",       # 期望意图：1
    "你好",                        # 期望意图：2
    "今天天气不错",                # 模糊输入，期望意图：2
    "价格是多少"                   # 期望意图：1
]

for q in test_queries:
    code = detect_intent_code(q)
    print(f"输入: {q:<20} => 意图编号: {code}")