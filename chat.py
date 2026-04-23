# chat.py
from db import fetch_chat_history, save_message, init_db
from intent import detect_intent_code, generate_answer, generate_question,generate_rag_answer
from prompts import INITIAL_GREETING

# 确保数据库已初始化
init_db()


def SeaChatInterview(phone_number: str, query: str) -> str:
    # 1. 获取该用户的历史对话
    history = fetch_chat_history(phone_number)

    # 2. 如果是新用户，返回欢迎语并存储
    if not history:
        # 存储初始化欢迎语和用户的第一条消息（注意：这里是模拟电话呼入场景，所以先存助手欢迎语，再存用户发的第一条）
        save_message(phone_number, "assistant", INITIAL_GREETING)
        save_message(phone_number, "user", query)
        # 实际场景中，欢迎语通常是外呼系统先播放的，然后再转接到 AI。这里简化处理，直接返回欢迎语。
        return INITIAL_GREETING

    # 3. 老用户：先保存当前用户消息
    save_message(phone_number, "user", query)

    # 4. 判断意图（注意：history 现在还不包含刚刚存入的用户消息，我们需要传给意图识别的是原始 query）
    intent_code = detect_intent_code(query)

    # 5. 根据意图生成回复
    if intent_code == 1:
        response = generate_rag_answer(history, query)
    else:
        # 注意：history 还是旧的历史，不包含本次用户消息。
        # 为让 generate_question 能看到最新对话，可以把本次用户消息临时加入。
        extended_history = history + [{"role": "user", "content": query}]
        response = generate_question(extended_history)

    # 6. 保存 AI 的回复到数据库
    save_message(phone_number, "assistant", response)

    return response