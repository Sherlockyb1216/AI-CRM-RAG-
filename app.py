# app.py
import json
from flask import Flask, request, Response, stream_with_context
from chat import SeaChatInterview
from db import init_db

# 初始化数据库（如果尚未初始化）
init_db()

app = Flask(__name__)


@app.route('/chat', methods=['POST'])
def chat_api():
    """处理聊天请求的 API 端点"""
    # 1. 解析请求体
    try:
        data = request.get_json(force=True)
    except Exception:
        return Response(
            json.dumps({"error": "Invalid JSON"}),
            status=400,
            mimetype='application/json'
        )

    # 2. 验证必需字段
    phone_number = data.get('phone_number')
    query = data.get('query')

    if not phone_number or not query:
        return Response(
            json.dumps({"error": "Missing phone_number or query"}),
            status=400,
            mimetype='application/json'
        )

    # 3. 定义流式生成器，调用主函数并逐块输出
    def generate():
        """流式生成器，逐字符输出响应（模拟打字机效果）"""
        response_text = SeaChatInterview(phone_number, query)
        for char in response_text:
            yield char

    # 4. 返回流式响应
    return Response(
        stream_with_context(generate()),
        mimetype='text/plain; charset=utf-8'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)