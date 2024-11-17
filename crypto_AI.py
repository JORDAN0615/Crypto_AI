import os
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
app = Flask(__name__)

class CryptoAnalyzer:
    def __init__(self):
        self.cmc_api_key = os.getenv('CMC_API_KEY')
        openai_api_key = os.getenv('OPENAI_API_KEY1')

        # 設定 LLM 模型
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=1,
            openai_api_key=openai_api_key
        )

        self.base_url = 'https://pro-api.coinmarketcap.com/v1'

    def _get_headers(self):
        return {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.cmc_api_key,
        }

    def get_crypto_data(self, symbol: str):
        url = f'{self.base_url}/cryptocurrency/quotes/latest'
        params = {'symbol': symbol, 'convert': 'USD'}
        #參數帶入:網址+key+參數
        response = requests.get(url, headers=self._get_headers(), params=params) 
        if response.status_code == 200: 
            # 把response轉成json存到data
            data = response.json() 
            if symbol in data['data']:
                # 取出符合symbol的資料
                crypto = data['data'][symbol]
                # 取出USD的資料
                quote = crypto['quote']['USD']
                return {
                    'name': crypto['name'],
                    'symbol': crypto['symbol'],
                    'price': quote['price'],
                    'market_cap': quote['market_cap'],
                    'volume_24h': quote['volume_24h'],
                    'percent_change_24h': quote['percent_change_24h'],
                    'percent_change_7d': quote['percent_change_7d']
                }
        return None

    def get_latest_news(self, topic: str = "crypto") -> list:
        url = f'https://cointelegraph.com/tags/{topic}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        news_data = []
        articles = soup.find_all('article')[:5]  # 只爬取前5篇文章
        for article in articles:
            title = article.find('h2').text.strip() if article.find('h2') else "無標題"
            link = article.find('a')['href'] if article.find('a') else None
            news_content = self._fetch_article_content(link) if link else "無內容"
            
            news_data.append({
                'title': title,
                'content': news_content
            })

        # 在伺服器上打印新聞標題
        print("\n[Cointelegraph 最新新聞標題]:")
        for idx, news in enumerate(news_data, start=1):
            print(f"{idx}. {news['title']}")

        return news_data

    def _fetch_article_content(self, url: str) -> str:
        article_url = f'https://cointelegraph.com{url}'
        response = requests.get(article_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([para.text for para in paragraphs])
        return content

    def analyze_crypto(self, symbol: str):
        crypto_data = self.get_crypto_data(symbol)
        if not crypto_data:
            return {"error": "無法取得加密貨幣數據"}

        # 爬取最新新聞
        latest_news = self.get_latest_news()
        news_summary = "\n".join([f"標題: {news['title']}\n內容: {news['content']}" for news in latest_news])

        analysis_template = """
        分析以下加密貨幣數據和最新新聞並提供見解：
        
        幣種：{name} ({symbol})
        當前價格：${price:,.2f}
        24小時交易量：${volume_24h:,.2f}
        市值：${market_cap:,.2f}
        
        最新新聞：
        {news_summary}
        
        請提供：
        1. 技術分析概述
        2. 關鍵支撐位
        3. 關鍵壓力位
        4. 市場趨勢分析
        5. 利好消息
        6. 利空消息
        7. 交易建議
        8. 熱門新聞標題
        """
        
        prompt = ChatPromptTemplate.from_template(analysis_template)
        chain = prompt | self.llm

        analysis = chain.invoke({
            "name": crypto_data['name'],
            "symbol": crypto_data['symbol'],
            "price": crypto_data['price'],
            "volume_24h": crypto_data['volume_24h'],
            "market_cap": crypto_data['market_cap'],
            "news_summary": news_summary
        }).content

        return {
            "data": crypto_data,
            "news": latest_news,
            "analysis": analysis
        }


@app.route('/api/crypto/analyze/<symbol>', methods=['GET'])
def analyze_cryptocurrency(symbol):
    analyzer = CryptoAnalyzer()
    analysis = analyzer.analyze_crypto(symbol.upper())
    return jsonify(analysis)

if __name__ == '__main__':
    app.run(debug=True)

