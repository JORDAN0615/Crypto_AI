import os
import json
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings

def add_news_to_vectorstore(file_path: str, vectorstore_path: str, openai_api_key: str):
    # 初始化 OpenAI 嵌入模型
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=openai_api_key)

    # 從 JSON 文件中讀取新聞
    with open(file_path, "r", encoding="utf-8") as file:
        news_data = json.load(file)

    # 批量處理新聞
    contents = [news["內容"] for news in news_data]
    metadata = [{"title": news["標題"], "url": news["網址"]} for news in news_data]

    # 初始化 FAISS 向量資料庫
    if os.path.exists(vectorstore_path):
        # 加載現有的向量資料庫
        vectorstore = FAISS.load_local(vectorstore_path, embedding_model, allow_dangerous_deserialization=True)
        # 一次性添加所有新聞到現有資料庫
        vectorstore.add_texts(contents, metadata)
    else:
        # 如果不存在，直接從文本創建新的向量資料庫
        vectorstore = FAISS.from_texts(contents, embedding_model, metadatas=metadata)

    # 保存向量資料庫
    vectorstore.save_local(vectorstore_path)
    print(f"新聞已成功添加到向量資料庫，儲存於：{vectorstore_path}")
    
file_path = "cointelegraph_news.json"  
vectorstore_path = "crypto_vectorstore"  # 向量資料庫儲存路徑
openai_api_key = os.getenv('OPENAI_API_KEY1')

add_news_to_vectorstore(file_path, vectorstore_path, openai_api_key)