# build_index.py
from knowledge import index_documents
import os


def main():
    # 假设你的产品文档叫 product_faq.txt
    doc_file = "product_faq.txt"
    if not os.path.exists(doc_file):
        print(f"错误：找不到文件 '{doc_file}'")
        return

    with open(doc_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 进行简单的按段落分块（更优雅的方式后续可以迭代）
    chunks = [{"text": chunk.strip()} for chunk in content.split('\n\n') if chunk.strip()]
    index_documents(chunks)
    print(f"知识库建立完成，共索引 {len(chunks)} 个文档块。")


if __name__ == "__main__":
    main()