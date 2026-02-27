from typing import Dict, List

import requests


def fetch_semantic_scholar_papers(query: str) -> List[Dict]:
    """Semantic Scholar APIから論文を取得"""
    url = 'https://api.semanticscholar.org/graph/v1/paper/search'

    try:
        response = requests.get(
            url,
            params={
                'query': query,
                'limit': 20,
                'fields': 'title,abstract,authors,year,url,tldr'
            },
            headers={'User-Agent': 'NewsAggregator/1.0'},
            timeout=10
        )

        if response.status_code != 200:
            print(f'Semantic Scholar API error: {response.status_code}')
            return []

        data = response.json()
        papers = data.get('data', [])

        articles = []
        for paper in papers:
            year = str(paper.get('year', ''))
            authors = [author.get('name', '') for author in paper.get('authors', [])]

            articles.append({
                'id': paper.get('paperId', f'semantic-{len(articles)}'),
                'title': paper.get('title', 'タイトル不明'),
                'authors': authors,
                'abstract': paper.get('abstract') or paper.get('tldr', {}).get('text', '概要なし'),
                'url': paper.get('url', '#'),
                'publishedDate': f'{year}-01-01' if year else '',
                'source': 'Semantic Scholar'
            })

        return articles

    except Exception as e:
        print(f'Semantic Scholar API error: {e}')
        return []
