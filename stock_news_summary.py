import requests
from datetime import datetime

# ✅ Your API keys
NEWSDATA_API_KEY = "pub_51c51defabfb4c8694cbb1a768e955b6"
OPENROUTER_API_KEY = "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"

# ✅ Output file name
OUTPUT_FILE = "latest_news.html"

# ✅ Step 1: Fetch latest Indian stock market news
def fetch_news():
    print("📡 Fetching latest news...")
    url = f"https://newsdata.io/api/1/latest?apikey={NEWSDATA_API_KEY}&q=Stock Market&country=in&language=en&timezone=Asia/Kolkata"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json().get("results", [])
    print("❌ Failed to fetch news:", res.status_code)
    return []

# ✅ Step 2: Use DeepSeek to summarize in English (1 paragraph)
def summarize_news(text):
    prompt = (
        "Summarize the following Indian stock market news in one paragraph in English. "
        "Also include the likely impact on the Indian stock market or specific stocks:\n\n"
        f"{text}\n\nSummary:"
    )
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    if res.status_code == 200:
        return res.json()["choices"][0]["message"]["content"].strip()
    print("❌ Summary generation failed:", res.status_code)
    return "⚠️ Could not summarize this article."

# ✅ Step 3: Generate `latest_news.html` file
def generate_html(news_items):
    print("✏️ Generating HTML file...")
    now = datetime.now().strftime("%d %B %Y, %I:%M %p")
    html = f"""
    <html>
    <head>
        <title>📈 Indian Stock Market News Summary</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f9f9f9;
                padding: 25px;
            }}
            .news-block {{
                background: #fff;
                padding: 20px;
                border-left: 5px solid #3477eb;
                margin-bottom: 20px;
                border-radius: 6px;
                box-shadow: 0 0 10px rgba(0,0,0,0.05);
            }}
            .timestamp {{
                font-size: 14px;
                color: #777;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <h1>📊 Indian Stock Market News </h1>
        <div class="timestamp">Last updated: {now}</div>
    """

    for i, article in enumerate(news_items[:5], 1):
        title = article.get("title", "No Title")
        description = article.get("description", "")
        full_text = f"{title}. {description}"
        print(f"🧠 Summarizing #{i}: {title[:60]}...")
        summary = summarize_news(full_text)
        html += f"""
        <div class="news-block">
            <h3>{i}. {title}</h3>
            <p>{summary}</p>
        </div>
        """

    html += "</body></html>"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ File created: {OUTPUT_FILE}")

# ✅ Main runner
def main():
    articles = fetch_news()
    if articles:
        generate_html(articles)
    else:
        print("❌ No news found to summarize.")

if __name__ == "__main__":
    main()


