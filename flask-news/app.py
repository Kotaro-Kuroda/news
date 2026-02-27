import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from routes.articles import articles_bp
from routes.summarize import summarize_bp

# 環境変数を読み込む
load_dotenv()

app = Flask(__name__)
CORS(app)

# 設定
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JSON_AS_ASCII'] = False  # 日本語のJSONレスポンスを正しく表示

# ブループリントを登録
app.register_blueprint(articles_bp, url_prefix='/api')
app.register_blueprint(summarize_bp, url_prefix='/api')


@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')


@app.route('/health')
def health():
    """ヘルスチェック"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    print(f'Starting Flask app on http://localhost:{port}')
    print(f'LLM Type: {os.getenv("LLM_TYPE", "dummy")}')
    app.run(host='0.0.0.0', port=port, debug=debug)
