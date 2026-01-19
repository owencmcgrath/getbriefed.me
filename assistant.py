from data.calendar import get_calendar_events
from ai.summarizer import generate_briefing
from data.email import get_recent_emails
from output.voice import call_with_briefing
from data.news import get_top_news
from data.stocks import get_stock_prices
from data.weather import get_weather

from config import ICLOUD_USERNAME, ICLOUD_APP_PASSWORD

if __name__ == "__main__":
    events = get_calendar_events(ICLOUD_USERNAME, ICLOUD_APP_PASSWORD)
    emails = get_recent_emails(ICLOUD_USERNAME, ICLOUD_APP_PASSWORD)
    news = get_top_news()
    weather = get_weather(city='Omaha')
    stocks = get_stock_prices(['SPY', 'QQQ', 'AAPL'])

    briefing = generate_briefing(
        events, reminders=[], emails=emails, news=news, stocks=stocks, weather=weather)

    print(briefing)
    # call_with_briefing(briefing)
