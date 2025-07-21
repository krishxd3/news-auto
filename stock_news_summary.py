import requests
import json
import subprocess

# ✅ Your API KEYS
NEWSDATA_API_KEY = "pub_51c51defabfb4c8694cbb1a768e955b6"
OPENROUTER_API_KEY = "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"

# ✅ Step 1: Fetch latest stock news from newsdata.io
def fetch_news():
    url = f"https://newsdata.io/api/1/latest?apikey={NEWSDATA_API_KEY}&q=Stock Market&country=in&language=en&timezone=Asia/Kolkata"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print("❌ Failed to fetch news:", response.status_code)
        return []

# ✅ Step 2: Summarize using DeepSeek (via OpenRouter)
def summarize_with_deepseek(text):
    prompt = (
        f"Summarize the following Indian stock market news in 2-3 lines "
        f"and tell what kind of impact it can have on the Indian stock market or any specific stock:\n\n{text}"
    )
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-r1:free",  # 💡 Free DeepSeek model
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        print("❌ Failed to summarize:", response.status_code)
        print(response.text)
        return "❌ Could not summarize"

# ✅ Step 3: Main Execution
def run_summary():
    print("📡 Fetching news...")
    articles = fetch_news()
    
    if not articles:
        print("No news found.")
        return

    for i, article in enumerate(articles[:5], 1):  # Limit to 5 headlines at a time
        title = article.get("title", "")
        description = article.get("description", "")
        full_text = f"{title}. {description}"
        print(f"\n📰 News #{i}: {title}")
        print("🧠 Generating Summary + Market Impact...")
        summary = summarize_with_deepseek(full_text)
        print("📋 Summary:", summary)

# Run the script
if __name__ == "__main__":
    run_summary()
subprocess.run(["git", "add", OUTPUT_FILE])
subprocess.run(["git", "commit", "-m", "Update latest news"])
subprocess.run(["git", "push"])
