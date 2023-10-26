import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import requests

# ウェブドライバーの設定
#chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument("--headless")
driver = webdriver.Chrome()

# グルナビの一覧ページのURLを指定
mainurl = "https://r.gnavi.co.jp/area/jp/motunabe/rs/"

#保存データのリストを作成
data = {
    '店舗名': [],
    '電話番号': [],
    '都道府県': [],
    '市区町村': [],
    '番地': [],
    '建物名': [],
    'URL':[],
    'SSL': []
    }
df = pd.DataFrame(data)

# タイムアウト時間を設定（秒）
timeout_duration = 6

def check_ssl(link):
    try:
        response = requests.head(link)
        ssl_enabled = response.url.startswith("https")
        if ssl_enabled == True:
            return "True"
        else:
            return "False"
    except Exception:
        return False



page = 1
items = 1
# 各店舗の情報を取得
while items < 51:
    url=mainurl + '?p=' + str(page)
    driver.get(url)

    link_elements = driver.find_elements(By.CLASS_NAME, "style_titleLink__oiHVJ")
    link_text_list = [link.get_attribute('href') for link in link_elements]

    for link in link_text_list:
        driver.set_page_load_timeout(timeout_duration)
        try:
            driver.get(link)
            is_ssl_enabled = check_ssl(link)
            name = driver.find_element(By.ID, "info-name").text
            phone = driver.find_element(By.CLASS_NAME, "number").text
            address = driver.find_element(By.CLASS_NAME, "region").text
            try:
                building = driver.find_element(By.CLASS_NAME, 'locality').text #建物名が格納されている'locality'タグがあるとき
            except NoSuchElementException:
                building = ""

            # 都道府県、市区町村、番地の正規表現パターン
            pattern = r"([^\x01-\x7E]+?[都道府県])([^0-9]+?)([0-9０-９]+[-－][0-9０-９]+)"

            matches = re.search(pattern, address)
            if matches:
                prefecture = matches.group(1)
                city = matches.group(2)
                street = matches.group(3)
            else:
                prefecture = address
                city = ""
                street = ""

            # データを辞書に格納
            new_data = {
                '店舗名': name,
                '電話番号': phone,
                '都道府県': prefecture,
                '市区町村': city,
                '番地': street,
                '建物名': building,
                'URL':link,
                'SSL': is_ssl_enabled

            }

            data_list = [new_data]

            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            items += 1

        except Exception:
            pass

        if items > 50:
            break
    page += 1
        

# ブラウザを閉じる
driver.quit()

# CSVファイルにデータフレームを保存
df.to_csv('1-2.csv', index=False)