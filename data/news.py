import requests
from config import NEWS_API_KEY


def get_top_news(max_headlines=5):
    try:
        url = f"https://newsapi.org/v2/top-headlines"
        params = {
            'country': 'us',
            'apiKey': NEWS_API_KEY,
            'pageSize': max_headlines
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        headlines = []
        for article in data.get('articles', []):
            headlines.append(
                f"{article['title']} - {article['source']['name']}")

        return headlines

    except Exception as e:
        print(f"News error: {e}")
        return []
