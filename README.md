```markdown
# AI CRM 智能访谈机器人（RAG 增强版）

基于大模型的 AI 客服访谈系统，支持自动欢迎、意图识别、多轮对话，并可通过检索私有知识库精准回答业务问题。

---

## ✨ 核心功能

- **新客欢迎**：新用户接入自动播放欢迎语，开启访谈流程。
- **意图识别**：自动判断用户是想“提问”（进入访谈模式）还是“回答”（查询知识库）。
- **知识库检索 (RAG)**：将企业产品手册、FAQ 等文档向量化，精准回答业务问题，杜绝“胡编乱造”。
- **对话记忆**：基于手机号持久化存储所有聊天记录，保持多轮对话连贯。
- **流式接口**：提供 HTTP SSE 流式 API，打字机效果返回，提升前端体验。

---

## 🧱 技术栈

| 模块 | 选型 |
|------|------|
| 大语言模型 | DeepSeek (兼容 OpenAI SDK) |
| 嵌入模型 | BAAI/bge-small-zh-v1.5 (本地运行) |
| 向量数据库 | FAISS (纯 Python，零编译) |
| 对话存储 | SQLite |
| API 框架 | Flask |
| 包管理器 | uv |

---

## 📂 项目结构

```

ai_crm/
├── .env                    # 密钥配置（勿提交）
├── pyproject.toml         # 依赖声明
├── uv.lock
├── app.py                # Flask API 服务
├── config.py             # 全局配置
├── db.py                 # SQLite 操作
├── prompts.py            # 提示词模板
├── intent.py             # 意图识别 + 回答生成
├── chat.py               # 核心对话逻辑 SeaChatInterview
├── knowledge.py          # FAISS 向量库操作
├── build_index.py        # 知识库索引构建脚本
├── product_faq.txt       # 示例产品文档
├── faiss_index           # 向量索引文件（自动生成）
├── faiss_index_texts.npy # 原始文本备份（自动生成）
└── conversations.db      # 聊天记录数据库

```

---

## ⚙️ 快速开始

### 1. 环境准备

确保已安装 Python 3.10+ 和 [uv](https://github.com/astral-sh/uv)。

```bash
# 克隆/进入项目目录
cd ai_crm

# 初始化并安装依赖
uv init
uv add flask openai python-dotenv sentence-transformers faiss-cpu
```

2. 配置密钥

创建 .env 文件，填入你的 DeepSeek API Key：

```
OPENAI_API_KEY=sk-your-deepseek-key
OPENAI_BASE_URL=https://api.deepseek.com

# 国内网络可添加镜像（非必须）
HF_ENDPOINT=https://hf-mirror.com
```

3. 构建知识库

准备你的产品文档 product_faq.txt（段落间用空行分隔），运行：

```bash
python build_index.py
```

首次运行会自动下载嵌入模型（约 100MB），请耐心等待。输出 FAISS 索引建立完成 即表示成功。

4. 启动服务

```bash
python app.py
```

看到终端输出 Debugger is active! 即启动成功，监听 http://127.0.0.1:5000。

5. 测试接口

重要: 测试 RAG 功能时必须用同一个手机号分至少两次请求，否则永远只会返回欢迎语。

```bash
# 第一次请求 – 新用户，返回欢迎语
python -c "import requests; r = requests.post('http://127.0.0.1:5000/chat', json={'phone_number':'13800001111','query':'你好'}); print(r.text)"

# 第二次请求 – 同一手机号，触发 RAG 检索
python -c "import requests; r = requests.post('http://127.0.0.1:5000/chat', json={'phone_number':'13800001111','query':'你们支持七天无理由退货吗'}); print(r.text)"
```

预期输出：

根据我们的退换货政策，线上购买的 SaaS 标准版支持 7 天内无理由全额退款…

---

🧩 模块详解

文件 职责
chat.py 核心调度：查历史→新/老用户→意图分类→回答/追问→存记录→返回
intent.py 调用大模型判断意图（1-回答，2-提问），并生成具体回复（含 RAG 模式）
knowledge.py FAISS 索引的创建、加载、检索，文本嵌入由 sentence-transformers 完成
db.py 聊天记录的增删查，手机号+角色+内容+时间戳
prompts.py 所有系统提示词：意图分类、访谈提问、标准回答、带知识库回答等
build_index.py 离线工具，读取 product_faq.txt → 分块 → 向量化 → 存入 FAISS

---

⚠️ 注意事项

1. 手机号连续性：系统依赖手机号区分用户，测试 RAG 时务必保持号码一致，否则会被视为新用户。
2. 知识库更新：修改文档后，请删除 faiss_index 和 faiss_index_texts.npy 再重新运行 build_index.py，避免数据重复。
3. Flask 重载：Debug 模式下任何 .py 文件改动都会导致服务重启，期间请求会失败。请等待终端出现 Debugger is active! 后再发请求。
4. 网络问题：若嵌入模型下载缓慢，可设置环境变量 HF_ENDPOINT=https://hf-mirror.com（国内镜像）。
5. 生产部署：请勿直接使用 Flask 开发服务器，可换用 waitress (Windows) 或 gunicorn (Linux)。
6. 安全：.env 和 conversations.db 等敏感文件务必加入 .gitignore。

---

🔧 常见问题

现象 原因 解决
访问 http://127.0.0.1:5000 显示 404 项目未定义 / 路由，这是正常的 请求 /chat 即可
永远只回复欢迎语 每次测试都换了手机号 用同一号码连续请求两次以上
请求时连接被拒绝 Flask 正在重载或未启动 等 Debugger is active! 出现后再试
知识库检索出错 旧版 Chroma 兼容问题（已弃用） 本项目已切换至 FAISS，无需处理
RAG 回答不精确 知识库分段过大或问题不在文档中 优化 product_faq.txt，确保每段语义独立

---

📦 依赖清单

```
flask
openai
python-dotenv
sentence-transformers
faiss-cpu
```

以上依赖由 pyproject.toml 统一管理，可通过 uv sync 一键安装。

---

📝 自定义提示词

所有对话风格、访谈话术、回答逻辑均由 prompts.py 中的模板控制，可直接编辑该文件调整机器人的行为。

---

🚀 后续可扩展方向

· 混合检索 (BM25 + 向量) 提升召回率
· 多轮对话状态管理
· 对话历史 Token 自动截断
· 接入语音外呼 / 企业微信消息推送
· 使用 gunicorn + Docker 生产化部署

---

项目状态：✅ 已完成全部核心功能，可直接用于原型演示或二次开发。

```

现在可以将以上内容保存为 `README.md`，放置在项目根目录。