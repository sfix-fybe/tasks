import csv

def add_inquiry_url_column():
    # CSVファイルのパス
    csv_file = 'bizmap_companies.csv'
    
    # CSVファイルを読み込む
    rows = []
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  # ヘッダー行を取得
        rows.append(header)
        
        # 残りの行を読み込む
        for row in reader:
            rows.append(row)
    
    # 新しいヘッダーと行を作成
    new_rows = []
    
    # ヘッダーに「問い合わせフォームURL」を追加
    new_header = header + ['問い合わせフォームURL']
    new_rows.append(new_header)
    
    # 各行に「null」を追加
    for row in rows[1:]:  # ヘッダー行をスキップ
        new_row = row + ['null']
        new_rows.append(new_row)
    
    # 更新したデータをCSVファイルに書き戻す
    with open(csv_file, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(new_rows)
    
    print(f"'{csv_file}'に「問い合わせフォームURL」列を追加しました。")

if __name__ == "__main__":
    add_inquiry_url_column()