import time
import xml.etree.ElementTree as ET
from typing import Dict, List

import requests


def fetch_arxiv_papers(field: str, keywords: str) -> List[Dict]:
    """arXiv APIから論文を取得"""
    # 検索クエリの構築
    search_queries = []
    if keywords:
        search_queries.append(keywords)
    if field:
        # 日本語の分野を英語に変換
        field_map = {
            '機械学習': 'machine learning',
            '自然言語処理': 'natural language processing NLP',
            'コンピュータビジョン': 'computer vision',
            'データサイエンス': 'data science',
            'Web開発': 'web development',
            'モバイル開発': 'mobile development',
            'クラウドコンピューティング': 'cloud computing',
            'ブロックチェーン': 'blockchain',
            'サイバーセキュリティ': 'cybersecurity security',
            '量子コンピューティング': 'quantum computing',
        }
        search_queries.append(field_map.get(field, field))
    else:
        search_queries.append('artificial intelligence')
    search_query = '+AND+'.join(search_queries)

    # arXiv API URL（複数のエンドポイントを試す）
    urls = [
        f'http://export.arxiv.org/api/query?search_query=all:{search_query}&start=0&max_results=20&sortBy=submittedDate&sortOrder=descending',
        f'https://export.arxiv.org/api/query?search_query=all:{search_query}&start=0&max_results=20&sortBy=submittedDate&sortOrder=descending',
    ]

    max_retries = 3
    articles = []

    for url in urls:
        for attempt in range(max_retries):
            try:
                print(f'Fetching from arXiv (attempt {attempt + 1}/{max_retries}): {url}')

                response = requests.get(
                    url,
                    headers={'User-Agent': 'NewsAggregator/1.0'},
                    timeout=10
                )

                if response.status_code == 200:
                    articles = parse_arxiv_response(response.text)
                    if articles:
                        print(f'Successfully fetched {len(articles)} articles from arXiv')
                        return articles

                if response.status_code == 503:
                    delay = 0.8 * (attempt + 1)
                    print(f'arXiv returned 503. Retrying after {delay}s...')
                    time.sleep(delay)
                    continue

            except Exception as e:
                print(f'Failed with {url}: {e}')
                time.sleep(0.8 * (attempt + 1))

        if articles:
            break

    return articles


def parse_arxiv_response(xml_text: str) -> List[Dict]:
    """arXiv APIのXMLレスポンスをパース"""
    try:
        # 名前空間を定義
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }

        root = ET.fromstring(xml_text)
        entries = root.findall('atom:entry', namespaces)

        articles = []
        for entry in entries:
            # タイトル
            title_elem = entry.find('atom:title', namespaces)
            title = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else 'タイトル不明'

            # 概要
            summary_elem = entry.find('atom:summary', namespaces)
            abstract = summary_elem.text.strip().replace('\n', ' ') if summary_elem is not None else '概要なし'

            # URL
            id_elem = entry.find('atom:id', namespaces)
            url = id_elem.text.strip() if id_elem is not None else '#'

            # 公開日
            published_elem = entry.find('atom:published', namespaces)
            published = published_elem.text.strip() if published_elem is not None else ''

            # 著者
            authors = []
            author_elems = entry.findall('atom:author', namespaces)
            for author_elem in author_elems:
                name_elem = author_elem.find('atom:name', namespaces)
                if name_elem is not None:
                    authors.append(name_elem.text.strip())

            articles.append({
                'id': url.split('/')[-1] if url else f'arxiv-{len(articles)}',
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'url': url,
                'publishedDate': published,
                'source': 'arXiv'
            })

        return articles

    except Exception as e:
        print(f'Error parsing arXiv response: {e}')
        return []
