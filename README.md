# 技術論文・記事検索サイト

AIで指定した技術分野の論文や記事を収集し、要約を提供するWebアプリケーション

## 特徴

- 📚 **学術論文検索**: arXiv APIとSemantic Scholar APIから論文を取得
- 🌐 **ウェブ記事収集**: RSS/Atomフィードから技術記事を収集
- 🤖 **AI要約**: OpenAIまたはローカルLLM (Ollama)で論文・記事を要約
- 🎨 **モダンUI**: レスポンシブデザイン、タブ切り替え、ダークモード対応
- 🔧 **カスタマイズ可能**: RSSソースを自由に追加・削除

## 必要要件

- Python 3.8以上
- OpenAI APIキー (オプション)
- Ollama (ローカルLLMを使用する場合)
- SERPAPI_KEY（Google Patentsで特許検索を行う場合）

## セットアップ

### 1. 依存パッケージのインストール

```bash
# uvを使う場合
uv sync
```

### 2. 環境変数の設定

`.env.example`をコピーして`.env`を作成:

```bash
cd flask-news
cp .env.example .env
```

`.env`ファイルを編集:

```env
# LLMタイプ: openai, ollama
LLM_TYPE=openai

# OpenAI APIキー (LLM_TYPE=openaiの場合)
OPENAI_API_KEY=your-api-key-here

# Ollama設定 (LLM_TYPE=ollamaの場合)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Google Patents検索用SERPAPIキー
SERPAPI_KEY=your-serpapi-key-here

# Flask設定
FLASK_ENV=development
FLASK_DEBUG=1
```

### 3. アプリケーションの起動

```bash
uv run ./flask_news/app.py
```

アプリケーションは http://localhost:5000 で起動します。

## 使い方

### 学術論文を検索
1. **📚 学術論文 (arXiv)** タブを選択
2. 技術分野を選択（機械学習、自然言語処理など）
3. オプションでキーワードを入力
4. 「論文・記事を検索」ボタンをクリック

### 特許検索
1. **📝 特許検索** タブを選択
2. 技術分野やキーワードを入力
3. 「特許を検索」ボタンをクリック
4. 検索結果から特許情報を閲覧
※ Google Patentsで特許検索を行う場合は、SERPAPI_KEYの設定が必要です。
[https://serpapi.com/](https://serpapi.com/)でAPIキーを取得してください。
### ウェブ記事を取得
1. **🌐 ウェブ記事 (RSS)** タブを選択
2. 必要に応じてRSSソースを追加・削除
3. 取得したいソースにチェックを入れる
4. 「記事を取得」ボタンをクリック

### AI要約を生成

- 各記事カードの「AI要約を生成」ボタンをクリック

## API エンドポイント

### POST /api/articles
論文を検索

**リクエスト:**
```json
{
  "field": "機械学習",
  "keywords": "transformer"
}
```

**レスポンス:**
```json
{
  "articles": [
    {
      "id": "2103.14030",
      "title": "論文タイトル",
      "abstract": "論文の概要...",
      "authors": ["著者1", "著者2"],
      "publishedDate": "2021-03-25T00:00:00Z",
      "url": "https://arxiv.org/abs/2103.14030",
      "source": "arXiv"
    }
  ]
}
```

### POST /api/web-articles
ウェブ記事を取得

**リクエスト:**
```json
{
  "sources": [
    {
      "name": "TechCrunch",
      "rssUrl": "https://techcrunch.com/feed/",
      "enabled": true
    }
  ]
}
```

### POST /api/summarize
論文・記事を要約

**リクエスト:**
```json
{
  "title": "論文タイトル",
  "abstract": "論文の概要..."
}
```

**レスポンス:**
```json
{
  "summary": "AI生成要約..."
}
```

## プロジェクト構造

```
flask-news/
├── app.py                 # メインアプリケーション
├── requirements.txt       # 依存パッケージ
├── .env.example          # 環境変数テンプレート
├── routes/               # APIルート
│   ├── articles.py       # 論文・記事取得
│   └── summarize.py      # 要約生成
├── services/             # ビジネスロジック
│   ├── arxiv.py         # arXiv API
│   ├── semantic_scholar.py  # Semantic Scholar API
│   ├── rss.py           # RSS取得
│   └── llm.py           # LLM統合
├── templates/            # HTMLテンプレート
│   └── index.html
└── static/              # 静的ファイル
    ├── style.css
    └── app.js
```

## LLMオプション

### OpenAI

```env
LLM_TYPE=openai
OPENAI_API_KEY=sk-...
```

### Ollama (ローカルLLM)

1. Ollamaをインストール: https://ollama.ai
2. モデルをダウンロード: `ollama pull llama3.2`
3. 環境変数を設定:

```env
LLM_TYPE=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

