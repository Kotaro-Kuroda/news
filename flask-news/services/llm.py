import os

from openai import OpenAI


def generate_summary(title: str, abstract: str) -> str:
    """論文の要約を生成"""
    llm_type = os.getenv('LLM_TYPE', 'openai')

    if llm_type == 'ollama':
        return generate_summary_ollama(title, abstract)
    elif llm_type == 'openai' and os.getenv('OPENAI_API_KEY'):
        return generate_summary_openai(title, abstract)
    else:
        return generate_dummy_summary(title, abstract)


def generate_summary_openai(title: str, abstract: str) -> str:
    """OpenAI APIで要約を生成"""
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        completion = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {
                    'role': 'system',
                    'content': 'あなたは技術論文を要約する専門家です。論文のタイトルと概要から、簡潔で分かりやすい日本語の要約を3-4文で作成してください。'
                },
                {
                    'role': 'user',
                    'content': f'以下の論文を要約してください。\n\nタイトル: {title}\n\n概要: {abstract}'
                }
            ],
            max_tokens=300,
            temperature=0.7
        )

        return completion.choices[0].message.content or generate_dummy_summary(title, abstract)

    except Exception as e:
        print(f'OpenAI API error: {e}')
        return generate_dummy_summary(title, abstract)


def generate_summary_ollama(title: str, abstract: str) -> str:
    """Ollamaで要約を生成"""
    try:
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        print(model)
        client = OpenAI(
            base_url=base_url,
            api_key='ollama'  # ダミーキー
        )
        print(client.base_url)

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    'role': 'system',
                    'content': 'あなたは技術論文を要約する専門家です。論文のタイトルと概要から、簡潔で分かりやすい日本語の要約を3-4文で作成してください。'
                },
                {
                    'role': 'user',
                    'content': f'以下の論文を要約してください。\n\nタイトル: {title}\n\n概要: {abstract}'
                }
            ],
            max_tokens=300,
            temperature=0.7
        )
        print(completion)

        return completion.choices[0].message.content or generate_dummy_summary(title, abstract)

    except Exception as e:
        print(f'Ollama error: {e}')
        return generate_dummy_summary(title, abstract)


def generate_dummy_summary(title: str, abstract: str) -> str:
    """ダミーの要約を生成"""
    title_snippet = title[:50] + '...' if len(title) > 50 else title
    abstract_snippet = abstract[:100] + '...' if len(abstract) > 100 else abstract

    return f'【要約】{title_snippet}\n\nこの研究は、{abstract_snippet}という内容を扱っています。主な貢献は新しい手法の提案と実験的検証です。結果は既存手法を上回る性能を示しています。'
