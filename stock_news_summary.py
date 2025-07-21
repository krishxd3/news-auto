# 🔁 stock_news_summary.py

import requests
import json
import subprocess
import os
from datetime import datetime

# ✅ Load API keys from GitHub Secrets
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ✅ Output HTML file location (used for GitHub Pages)
OUTPUT_FILE = "docs/latest_news.html"  # Make sure you enable GitHub Pages on /docs folder

# ✅ Create "docs" folder if it doesn't exist
os.makedirs("docs", exist_ok=True)

# 🔹 Step 1: Fetch latest Indian stock news headlines
def fetch_news():
    url = f"https://newsdata.io/api/1/latest?apikey={NEWSDATA_API_KEY}&q=Stock Market&country=in&language=en&timezone=Asia/Kolkata"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print("❌ Failed to fetch news:", response.status_code)
        return []

# 🔹 Step 2: Summarize news article using DeepSeek via OpenRouter
def summarize_with_deepseek(text):
    prompt = (
        f"Summarize this Indian stock market news in 2-3 lines, "
        f"and describe its likely impact on the Indian stock market or specific stock:\n\n{text}"
    )
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        print("❌ Failed to summarize:", response.status_code)
        print(response.text)
        return "❌ Could not summarize"

# 🔹 Step 3: Create clean HTML output
def generate_html(news_items):
    print("📝 Generating HTML output...")
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    html = f"""
    <html>
    <head>
        <title>📈 Latest Stock Market News Summary</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 20px;
                background: #f9f9f9;
            }}
            h1 {{
                color: #234155;
            }}
            .news-block {{
                background: white;
                margin: 20px 0;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 0 8px rgba(0,0,0,0.1);
            }}
            .timestamp {{
                font-size: 14px;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <h1>📰 Indian Stock Market News (Auto-Updating)</h1>
        <div class="timestamp">Last updated: {now}</div>
    """

    for i, item in enumerate(news_items[:5], 1):  # Limit to top 5
        title = item.get("title", "No title")
        description = item.get("description", "")
        full_text = f"{title}. {description}"
        summary = summarize_with_deepseek(full_text)

        html += f"""
        <div class="news-block">
            <h3>{i}. {title}</h3>
            <p><strong>🧠 Summary & Impact:</strong><br>{summary}</p>
        </div>
        """

    html += "</body></html>"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ HTML saved to: {OUTPUT_FILE}")

# 🔹 Step 4: Auto commit & push to GitHub (for GitHub Pages)
def git_commit_push():
    print("📤 Git committing & pushing updates...")
    subprocess.run(["git", "config", "--global", "user.name", "AutoBot"])
    subprocess.run(["git", "config", "--global", "user.email", "newsbot@example.com"])
    subprocess.run(["git", "add", OUTPUT_FILE])
    subprocess.run(["git", "commit", "-m", "🔄 Auto update news summary"])
    subprocess.run(["git", "push"])
    print("✅ Git push complete.")

# 🔹 Main driver
def main():
    print("📡 Fetching news...")
    articles = fetch_news()
    if articles:
        generate_html(articles)
        git_commit_push()
    else:
        print("❌ No articles found.")

if __name__ == "__main__":
    main()
