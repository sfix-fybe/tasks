import os
import pandas as pd
from openai import OpenAI
import time
import re
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAI APIの設定
# 環境変数からAPIキーを取得
api_key = os.environ.get("OPENAPI_API_KEY")
if not api_key:
    print("警告: .envファイルにOPENROUTER_API_KEYが設定されていません。")
    print("APIキーを.envファイルに設定してください。")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

def find_inquiry_form_with_perplexity(company_name):
    """
    Perplexityを使用して企業の問い合わせフォームURLを取得する
    """
    # APIキーが設定されていない場合はNoneを返す
    if not api_key:
        print("  APIキーが設定されていないため、Perplexityを使用できません")
        return None
        
    prompt = f"""
    あなたは企業の問い合わせフォームURLを見つけるアシスタントです。
    
    以下の企業の問い合わせフォームURLを見つけてください：
    
    企業名: {company_name}
    
    問い合わせフォームURLのみを返してください。URLだけを返してください。
    問い合わせフォームが見つからない場合は「見つかりません」と回答してください。
    
    回答例：
    https://example.com/contact
    
    または
    
    見つかりません
    """
    
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://example.com",
                "X-Title": "Inquiry Form Extractor",
            },
            model="perplexity/sonar-pro",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        response = completion.choices[0].message.content.strip()
        
        # レスポンスから問い合わせフォームURLを抽出
        if "見つかりません" in response or "not found" in response.lower() or "見つかりませんでした" in response:
            return None
        
        # URLを抽出
        urls = re.findall(r'https?://[^\s"\'<>]+', response)
        if urls:
            return urls[0]  # 最初のURLを返す
        
        return None
    
    except Exception as e:
        print(f"  Perplexityでのエラー: {e}")
        return None

def resume_inquiry_extraction(start_index=0):
    """
    指定したインデックスから問い合わせフォームURLの抽出を再開する
    
    Args:
        start_index: 処理を開始するインデックス（0から始まる）
    """
    # CSVファイルのパス
    input_csv = 'bizmap_companies.csv'
    output_csv = 'bizmap_companies_with_inquiry.csv'
    
    # CSVファイルを読み込む
    df = pd.read_csv(input_csv)
    
    # 処理する企業の総数
    total_companies = len(df)
    print(f"合計 {total_companies} 社の企業があります")
    print(f"インデックス {start_index} から処理を開始します")
    
    # 問い合わせフォームURLが既に存在するか確認
    if '問い合わせフォームURL' not in df.columns:
        # 明示的に文字列型（object）として初期化
        df['問い合わせフォームURL'] = pd.Series(dtype='object')
    else:
        # 既存の列を文字列型に変換
        df['問い合わせフォームURL'] = df['問い合わせフォームURL'].astype('object')
    
    # 既存の出力ファイルがあれば読み込む
    if os.path.exists(output_csv):
        print(f"既存の出力ファイル {output_csv} を読み込みます")
        existing_df = pd.read_csv(output_csv)
        
        # 既存のデータで問い合わせフォームURLが設定されている行を更新
        for idx, row in existing_df.iterrows():
            if pd.notna(row.get('問い合わせフォームURL')):
                df.at[idx, '問い合わせフォームURL'] = row['問い合わせフォームURL']
    
    # 各企業の問い合わせフォームURLを取得
    for index, row in df.iloc[start_index:].iterrows():
        company_name = row['会社名']
        
        print(f"処理中 ({index + 1}/{total_companies}): {company_name}")
        
        # 既に問い合わせフォームURLが設定されている場合はスキップ
        if pd.notna(df.at[index, '問い合わせフォームURL']):
            print(f"  既に問い合わせフォームURLが設定されています: {df.at[index, '問い合わせフォームURL']}")
            continue

        try:
            # Perplexityを使用して問い合わせフォームURLを取得
            inquiry_url = find_inquiry_form_with_perplexity(company_name)
            
            if inquiry_url:
                print(f"  問い合わせフォームURL発見: {inquiry_url}")
            else:
                print("  問い合わせフォームURLが見つかりませんでした")
            
            # 問い合わせフォームURLをDataFrameに追加
            df.at[index, '問い合わせフォームURL'] = inquiry_url
            
            # APIレート制限を避けるために少し待機
            time.sleep(1)
            
            # 定期的に結果を保存（5社ごと）
            if (index + 1) % 5 == 0 or index == total_companies - 1:
                df.to_csv(output_csv, index=False, encoding='utf-8-sig')
                print(f"  中間結果を保存しました: {index + 1}/{total_companies}")
            
        except Exception as e:
            print(f"  エラー: {company_name} - {e}")
            # エラーが発生した場合も結果を保存
            df.to_csv(output_csv, index=False, encoding='utf-8-sig')
            print(f"  エラー発生時点での結果を保存しました: {index + 1}/{total_companies}")
            continue
    
    # 結果をCSVファイルに保存
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\n処理完了！ 結果を {output_csv} に保存しました。")

if __name__ == "__main__":
    # コマンドライン引数から開始インデックスを取得
    import sys
    start_idx = 0
    
    if len(sys.argv) > 1:
        try:
            start_idx = int(sys.argv[1])
        except ValueError:
            print("警告: 開始インデックスは整数で指定してください。デフォルトの0を使用します。")
    
    resume_inquiry_extraction(start_idx)