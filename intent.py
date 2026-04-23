from openai import OpenAI
import config
from prompts import INTENT_CLASSIFICATION_PROMPT
from knowledge import retrieve_context
from prompts import ANSWER_WITH_CONTEXT_PROMPT

client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_BASE_URL)


def detect_intent_code(user_query: str) -> int:
    """
    调用大模型判断用户输入的意图类别。
    返回 1（回答）或 2（提问）。异常时默认为 2（进入访谈模式）。
    """
    prompt = INTENT_CLASSIFICATION_PROMPT.format(user_query=user_query)

    try:
        response = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,   # 分类任务要求结果稳定，设为 0
            max_tokens=5       # 只需要一个数字
        )
        content = response.choices[0].message.content.strip()
        # 提取第一个数字字符
        for char in content:
            if char in "12":
                return int(char)
        return 2  # 未识别到有效数字时默认进入访谈模式
    except Exception as e:
        print(f"意图识别失败: {e}")
        return 2  # 异常时默认为访谈模式，保证对话可继续

def generate_answer(chat_history: list, user_query: str) -> str:
    """
    基于历史对话和用户问题生成回答。
    chat_history 格式: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
    """
    from prompts import ANSWER_SYSTEM_PROMPT

    messages = [{"role": "system", "content": ANSWER_SYSTEM_PROMPT}]
    messages.extend(chat_history)  # 历史对话（已包含 user 和 assistant）
    messages.append({"role": "user", "content": user_query})

    try:
        response = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=messages,
            temperature=0.7,     # 回答模式可适当提高创造性
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"生成回答失败: {e}")
        return "抱歉，我暂时无法回答您的问题，请稍后再试。"

def generate_question(chat_history: list) -> str:
    """
    基于历史对话生成下一段访谈内容（主动提问）。
    """
    from prompts import INTERVIEW_PROMPT

    # 将历史对话格式化为可读文本
    history_text = ""
    for msg in chat_history:
        role = "用户" if msg["role"] == "user" else "助手"
        history_text += f"{role}: {msg['content']}\n"

    prompt = INTERVIEW_PROMPT.format(history_text=history_text)

    try:
        response = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,     # 访谈模式可更具变化性
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"生成提问失败: {e}")
        return "感谢您的分享。请问还有其他方面您想聊聊吗？"



def generate_rag_answer(chat_history, user_query):
    """使用RAG模式生成回答"""
    # 步骤1: 去知识库里“翻资料”
    context = retrieve_context(user_query)

    # 步骤2: 整理聊天历史
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])

    # 步骤3: 打包提问
    prompt = ANSWER_WITH_CONTEXT_PROMPT.format(
        context=context,
        history_text=history_text,
        user_query=user_query
    )

    # 步骤4: 请AI基于资料回答（这里面不超时、不做容错处理）
    try:
        response = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"RAG模式生成回答失败: {e}")
        return "抱歉，我暂时无法访问我的知识库来回答您的问题。"