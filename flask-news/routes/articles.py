from flask import Blueprint, jsonify, request
from services.arxiv import fetch_arxiv_papers
from services.patents import fetch_patents
from services.semantic_scholar import fetch_semantic_scholar_papers

articles_bp = Blueprint('articles', __name__)


@articles_bp.route('/articles', methods=['POST'])
def get_articles():
    """論文を検索して取得"""
    try:
        data = request.get_json()
        field = data.get('field', '')
        keywords = data.get('keywords', '')

        print(f'Searching for: field={field}, keywords={keywords}')

        # arXiv APIから論文を取得
        articles = fetch_arxiv_papers(field, keywords)

        # arXivで取得できなかった場合はSemantic Scholarを試す
        if not articles:
            fallback_query = keywords or field or 'artificial intelligence'
            articles = fetch_semantic_scholar_papers(fallback_query)

        if not articles:
            return jsonify({
                'articles': [],
                'message': '検索結果が見つかりませんでした。別のキーワードで試してください。'
            })

        return jsonify({'articles': articles})

    except Exception as e:
        print(f'Error fetching articles: {e}')
        return jsonify({
            'error': '論文の取得に失敗しました',
            'details': str(e)
        }), 500


@articles_bp.route('/web-articles', methods=['POST'])
def get_web_articles():
    """ウェブ記事をRSSから取得"""
    try:
        from services.rss import fetch_multiple_rss_feeds

        data = request.get_json()
        sources = data.get('sources', [])

        if not sources:
            return jsonify({
                'articles': [],
                'message': 'ソースが指定されていません'
            })

        articles = fetch_multiple_rss_feeds(sources)

        if not articles:
            return jsonify({
                'articles': [],
                'message': '記事が見つかりませんでした'
            })

        return jsonify({'articles': articles})

    except Exception as e:
        print(f'Error fetching web articles: {e}')
        return jsonify({
            'error': 'ウェブ記事の取得に失敗しました',
            'details': str(e)
        }), 500


@articles_bp.route('/patents', methods=['POST'])
def get_patents():
    """特許を検索して取得"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        limit = data.get('limit', 20)

        if not query:
            return jsonify({
                'patents': [],
                'message': '検索キーワードを入力してください'
            })

        print(f'Searching for patents: query={query}')

        # 特許を検索
        patents = fetch_patents(query, limit)

        if not patents:
            return jsonify({
                'patents': [],
                'message': '特許が見つかりませんでした。別のキーワードで試してください。'
            })

        return jsonify({'patents': patents})

    except Exception as e:
        print(f'Error fetching patents: {e}')
        return jsonify({
            'error': '特許の取得に失敗しました',
            'details': str(e)
        }), 500
