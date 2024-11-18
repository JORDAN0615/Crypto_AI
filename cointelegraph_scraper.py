from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import pandas as pd

# 設定 Firefox 無頭模式
options = Options()
options.add_argument('--headless')  # 無頭模式（不顯示瀏覽器）

# 設定 GeckoDriver 的路徑
gecko_path = "C:/Users/user\Downloads/geckodriver-v0.35.0-win32/geckodriver.exe"  # 根據您實際安裝的路徑調整

# 創建 GeckoDriver 服務
service = Service(executable_path=gecko_path)

# 初始化 WebDriver
driver = webdriver.Firefox(service=service, options=options)

# 設定新聞關鍵字和爬取數量
news_keyword = "crypto"
num_articles = 10

# 訪問 CoinTelegraph
url = f"https://cointelegraph.com/tags/{news_keyword}"
driver.get(url)

# 等待頁面加載
time.sleep(5)

# 爬取標題和內容
articles = driver.find_elements(By.CLASS_NAME, 'post-card')

news_data = []
for article in articles[:num_articles]:
    title = article.find_element(By.TAG_NAME, 'h2').text
    link = article.find_element(By.TAG_NAME, 'a').get_attribute('href')
    summary = article.find_element(By.TAG_NAME, 'p').text
    
    # 訪問每篇新聞的詳細頁面
    driver.get(link)
    time.sleep(3)  # 等待頁面加載
    content = driver.find_element(By.CLASS_NAME, 'post-content').text
    
    news_data.append({
        'title': title,
        'link': link,
        'summary': summary,
        'content': content
    })

# 關閉瀏覽器
driver.quit()

# 保存新聞數據到 CSV 文件
if news_data:
    df = pd.DataFrame(news_data)
    df.to_csv(f"cointelegraph_{news_keyword}_news.csv", index=False, encoding='utf-8-sig')
    print("新聞已保存到 CSV 文件。")
else:
    print("未能成功爬取新聞。")


# 卡在讀不到firefox瀏覽器