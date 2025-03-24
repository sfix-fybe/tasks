from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import os

def access_bizmap():
    # 保存先ディレクトリの作成
    html_dir = "bizmap_html"
    if not os.path.exists(html_dir):
        os.makedirs(html_dir)
        print(f"ディレクトリを作成しました: {html_dir}")
    
    # Chromeオプションの設定
    chrome_options = Options()
    # ヘッドレスモードを無効にする（ブラウザを表示する）
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # WebDriverの初期化
    # ChromeDriverのパスを指定する必要がある場合は以下のようにServiceを使用
    # service = Service('/path/to/chromedriver')
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 多くの場合、最新のSeleniumではドライバーを自動的に検出
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 指定されたURLにアクセス
        url = "https://biz-maps.com/s/prefs/13/m-inds/162,197,237,481,485,546,573,651"
        print(f"アクセス中: {url}")
        driver.get(url)
        
        # ページが完全に読み込まれるまで待機（最大10秒）
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print("最初に10秒待機します...")
        time.sleep(20)  # 最初に10秒待機
        
        # ページ番号の初期化
        page_num = 1
        has_next_page = True
        
        while has_next_page:
            # 現在のページのHTMLを取得して保存
            html_content = driver.page_source
            html_file = os.path.join(html_dir, f"page_{page_num}.html")
            
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print(f"ページ {page_num} のHTMLを保存しました: {html_file}")
            
            # 「次へ」ボタンを探す
            try:
                # 「次へ」ボタンを探す（rel="next" と class="page-link" を持つ <a> タグ）
                next_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.page-link[rel='next']"))
                )
                
                print(f"「次へ」ボタンを発見しました。ページ {page_num + 1} に移動します...")
                next_button.click()
                
                # 1秒待機
                time.sleep(1)
                
                # 新しいページが読み込まれるのを待機
                WebDriverWait(driver, 10).until(
                    EC.staleness_of(next_button)
                )
                
                # ページが完全に読み込まれるまで待機
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # ページ番号をインクリメント
                page_num += 1
                
            except (NoSuchElementException, TimeoutException):
                # 「次へ」ボタンが見つからない場合、ループを終了
                print("「次へ」ボタンが見つかりません。全てのページを取得しました。")
                has_next_page = False
        
        print(f"合計 {page_num} ページのHTMLを取得しました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    
    finally:
        # ブラウザを閉じる
        print("ブラウザを閉じています...")
        driver.quit()

if __name__ == "__main__":
    access_bizmap()