import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.tools import tool

# ===== 千问 embedding 模型（走 DashScope OpenAI 兼容接口） =====
# check_embedding_ctx_length=False：关闭 tiktoken 预切分，
# 否则 text-embedding-v3 会被 tiktoken 切成 token ID 发给接口导致报错
embeddings = OpenAIEmbeddings(
    model="text-embedding-v3",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    dimensions=1024,
    check_embedding_ctx_length=False,
)

# ===== Chroma 持久化向量库 =====
# 入库脚本和检索必须用同一个 collection_name + persist_directory，才能读到数据
vector_store = Chroma(
    collection_name="customer_service_faq",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)

@tool
def search_knowledge(query: str, k: int = 3):
    """检索客服知识库（售后政策、包邮、退货、退款、发货规则等）。query：用户的问题"""
    docs = vector_store.similarity_search(query, k=k)
    if not docs:
        return "知识库中没有找到相关内容"
    return "\n\n".join(doc.page_content for doc in docs)
