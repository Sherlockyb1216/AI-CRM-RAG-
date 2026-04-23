import sqlite3
from typing import List, Dict, Optional

DB_PATH = "conversations.db"


def init_db() -> None:
    """初始化数据库，创建表和索引（如不存在）"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user','assistant')),
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_phone ON conversations(phone_number);")
        conn.commit()


def fetch_chat_history(phone_number: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
    """
    获取指定手机号的对话历史，按时间正序排列。
    返回列表，每个元素为字典：{"role": "user"/"assistant", "content": "..."}
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row  # 让查询结果支持字典访问
        query = """
            SELECT role, content FROM conversations
            WHERE phone_number = ?
            ORDER BY timestamp ASC
        """
        if limit:
            query += f" LIMIT {limit}"
        cursor = conn.execute(query, (phone_number,))
        rows = cursor.fetchall()
        return [{"role": row["role"], "content": row["content"]} for row in rows]


def save_message(phone_number: str, role: str, content: str) -> None:
    """保存一条对话记录"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO conversations (phone_number, role, content) VALUES (?, ?, ?)",
            (phone_number, role, content)
        )
        conn.commit()


def clear_history(phone_number: str) -> None:
    """清空指定用户的聊天历史（可用于重置或测试）"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM conversations WHERE phone_number = ?", (phone_number,))
        conn.commit()


# 测试代码（可选）
if __name__ == "__main__":
    init_db()
    # 模拟存入一条消息
    save_message("13800138000", "user", "你好，我想咨询产品价格")
    save_message("13800138000", "assistant", "您好，请问您对哪款产品感兴趣？")
    history = fetch_chat_history("13800138000")
    print(history)