import os
import numpy as np
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = "BAAI/bge-small-zh-v1.5"
INDEX_DIR = "./faiss_index"

# 全局加载模型
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# 用于存储文档文本的列表（与向量索引的 id 对应）
documents_store = []


def build_faiss_index(docs):
    """构建索引：向量化所有文档并存入 FAISS"""
    global documents_store
    texts = [doc["text"] for doc in docs]
    vectors = embedding_model.encode(texts).astype('float32')

    import faiss
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)  # L2 距离
    index.add(vectors)

    # 保存向量索引到磁盘
    faiss.write_index(index, INDEX_DIR)
    # 保存原始文档（为简单，用 numpy 或 pickle）
    np.save(INDEX_DIR + "_texts.npy", np.array(texts))
    print(f"FAISS 索引建立完成，共 {len(docs)} 个文档块。")


def load_faiss_index():
    """加载索引和文本库"""
    import faiss
    global documents_store
    if os.path.exists(INDEX_DIR):
        index = faiss.read_index(INDEX_DIR)
        documents_store = list(np.load(INDEX_DIR + "_texts.npy", allow_pickle=True))
        print(f"已加载 FAISS 索引，包含 {len(documents_store)} 个文档块。")
        return index, True
    else:
        print("FAISS 索引文件不存在，请先运行 build_index.py 建立索引。")
        return None, False


def retrieve_context(query, n_results=3):
    """检索与查询最相似的文本块"""
    import faiss
    index, loaded = load_faiss_index()
    if not loaded:
        return ""

    query_vec = embedding_model.encode([query]).astype('float32')
    distances, indices = index.search(query_vec, n_results)

    retrieved = [documents_store[i] for i in indices[0] if i < len(documents_store)]
    return "\n\n---\n\n".join(retrieved)


def index_documents(docs):
    """供 build_index.py 调用的接口"""
    build_faiss_index(docs)


# 初始化时尝试加载已有索引（若存在），以便 Flask 启动时可用
load_faiss_index()