from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from datetime import datetime
from data.calendar import get_calendar_events
from data.email import get_recent_emails
from data.news import get_top_news
from data.stocks import get_stock_prices
from data.weather import get_weather
from ai.summarizer import generate_briefing
from models import db, User, BriefingLog, UserPreferences

app = Flask(__name__)

@app.before_request
def before_request():
    if db.is_closed():
        db.connect()


@app.after_request
def after_request(response):
    if not db.is_closed():
        db.close()
    return response


def filter_upcoming_events(events):
    now = datetime.now()
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
    caller_number = request.form.get('From', '')
    resp = VoiceResponse()

    # Check if caller is a registered user
    try:
        user = User.get(User.phone_number == caller_number)
        
        # User exists, ask for PIN
        gather = Gather(
            input='dtmf',
            num_digits=8,
            action='/verify-pin',
            timeout=30
        )
        gather.say("Please enter your eight digit pin", voice='Polly.Matthew')
        resp.append(gather)
        
        resp.say("No pin entered. Goodbye.", voice='Polly.Matthew')
        resp.hangup()
        
    except User.DoesNotExist:
        # Caller not registered
        resp.say("Phone number not recognized. Please contact support to register.", voice='Polly.Matthew')
        resp.hangup()

    return str(resp)


@app.route("/verify-pin", methods=['POST'])
def verify_pin():
    digits = request.form.get('Digits', '')
    caller_number = request.form.get('From', '')
    resp = VoiceResponse()

    try:
        # Get user by phone number
        user = User.get(User.phone_number == caller_number)
        
        # Verify PIN
        if user.verify_pin(digits):
            # Get user preferences
            prefs = UserPreferences.get_or_none(UserPreferences.user == user)
            if not prefs:
                # Create default preferences if they don't exist
                prefs = UserPreferences.create(user=user)
            
            # Get decrypted iCloud credentials
            icloud_username, icloud_password = user.get_icloud_credentials()
            
            # Generate briefing using user's settings
            events = []
            emails = []
            
            if icloud_username and icloud_password:
                all_events = get_calendar_events(icloud_username, icloud_password)
                events = filter_upcoming_events(all_events)
                
                if prefs.emails_enabled:
                    emails = get_recent_emails(
                        icloud_username, icloud_password, unread_only=True
                    )
            
            news = []
            if prefs.news_enabled:
                news = get_top_news(max_headlines=prefs.max_news_headlines)
            
            stocks = []
            if prefs.stocks_enabled:
                stock_symbols = user.stock_symbols.split(',')
                stocks = get_stock_prices(stock_symbols)
            
            weather = None
            if prefs.weather_enabled:
                weather = get_weather(city=user.city, units=prefs.temperature_unit)
            
            # Generate briefing
            briefing = generate_briefing(
                events,
                reminders=[],
                emails=emails,
                news=news,
                stocks=stocks,
                weather=weather
            )
            
            # Log the briefing
            BriefingLog.create(
                user=user,
                briefing_text=briefing,
                call_sid=request.form.get('CallSid'),
                delivery_method='inbound',
                events_count=len(events),
                emails_count=len(emails)
            )
            
            # Deliver briefing
            resp.say(briefing, voice=prefs.briefing_voice)
            
        else:
            resp.say("Incorrect pin. Call again for another attempt.", voice='Polly.Matthew')
            resp.hangup()
            
    except User.DoesNotExist:
        resp.say("Phone number not recognized.", voice='Polly.Matthew')
        resp.hangup()
    except Exception as e:
        print(f"Error generating briefing: {e}")
        resp.say("Sorry, there was an error generating your briefing. Please try again later.", voice='Polly.Matthew')
        resp.hangup()

    return str(resp)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)