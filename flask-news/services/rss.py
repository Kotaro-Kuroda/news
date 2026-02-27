import concurrent.futures
from datetime import datetime
from typing import Dict, List

import feedparser
import requests


def fetch_rss_feed(rss_url: str, source_name: str, category: str = '未分類') -> List[Dict]:
    """RSSフィードを取得してパース"""
    try:
        response = requests.get(
            rss_url,
            headers={'User-Agent': 'NewsAggregator/1.0'},
            timeout=10
        )

        if response.status_code != 200:
            print(f'Failed to fetch {source_name}: {response.status_code}')
            return []

        feed = feedparser.parse(response.text)
        articles = []

        for entry in feed.entries[:20]:  # 最大20件
            # タイトル
            title = entry.get('title', 'タイトル不明')

            # リンク
            link = entry.get('link', '#')

            # 説明
            description = entry.get('summary', entry.get('description', ''))
            # HTMLタグを削除
            from bs4 import BeautifulSoup
            description = BeautifulSoup(description, 'html.parser').get_text()

            # 公開日
            published = entry.get('published', entry.get('updated', ''))

            # 著者
            author = entry.get('author', '')
            authors = [author] if author else []

            articles.append({
                'id': f'{source_name}-{len(articles)}',
                'title': title,
                'authors': authors,
                'abstract': description[:500],  # 最大500文字
                'url': link,
                'publishedDate': published,
                'source': source_name,
                'category': category
            })

        return articles

    except Exception as e:
        print(f'Error fetching {source_name}: {e}')
        return []


def fetch_multiple_rss_feeds(sources: List[Dict]) -> List[Dict]:
    """複数のRSSフィードを並列で取得"""
    enabled_sources = [s for s in sources if s.get('enabled', True)]

    if not enabled_sources:
        return []

    all_articles = []

    # 並列処理で各RSSフィードを取得
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(
                fetch_rss_feed,
                source['rssUrl'],
                source['name'],
                source.get('category', '未分類')
            ): source
            for source in enabled_sources
        }

        for future in concurrent.futures.as_completed(futures):
            try:
                articles = future.result()
                all_articles.extend(articles)
            except Exception as e:
                print(f'Error in thread: {e}')

    # 日付でソート（新しい順）
    all_articles.sort(key=lambda x: x.get('publishedDate', ''), reverse=True)

    return all_articles[:50]  # 最大50件
