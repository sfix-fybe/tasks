import os
import pandas as pd
from openai import OpenAI
import time
import re
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAI APIの設定
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("警告: .envファイルにOPENAI_API_KEYが設定されていません。")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

def find_inquiry_form_with_perplexity(company_name):
    if not api_key:
        print("  APIキーが設定されていないため、Perplexityを使用できません")
        return None

    prompt = f"""
    あなたは企業の問い合わせフォームURLを見つけるントです。

    以下の企業の問い合わせフォームとしてのURLを見つけてください：

    企業名: {company_name}

    問い合わせフォームURLのみを返してください。URLだけください。
    問い合わせフォームが見つからない場合は「見つかりません」と回答してください。
    """

    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://example.com",
                "X-Title": "Inquiry Form Extractor",
            },
            model="perplexity/sonar-pro",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        response = completion.choices[0].message.content.strip()

        if "見つかりません" in response or "not found" in response.lower():
            return None

        urls = re.findall(r'https?://[^\s"\'<>]+', response)
        return urls[0] if urls else None

    except Exception as e:
        print(f"  エラー（{company_name}）: {e}")
        return None

def process_company(index, company_name):
    print(f"処理中 ({index + 1}): {company_name}")
    url = find_inquiry_form_with_perplexity(company_name)
    if url:
        print(f"  問い合わせURL発見: {url}")
    else:
        print("  問い合わせフォームURLが見せんでした")
    return index, url

def extract_inquiry_urls_parallel():
    # 入力と出力を同じファイルにする
    csv_path = 'ワーカーメール管理シート - 3_27.csv'

    # 読み込み（再開に対応）
    df = pd.read_csv(csv_path)

    # 列名の誤字修正もここで対応（※元のコードでは "問い合ームURL" になってました）
    if '問い合わせフォームURL' not in df.columns:
        df['問い合わせフォームURL'] = pd.Series(dtype='object')

    total_companies = len(df)
    print(f"合計 {total_companies} 社の企業を処理します")

    max_workers = 5
    futures = []

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for idx, row in df.iterrows():
                # スキップ条件（すでにURLあり）
                if pd.notna(row.get('問い合わせフォームURL')):
                    print(f"スキップ済み: {row['会社名']}")
                    continue

                future = executor.submit(process_company, idx, row['会社名'])
                futures.append(future)

            counter = 0
            for future in as_completed(futures):
                idx, url = future.result()
                df.at[idx, '問い合わせフォームURL'] = url
                counter += 1

                # 定期保存（同じファイルに上書き）
                if counter % 5 == 0:
                    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                    print(f"  中間保存しました: {counter} 件処理済み")

    except Exception as e:
        print(f"\n予期せぬエラーが発生しました: {e}")
    finally:
        # 最終保存（上書き）
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"\n処理完了（または中断）: 結果を {csv_path} に保存しました。")



if __name__ == "__main__":
    extract_inquiry_urls_parallel()
