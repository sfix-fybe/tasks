# Selenium BizMap アクセスツール

このツールは、Seleniumを使用して指定されたBizMapのURLにアクセスし、全てのページのHTMLを取得するためのものです。

## 必要条件

- Python 3.6以上
- Google Chrome ブラウザ
- ChromeDriver（Seleniumの最新バージョンでは自動的にインストールされます）

## セットアップ

1. 必要なパッケージをインストールします：

```bash
pip install -r requirements.txt
```

2. Google Chromeがインストールされていることを確認してください。

## 使用方法

以下のコマンドを実行して、指定されたBizMapのURLにアクセスし、全てのページのHTMLを取得します：

```bash
python selenium_bizmap.py
```

## 機能

- 指定されたBizMapのURLにアクセスします
- 最初に10秒待機します
- 各ページのHTMLを取得して保存します（bizmap_html/page_1.html, page_2.html, ...）
- 「次へ」ボタンがなくなるまで、1秒ごとにクリックして次のページに移動します
- 全てのページを取得したら、ブラウザを閉じます

## 出力ファイル

全てのファイルは `bizmap_html` ディレクトリに保存されます：

- `page_1.html`, `page_2.html`, ... - 各ページのHTML

## カスタマイズ

- ヘッドレスモードを有効にするには、コード内の`chrome_options.add_argument("--headless")`のコメントを解除します
- 待機時間やその他のパラメータは、必要に応じてコード内で調整できます