import requests
import json
import subprocess
import os
from datetime import datetime

# ✅ Load API keys from GitHub Secrets
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GH_TOKEN = os.getenv("GH_TOKEN")  # GitHub Token for push

# ✅ Output file
OUTPUT_FILE = "docs/latest_news.html"
REPO = "krishxd3/news-auto"  # Change if repo name is different
BRANCH = "main"

# ✅ Create docs folder if not exists
os.makedirs("docs", exist_ok=True)

# ✅ Step 1: Fetch latest stock market news from India
def fetch_news():
    print("📡 Fetching stock market news...")
    url = f"https://newsdata.io/api/1/latest?apikey={NEWSDATA_API_KEY}&q=Stock Market&country=in&language=en&timezone=Asia/Kolkata"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print("❌ Failed to fetch news:", response.status_code)
        return []

# ✅ Step 2: Summarize using DeepSeek
def summarize_with_deepseek(text):
    prompt = (
        f"Summarize this Indian stock market news in 2-3 lines "
        f"and describe its impact on Indian stock market or specific stocks:\n\n{text}"
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

# ✅ Step 3: Generate HTML file
def generate_html(news_items):
    print("📝 Generating HTML file...")
    now = datetime.now().strftime("%d %B %Y, %I:%M %p")
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>📈 Latest Indian Stock Market News</title>
        <style>
            body {{ font-family: sans-serif; padding: 20px; background: #f8f8f8; }}
            .news-block {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 20px; }}
            .timestamp {{ color: #666; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <h1>📰 Latest Indian Stock Market News Summary</h1>
        <div class="timestamp">Last Updated: {now}</div>
    """

    for i, article in enumerate(news_items[:5], 1):
        title = article.get("title", "No Title")
        description = article.get("description", "")
        full_text = f"{title}. {description}"
        summary = summarize_with_deepseek(full_text)

        html += f"""
        <div class="news-block">
            <h3>{i}. {title}</h3>
            <p><strong>Impact Summary:</strong><br>{summary}</p>
        </div>
        """

    html += "</body></html>"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ HTML saved to → {OUTPUT_FILE}")

# ✅ Step 4: Git Commit & Push with Token Auth
def git_commit_push():
    print("📤 Committing and pushing file to GitHub...")
    subprocess.run(["git", "config", "--global", "user.name", "NewsAutoBot"])
    subprocess.run(["git", "config", "--global", "user.email", "news@bot.com"])
    
    # Replace origin URL with GH_TOKEN to push from GitHub Action
    remote_url = f"https://x-access-token:{GH_TOKEN}@github.com/{REPO}.git"
    subprocess.run(["git", "remote", "set-url", "origin", remote_url])
    
    subprocess.run(["git", "add", OUTPUT_FILE])
    subprocess.run(["git", "commit", "-m", "🔁 Auto update news summary"])
    subprocess.run(["git", "push", "origin", BRANCH])
    print("✅ Push completed!")

# ✅ Main function
def main():
    articles = fetch_news()
    if articles:
        generate_html(articles)
        git_commit_push()
    else:
        print("❌ No articles found.")

if __name__ == "__main__":
    main()

