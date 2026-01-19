from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from datetime import datetime
from data.calendar import get_calendar_events
from data.email import get_recent_emails
from data.news import get_top_news
from data.stocks import get_stock_prices
from data.weather import get_weather
from ai.summarizer import generate_briefing
from config import ICLOUD_USERNAME, ICLOUD_APP_PASSWORD

app = Flask(__name__)


def filter_upcoming_events(events):
    now = datetime.now()
    current_time = now.strftime('%I:%M %p')

    upcoming = []
    for event in events:
        event_time = datetime.strptime(event['time'], '%I:%M %p').replace(
            year=now.year, month=now.month, day=now.day
        )
        if event_time >= now:
            upcoming.append(event)

    return upcoming


@app.route("/incoming-call", methods=['POST'])
def handle_incoming_call():
    caller = request.form['From']

    # Generate briefing
    all_events = get_calendar_events(ICLOUD_USERNAME, ICLOUD_APP_PASSWORD)
    upcoming_events = filter_upcoming_events(all_events)

    emails = get_recent_emails(ICLOUD_USERNAME, ICLOUD_APP_PASSWORD, unread_only=True)
    news = get_top_news(max_headlines=3)
    stocks = get_stock_prices(['SPY', 'QQQ', 'AAPL'])
    weather = get_weather(city='Omaha')

    briefing = generate_briefing(
        upcoming_events,
        reminders=[],
        emails=emails,
        news=news,
        stocks=stocks,
        weather=weather
    )

    resp = VoiceResponse()
    resp.say(briefing, voice='Polly.Matthew')

    return str(resp)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
