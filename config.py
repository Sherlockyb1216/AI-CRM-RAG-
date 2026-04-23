import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

if not OPENAI_API_KEY:
    raise ValueError("请在.env中设置环境变量")