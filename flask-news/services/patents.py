import os
from datetime import datetime
from typing import Dict, List

import requests


def fetch_patents(query: str, limit: int = 20) -> List[Dict]:
    """
    Google PatenとUSPTO PatentsViewから特許を検索

    Args:
        query: 検索キーワード
        limit: 取得する特許数

    Returns:
        特許情報のリスト
    """
    patents = []

    # まずGoogle Patentsから検索を試みる
    google_patents = fetch_google_patents(query, limit)
    patents.extend(google_patents)

    # 結果が少ない場合はPatentViewsも試す
    if len(patents) < 5:
        pv_patents = fetch_patentsview(query, limit - len(patents))
        patents.extend(pv_patents)

    return patents[:limit]


def fetch_patentsview(query: str, limit: int = 20) -> List[Dict]:
    """
    USPTO PatentViews APIから特許を取得
    https://patentsview.org/apis/api-endpoints
    """
    try:
        url = "https://api.patentsview.org/patents/query"

        # クエリパラメータを構築
        params = {
            "q": {
                "_or": [
                    {"_text_any": {"patent_title": query}},
                    {"_text_any": {"patent_abstract": query}}
                ]
            },
            "f": [
                "patent_number",
                "patent_title",
                "patent_abstract",
                "patent_date",
                "inventor_first_name",
                "inventor_last_name",
                "assignee_organization"
            ],
            "o": {
                "per_page": min(limit, 100)
            }
        }

        print(f'Searching PatentsView for: {query}')

        response = requests.post(
            url,
            json=params,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(response)

        if response.status_code != 200:
            print(f'PatentsView API error: {response.status_code}')
            return []

        data = response.json()
        patents_data = data.get('patents', [])

        patents = []
        for patent in patents_data:
            # 発明者情報を整形
            inventors = []
            if patent.get('inventors'):
                for inv in patent['inventors']:
                    name = f"{inv.get('inventor_first_name', '')} {inv.get('inventor_last_name', '')}".strip()
                    if name:
                        inventors.append(name)

            # 出願人情報
            assignees = []
            if patent.get('assignees'):
                for asg in patent['assignees']:
                    org = asg.get('assignee_organization', '').strip()
                    if org:
                        assignees.append(org)

            patents.append({
                'id': patent.get('patent_number', ''),
                'title': patent.get('patent_title', 'タイトル不明'),
                'abstract': patent.get('patent_abstract', '概要なし')[:500],
                'authors': inventors[:5],  # 最大5人
                'assignees': assignees[:3],  # 最大3組織
                'publishedDate': patent.get('patent_date', ''),
                'url': f"https://patents.google.com/patent/US{patent.get('patent_number', '')}",
                'source': 'USPTO'
            })

        print(f'Found {len(patents)} patents from PatentsView')
        return patents

    except requests.exceptions.Timeout:
        print('PatentsView API timeout')
        return []
    except Exception as e:
        print(f'PatentsView error: {e}')
        return []


def fetch_google_patents(query: str, limit: int = 10) -> List[Dict]:
    """
    Google Patentsから特許を検索
    1. SerpApiを使用（APIキーがある場合）
    2. フォールバック: Google Custom Search API
    3. フォールバック: 直接スクレイピング
    """
    serpapi_key = os.getenv('SERPAPI_KEY')

    if serpapi_key:
        return fetch_google_patents_serpapi(query, limit, serpapi_key)
    else:
        print('SerpApi key not found, using direct search')
        return fetch_google_patents_direct(query, limit)


def fetch_google_patents_serpapi(query: str, limit: int, api_key: str) -> List[Dict]:
    """
    SerpApiを使用してGoogle Patentsを検索
    https://serpapi.com/google-patents-api
    """
    try:
        url = "https://serpapi.com/search"

        params = {
            'engine': 'google_patents',
            'q': query,
            'api_key': api_key,
            'num': min(limit, 100)
        }

        print(f'Searching Google Patents via SerpApi for: {query}')

        response = requests.get(url, params=params, timeout=15)

        if response.status_code != 200:
            print(f'SerpApi error: {response.status_code}')
            return []

        data = response.json()
        results = data.get('organic_results', [])

        patents = []
        for result in results:
            # 特許番号を抽出
            patent_id = result.get('patent_id', '')

            # 発明者情報
            inventors = []
            inventor_info = result.get('inventor', '')
            if inventor_info:
                if isinstance(inventor_info, list):
                    inventors = [inv.get('name', inv) if isinstance(inv, dict) else inv for inv in inventor_info]
                else:
                    inventors = [inventor_info]

            # 出願人情報
            assignees = []
            assignee_info = result.get('assignee', '')
            if assignee_info:
                if isinstance(assignee_info, list):
                    assignees = [asg.get('name', asg) if isinstance(asg, dict) else asg for asg in assignee_info]
                else:
                    assignees = [assignee_info]

            # 公開日を取得
            pub_date = result.get('publication_date', '') or result.get('filing_date', '')

            patents.append({
                'id': patent_id,
                'title': result.get('title', 'タイトル不明'),
                'abstract': (result.get('snippet', '') or result.get('description', '') or '概要なし')[:500],
                'authors': inventors[:5],
                'assignees': assignees[:3],
                'publishedDate': pub_date,
                'url': result.get('pdf', result.get('link', f'https://patents.google.com/patent/{patent_id}')),
                'source': 'Google Patents'
            })

        print(f'Found {len(patents)} patents from Google Patents (SerpApi)')
        return patents

    except Exception as e:
        print(f'SerpApi error: {e}')
        return []


def fetch_google_patents_direct(query: str, limit: int) -> List[Dict]:
    """
    Google Patentsを直接検索（簡易実装）
    スクレイピングではなく、公開APIエンドポイントを使用
    """
    try:
        # Google Patents Public Dataを使用（制限あり）
        # 注: これはデモ版で、実際にはSerpApiを推奨

        print(f'Direct Google Patents search for: {query} (limited functionality)')

        # USPTOの公開APIを使用
        url = "https://developer.uspto.gov/ibd-api/v1/patent/application"

        params = {
            'searchText': query,
            'start': 0,
            'rows': min(limit, 25)
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            results = data.get('response', {}).get('docs', [])

            patents = []
            for result in results:
                app_number = result.get('appNumber', '')

                patents.append({
                    'id': app_number,
                    'title': result.get('inventionTitle', 'タイトル不明'),
                    'abstract': (result.get('appAbstract', '') or '概要なし')[:500],
                    'authors': [result.get('appInventorName', '')] if result.get('appInventorName') else [],
                    'assignees': [result.get('appAssigneeName', '')] if result.get('appAssigneeName') else [],
                    'publishedDate': result.get('appFilingDate', ''),
                    'url': f'https://patents.google.com/?q={app_number}',
                    'source': 'Google Patents (Direct)'
                })

            print(f'Found {len(patents)} patents from direct search')
            return patents

        return []

    except Exception as e:
        print(f'Direct search error: {e}')
        return []


def search_japanese_patents(query: str, limit: int = 20) -> List[Dict]:
    """
    日本の特許を検索（J-PlatPat）
    注: J-PlatPatは公式APIが制限されているため、簡易実装
    """
    # 将来的にはJ-PlatPatのAPIを使用
    # 現在は実装をスキップ
    return []
