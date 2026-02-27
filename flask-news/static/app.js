// デフォルトのウェブサイトソース
const DEFAULT_SOURCES = [
    { id: 'techcrunch', name: 'TechCrunch', url: 'https://techcrunch.com', rssUrl: 'https://techcrunch.com/feed/', category: 'スタートアップ', enabled: true },
    { id: 'hackernews', name: 'Hacker News', url: 'https://news.ycombinator.com', rssUrl: 'https://hnrss.org/frontpage', category: 'テックニュース', enabled: true },
    { id: 'devto', name: 'DEV Community', url: 'https://dev.to', rssUrl: 'https://dev.to/feed', category: '開発', enabled: true },
    { id: 'qiita', name: 'Qiita', url: 'https://qiita.com', rssUrl: 'https://qiita.com/popular-items/feed', category: '日本語', enabled: true },
];

// 状態管理
let sources = [];
let articles = [];
let currentTab = 'arxiv';

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initArxivSearch();
    initPatentSearch();
    initWebSources();
    loadSources();
});

// タブ切り替え
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            switchTab(tab);
        });
    });
}

function switchTab(tab) {
    currentTab = tab;

    // ボタンのアクティブ状態を切り替え
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tab);
    });

    // コンテンツの表示を切り替え
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tab}-tab`);
    });

    // 記事リストをクリア
    clearArticles();
}

// arXiv検索の初期化
function initArxivSearch() {
    const searchBtn = document.getElementById('search-btn');
    searchBtn.addEventListener('click', searchArxiv);

    // Enterキーで検索
    document.getElementById('keywords').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchArxiv();
    });
}

async function searchArxiv() {
    const field = document.getElementById('field').value;
    const keywords = document.getElementById('keywords').value;

    showLoading();
    hideError();

    try {
        const response = await fetch('/api/articles', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ field, keywords })
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || '論文の取得に失敗しました');
            clearArticles();
        } else if (data.articles && data.articles.length > 0) {
            displayArticles(data.articles);
        } else {
            showError(data.message || '検索結果が見つかりませんでした');
            clearArticles();
        }
    } catch (error) {
        showError('ネットワークエラー: サーバーに接続できませんでした');
        clearArticles();
    } finally {
        hideLoading();
    }
}

// 特許検索の初期化
function initPatentSearch() {
    const searchBtn = document.getElementById('search-patents-btn');
    searchBtn.addEventListener('click', searchPatents);

    // Enterキーで検索
    document.getElementById('patent-query').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchPatents();
    });
}

async function searchPatents() {
    const query = document.getElementById('patent-query').value.trim();

    if (!query) {
        showError('検索キーワードを入力してください');
        return;
    }

    showLoading();
    hideError();

    try {
        const response = await fetch('/api/patents', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, limit: 20 })
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || '特許の取得に失敗しました');
            clearArticles();
        } else if (data.patents && data.patents.length > 0) {
            displayArticles(data.patents, true);  // isPatent = true
        } else {
            showError(data.message || '特許が見つかりませんでした');
            clearArticles();
        }
    } catch (error) {
        showError('ネットワークエラー: サーバーに接続できませんでした');
        clearArticles();
    } finally {
        hideLoading();
    }
}

// ウェブソースの初期化
function initWebSources() {
    document.getElementById('add-source-btn').addEventListener('click', toggleAddForm);
    document.getElementById('confirm-add-btn').addEventListener('click', addSource);
    document.getElementById('reset-sources-btn').addEventListener('click', resetSources);
    document.getElementById('fetch-web-btn').addEventListener('click', fetchWebArticles);
}

function loadSources() {
    const stored = localStorage.getItem('websiteSources');
    sources = stored ? JSON.parse(stored) : DEFAULT_SOURCES;
    sources = sources.map(normalizeSource);
    renderSources();
    updateFetchButton();
}

function normalizeSource(source) {
    return {
        ...source,
        category: source.category && source.category.trim() ? source.category.trim() : '未分類'
    };
}

function saveSources() {
    localStorage.setItem('websiteSources', JSON.stringify(sources));
    updateFetchButton();
}

function renderSources() {
    const container = document.getElementById('sources-list');
    container.innerHTML = sources.map((source, index) => `
        <div class="source-item">
            <div class="source-info">
                <input type="checkbox" ${source.enabled ? 'checked' : ''}
                    onchange="toggleSource(${index})">
                <div class="source-details">
                    <div class="source-name">${source.name}</div>
                    <div class="source-category">カテゴリ: ${source.category || '未分類'}</div>
                    <div class="source-url">${source.rssUrl}</div>
                </div>
            </div>
            <button class="delete-btn" onclick="deleteSource(${index})">削除</button>
        </div>
    `).join('');
}

function toggleAddForm() {
    const form = document.getElementById('add-source-form');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

function addSource() {
    const name = document.getElementById('source-name').value.trim();
    const url = document.getElementById('source-url').value.trim();
    const rssUrl = document.getElementById('source-rss').value.trim();
    const category = document.getElementById('source-category').value.trim();

    if (!name || !rssUrl) {
        alert('名前とRSS URLは必須です');
        return;
    }

    sources.push({
        id: `custom-${Date.now()}`,
        name,
        url: url || rssUrl,
        rssUrl,
        category: category || '未分類',
        enabled: true
    });

    saveSources();
    renderSources();

    // フォームをリセット
    document.getElementById('source-name').value = '';
    document.getElementById('source-url').value = '';
    document.getElementById('source-rss').value = '';
    document.getElementById('source-category').value = '';
    toggleAddForm();
}

function toggleSource(index) {
    sources[index].enabled = !sources[index].enabled;
    saveSources();
}

function deleteSource(index) {
    if (confirm('このウェブサイトを削除しますか？')) {
        sources.splice(index, 1);
        saveSources();
        renderSources();
    }
}

function resetSources() {
    if (confirm('デフォルトのウェブサイトリストに戻しますか？')) {
        sources = [...DEFAULT_SOURCES];
        saveSources();
        renderSources();
    }
}

function updateFetchButton() {
    const btn = document.getElementById('fetch-web-btn');
    const enabledCount = sources.filter(s => s.enabled).length;
    btn.disabled = enabledCount === 0;
}

async function fetchWebArticles() {
    showLoading();
    hideError();

    try {
        const response = await fetch('/api/web-articles', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sources })
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || 'ウェブ記事の取得に失敗しました');
            clearArticles();
        } else if (data.articles && data.articles.length > 0) {
            displayWebArticles(data.articles);
        } else {
            showError(data.message || '記事が見つかりませんでした');
            clearArticles();
        }
    } catch (error) {
        showError('ネットワークエラー: サーバーに接続できませんでした');
        clearArticles();
    } finally {
        hideLoading();
    }
}

// 記事表示
function displayArticles(articleList, isPatent = false) {
    articles = articleList;
    const container = document.getElementById('articles-container');

    const itemType = isPatent ? '特許' : '記事';

    container.innerHTML = `
        <h2 class="results-header">検索結果: ${articles.length}件の${itemType}</h2>
        ${articles.map((article, index) => createArticleCard(article, index, isPatent)).join('')}
    `;
}

function displayWebArticles(articleList) {
    articles = articleList;
    const container = document.getElementById('articles-container');

    const groups = {};
    for (let i = 0; i < articles.length; i++) {
        const category = (articles[i].category && articles[i].category.trim()) ? articles[i].category : '未分類';
        if (!groups[category]) {
            groups[category] = [];
        }
        groups[category].push(i);
    }

    const categories = Object.keys(groups);

    const tabsHtml = categories.map((category, index) => `
        <button class="category-tab ${index === 0 ? 'active' : ''}" data-index="${index}">
            ${category} (${groups[category].length})
        </button>
    `).join('');

    const panelsHtml = categories.map((category, index) => `
        <div class="category-panel ${index === 0 ? 'active' : ''}" data-index="${index}">
            ${groups[category].map(i => createArticleCard(articles[i], i, false)).join('')}
        </div>
    `).join('');

    container.innerHTML = `
        <h2 class="results-header">検索結果: ${articles.length}件のウェブ記事</h2>
        <div class="category-tabs">${tabsHtml}</div>
        <div class="category-panels">${panelsHtml}</div>
    `;

    initCategoryTabs();
}

function initCategoryTabs() {
    const tabs = document.querySelectorAll('.category-tab');
    const panels = document.querySelectorAll('.category-panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const index = tab.dataset.index;

            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));

            tab.classList.add('active');
            const panel = document.querySelector(`.category-panel[data-index="${index}"]`);
            if (panel) {
                panel.classList.add('active');
            }
        });
    });
}

function createArticleCard(article, index, isPatent = false) {
    // 特許の場合は出願人情報も表示
    const assigneeInfo = isPatent && article.assignees && article.assignees.length > 0
        ? `<span>出願人: ${article.assignees.slice(0, 2).join(', ')}${article.assignees.length > 2 ? ' 他' : ''}</span>`
        : '';
    const categoryInfo = !isPatent && article.category
        ? `<span>カテゴリ: ${article.category}</span>`
        : '';

    return `
        <div class="article-card" id="article-${index}">
            <h3 class="article-title">${article.title}</h3>
            <div class="article-meta">
                <span class="article-source">${article.source}</span>
                <span>${new Date(article.publishedDate).toLocaleDateString('ja-JP')}</span>
                ${article.authors && article.authors.length > 0 ? `<span>${isPatent ? '発明者' : '著者'}: ${article.authors.slice(0, 3).join(', ')}${article.authors.length > 3 ? ' 他' : ''}</span>` : ''}
                ${assigneeInfo}
                ${categoryInfo}
            </div>
            <p class="article-abstract">${article.abstract}</p>
            <div id="summary-${index}"></div>
            <div class="article-actions">
                <a href="${article.url}" target="_blank">詳細を見る</a>
                <button onclick="summarizeArticle(${index})">AI要約を生成</button>
            </div>
        </div>
    `;
}

async function summarizeArticle(index) {
    const article = articles[index];
    const summaryDiv = document.getElementById(`summary-${index}`);
    const button = event.target;

    button.disabled = true;
    button.textContent = '要約中...';

    try {
        const response = await fetch('/api/summarize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: article.title,
                abstract: article.abstract
            })
        });

        const data = await response.json();

        if (response.ok) {
            summaryDiv.innerHTML = `
                <div class="article-summary">
                    <h4>AI要約:</h4>
                    <p>${data.summary}</p>
                </div>
            `;
            button.style.display = 'none';
        } else {
            alert('要約の生成に失敗しました');
            button.disabled = false;
            button.textContent = 'AI要約を生成';
        }
    } catch (error) {
        alert('ネットワークエラーが発生しました');
        button.disabled = false;
        button.textContent = 'AI要約を生成';
    }
}

function clearArticles() {
    const container = document.getElementById('articles-container');
    container.innerHTML = '<div class="placeholder"><p>技術分野を選択して、論文・記事を検索してください</p></div>';
}

// UI ヘルパー
function showLoading() {
    document.getElementById('loading').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = '⚠️ ' + message;
    errorDiv.style.display = 'block';
}

function hideError() {
    document.getElementById('error-message').style.display = 'none';
}
