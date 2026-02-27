from flask import Blueprint, jsonify, request
from services.llm import generate_summary

summarize_bp = Blueprint('summarize', __name__)


@summarize_bp.route('/summarize', methods=['POST'])
def summarize():
    """論文を要約"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        abstract = data.get('abstract', '')

        if not title or not abstract:
            return jsonify({
                'error': 'タイトルと概要が必要です'
            }), 400

        summary = generate_summary(title, abstract)

        return jsonify({'summary': summary})

    except Exception as e:
        print(f'Error generating summary: {e}')
        return jsonify({
            'error': '要約の生成に失敗しました',
            'details': str(e)
        }), 500
