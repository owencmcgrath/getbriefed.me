from data.calendar import get_calendar_events
from ai.summarizer import generate_briefing
from data.email import get_recent_emails
from output.voice import call_with_briefing
from data.news import get_top_news
from data.stocks import get_stock_prices
from data.weather import get_weather
from models import db, User, BriefingLog, UserPreferences

import os


def generate_and_deliver_briefing(user_id=None, phone_number=None):
    """
    Generate and deliver briefing for a user
    Specify either user_id or phone_number
    """

    # Connect to database
    db.connect()

    try:
        # Get user
        if user_id:
            user = User.get_by_id(user_id)
        elif phone_number:
            user = User.get(User.phone_number == phone_number)
        else:
            raise ValueError("Must specify either user_id or phone_number")

        # Check if user is active
        if not user.is_active:
            print(f"User {user.phone_number} is inactive, skipping")
            return

        # Get user preferences
        prefs = UserPreferences.get_or_none(UserPreferences.user == user)
        if not prefs:
            prefs = UserPreferences.create(user=user)

        # Get decrypted credentials
        icloud_username, icloud_password = user.get_icloud_credentials()

        # Gather data based on user preferences
        events = []
        emails = []

        if icloud_username and icloud_password:
            events = get_calendar_events(icloud_username, icloud_password)

            if prefs.emails_enabled:
                emails = get_recent_emails(icloud_username, icloud_password)

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

        # Make the call
        call_sid = call_with_briefing(briefing, user.phone_number)

        # Log the briefing
        BriefingLog.create(
            user=user,
            briefing_text=briefing,
            call_sid=call_sid,
            delivery_method='outbound',
            events_count=len(events),
            emails_count=len(emails)
        )

        print(f"✓ Briefing delivered to {user.phone_number}")

    except User.DoesNotExist:
        print(f"User not found")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


def deliver_all_active_briefings():
    """
    Deliver briefings to all active users
    Use this for scheduled morning briefings
    """
    db.connect()

    try:
        active_users = User.select().where(User.is_active == True)

        print(f"Delivering briefings to {len(active_users)} active user(s)...")

        for user in active_users:
            try:
                generate_and_deliver_briefing(user_id=user.id)
            except Exception as e:
                print(
                    f"Failed to deliver briefing to {user.phone_number}: {e}")
                continue

        print("✓ All briefings delivered")

    finally:
        db.close()


if __name__ == "__main__":
    # For manual testing, specify your phone number
    YOUR_NUMBER = os.getenv('YOUR_NUMBER')

    if YOUR_NUMBER:
        generate_and_deliver_briefing(phone_number=YOUR_NUMBER)
    else:
        # Or deliver to all active users
        deliver_all_active_briefings()
