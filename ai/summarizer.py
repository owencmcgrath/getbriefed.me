import anthropic
from config import ANTHROPIC_API_KEY
from datetime import datetime


def generate_briefing(events, reminders, emails=None, news=None, stocks=None, weather=None):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    context = f"""Generate a 45-60 second voice briefing for Owen.

Today: {datetime.now().strftime('%A, %B %d')}

Schedule ({len(events)} events):
"""

    for event in events:
        location = f" at {event['location']}" if event['location'] else ""
        context += f"- {event['time']}: {event['title']}{location}\n"

    if reminders:
        context += f"\nReminders ({len(reminders)}):\n"
        for reminder in reminders:
            due = f" (due {reminder['due']})" if reminder['due'] else ""
            context += f"- {reminder['title']}{due}\n"

    if emails:
        context += f"\nRecent Emails ({len(emails)}):\n"
        for email in emails:
            context += f"- {email['from']}: {email['subject']}\n"

    if news:
        context += f"\nTop Headlines ({len(news)}):\n"
        for headline in news:
            context += f"- {headline}\n"

    if stocks:
        context += f"\nMarket Update:\n"
        for stock in stocks:
            context += f"- {stock['symbol']}: {stock['price']} ({stock['change']})\n"

    if weather:
        context += f"\nWeather in {weather['city']}:\n"
        context += f"- Current: {weather['temp']}, Feels like: {weather['feels_like']}\n"
        context += f"- High: {weather['high']}, Low: {weather['low']}\n"
        context += f"- Conditions: {weather['conditions']}\n"

    context += """
Voice Guidelines:
- Conversational, direct tone (speaking to Owen, not writing for him)
- NO headers, bullets, or formatting—continuous prose only
- Group events by location to minimize context switching
- Flag tight transitions (<30 min between events at different locations)
- Estimate total commute time if multiple location changes
- Skip routine items (morning routine, breakfast, wind down) unless time-critical
- Mention notable emails briefly (just sender + topic)
- Summarize news in 1-2 sentences total, not headline by headline
- For stocks: just say "markets are up/down" with key movers if significant (>2% change)
- For weather: mention temp and conditions naturally ("it's 45 and cloudy"), flag extreme conditions
- Prioritize: work commitments > classes > personal tasks
- Target 45-60 seconds when read aloud
- End with brief actionable takeaway or heads-up
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": context}]
    )

    return response.content[0].text
