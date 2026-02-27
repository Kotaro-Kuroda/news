# 実際の論文・記事データの取得について

このアプリケーションは、**実際のデータソース**から論文や記事を取得します。ダミーデータは使用していません。

## データソース

### 1. 学術論文 (arXiv)

**データソース**: [arXiv.org](https://arxiv.org) の公式API

**取得方法**:
- arXiv APIに直接リクエスト
- リアルタイムで最新の論文を取得
- 最大20件の論文を取得

**検索のコツ**:
- **英語のキーワードを使う**: arXivは英語のデータベースなので、英語キーワードが効果的
  - 良い例: `transformer`, `deep learning`, `neural network`
  - 日本語の分野は自動的に英語に変換されます
- **具体的なキーワード**: より具体的なキーワードで絞り込み
  - 例: `GPT`, `BERT`, `stable diffusion`, `reinforcement learning`
- **複数キーワード**: スペース区切りで複数指定可能
  - 例: `machine learning computer vision`

**検索例**:
1. 分野「機械学習」を選択 → 自動的に "machine learning" で検索
2. キーワード「transformer」を入力 → Transformerに関する最新論文
3. キーワード「llm fine-tuning」→ LLMのファインチューニング論文

### 2. ウェブ記事 (RSS/Atom フィード)

**データソース**: 登録したウェブサイトのRSSフィード

**デフォルト登録サイト**:
- **TechCrunch**: https://techcrunch.com/feed/
- **Hacker News**: https://hnrss.org/frontpage
- **DEV Community**: https://dev.to/feed
- **Qiita**: https://qiita.com/popular-items/feed

**カスタムサイトの追加**:
1. 「+ 追加」ボタンをクリック
2. サイト名とRSS URLを入力
3. 「追加」ボタンで登録

**追加可能なサイト例**:
- **Zenn**: https://zenn.dev/feed
- **GitHub Blog**: https://github.blog/feed/
- **Stack Overflow Blog**: https://stackoverflow.blog/feed/
- **Medium (トピック別)**: https://medium.com/feed/tag/[topic]
- **Reddit (サブレディット)**: https://www.reddit.com/r/[subreddit]/.rss

## トラブルシューティング

### 論文が取得できない

**症状**: 「検索結果が見つかりませんでした」と表示される

**解決方法**:
1. **より一般的なキーワードを試す**
   - NG: `極めて特殊な専門用語`
   - OK: `deep learning`, `neural network`

2. **英語キーワードを使う**
   - NG: 日本語のまま `深層学習`
   - OK: 英語で `deep learning`

3. **キーワードを短くする**
   - NG: `transformer based large language model fine-tuning techniques`
   - OK: `transformer llm`

4. **分野だけで検索**
   - キーワード欄を空にして、分野だけを選択

### ウェブ記事が取得できない

**症状**: 「記事が見つかりませんでした」と表示される

**解決方法**:
1. **RSSフィードURLを確認**
   - ブラウザで直接URLにアクセスして、XMLが表示されるか確認
   - RSS/Atomフィードである必要があります

2. **有効なソースがあるか確認**
   - 少なくとも1つのウェブサイトがチェック済み（有効）か確認

3. **デフォルトに戻す**
   - 「リセット」ボタンでデフォルトのサイトリストに戻す

### ネットワークエラー

**症状**: 「ネットワークエラー: サーバーに接続できませんでした」

**解決方法**:
1. インターネット接続を確認
2. 開発サーバーが起動しているか確認（`npm run dev`）
3. ブラウザのコンソールでエラーを確認（F12キー）

## データの信頼性

### arXiv
- ✅ 信頼性: 非常に高い（査読前論文のプレプリントサーバー）
- ✅ 更新頻度: 毎日
- ✅ カバレッジ: 物理学、数学、CS、生物学など幅広い分野

### RSSフィード
- ⚠️ 信頼性: ソースによる
- ✅ 更新頻度: リアルタイム〜数時間
- ⚠️ カバレッジ: 登録したサイトに依存

## パフォーマンス

- **arXiv検索**: 通常300ms〜1秒
- **RSS取得**: 登録サイト数に依存（1サイトあたり500ms〜2秒）
- **並列処理**: 複数のRSSフィードを同時に取得

## プライバシー

- ✅ 検索クエリはサーバー側でのみ処理
- ✅ arXiv APIへの直接アクセス（中間サーバー不要）
- ✅ RSS取得も直接アクセス
- ✅ データは保存されません（ブラウザのみ）
