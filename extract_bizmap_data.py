import os
import re
import pandas as pd
from bs4 import BeautifulSoup

def extract_company_data(html_content):
    """HTMLコンテンツから企業データを抽出する関数"""
    soup = BeautifulSoup(html_content, 'html.parser')
    companies = []
    
    # 企業リストの各アイテムを取得
    items = soup.select('li.results__item')
    
    for item in items:
        company = {}
        
        # 会社名
        name_elem = item.select_one('.results__name')
        if name_elem:
            company['会社名'] = name_elem.text.strip()
        
        # キーマン人数
        keyman_elem = item.select_one('.results_keyman_number--num')
        if keyman_elem:
            company['キーマン人数'] = keyman_elem.text.strip()
        
        # 事業内容
        description_elem = item.select_one('.results__text p')
        if description_elem:
            company['事業内容'] = description_elem.text.strip()
        
        # 企業URL
        url_elem = item.select_one('a')
        if url_elem and 'href' in url_elem.attrs:
            company['企業URL'] = 'https://biz-maps.com' + url_elem['href']
        
        # テーブルデータの抽出
        table_rows = item.select('.results__table tr')
        for row in table_rows:
            header = row.select_one('.results__table--ttl')
            value = row.select_one('.results__table--txt')
            
            if header and value:
                header_text = header.text.strip()
                
                # 画像が含まれている場合（ぼかされているデータ）はスキップ
                if value.select_one('img'):
                    continue
                
                value_text = value.text.strip()
                
                if header_text == '業種':
                    company['業種'] = value_text
                elif header_text == '住所':
                    company['住所'] = re.sub(r'\s+', ' ', value_text).strip()
                elif header_text == '設立年度':
                    company['設立年度'] = value_text
                elif header_text == '代表者名':
                    company['代表者名'] = value_text
                elif header_text == '資本金等':
                    company['資本金等'] = value_text
                elif header_text == 'オリジナルタグ':
                    tag_elem = value.select_one('.results__table--TagTxt')
                    if tag_elem:
                        company['オリジナルタグ'] = tag_elem.text.strip()
        
        companies.append(company)
    
    return companies

def main():
    """メイン関数"""
    all_companies = []
    html_dir = "bizmap_html"
    
    # HTMLファイルを処理
    for filename in sorted(os.listdir(html_dir)):
        if filename.endswith('.html'):
            file_path = os.path.join(html_dir, filename)
            print(f"処理中: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 企業データを抽出
            companies = extract_company_data(html_content)
            all_companies.extend(companies)
    
    # 重複を削除（会社名をキーとして）
    unique_companies = {}
    for company in all_companies:
        if '会社名' in company:
            unique_companies[company['会社名']] = company
    
    # DataFrameに変換
    df = pd.DataFrame(list(unique_companies.values()))
    
    # カラムの順序を設定
    columns = [
        '会社名', 'キーマン人数', '事業内容', '業種', '住所', 
        '設立年度', '代表者名', '資本金等', 'オリジナルタグ', '企業URL'
    ]
    
    # 存在するカラムのみを使用
    existing_columns = [col for col in columns if col in df.columns]
    df = df[existing_columns]
    
    # CSVファイルに保存
    csv_path = "bizmap_companies.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')  # BOMありUTF-8でExcelでも文字化けしないように
    
    print(f"\n処理完了！ {len(df)} 件の企業データを {csv_path} に保存しました。")

if __name__ == "__main__":
    main()