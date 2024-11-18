import requests
from bs4 import BeautifulSoup
import pandas as pd

# 設定新聞搜尋關鍵字和要爬取的數量
news_keyword = "crypto"
num_articles = 10

# 設定 User-Agent 模擬瀏覽器訪問
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 定義爬取 CoinTelegraph 新聞的函數
def fetch_cointelegraph_news(keyword, num_articles):
    url = f"https://cointelegraph.com/tags/{keyword}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"無法訪問網站，狀態碼: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article', class_='post-card')

    news_data = []
    for article in articles[:num_articles]:
        title = article.find('h2').get_text(strip=True)
        link = article.find('a')['href']
        summary = article.find('p').get_text(strip=True)
        
        full_article = requests.get(link, headers=headers)
        full_soup = BeautifulSoup(full_article.text, 'html.parser')
        content = full_soup.find('div', class_='post-content').get_text(strip=True)
        
        news_data.append({
            'title': title,
            'link': link,
            'summary': summary,
            'content': content
        })
        
        print(f"標題: {title}")
        print(f"連結: {link}")
        print(f"摘要: {summary}")
        print(f"完整內容: {content[:150]}...")  # 只顯示前150個字

    return news_data

# 爬取新聞並保存到 CSV
news_data = fetch_cointelegraph_news(news_keyword, num_articles)

if news_data:
    # 將數據保存到 CSV 文件
    df = pd.DataFrame(news_data)
    df.to_csv(f"cointelegraph_{news_keyword}_news.csv", index=False, encoding='utf-8-sig')
    print("新聞已保存到 CSV 文件。")
else:
    print("未能成功爬取新聞。")

# 這個方式一直被瀏覽器擋爬蟲
