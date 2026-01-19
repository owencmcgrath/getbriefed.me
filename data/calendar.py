from caldav import DAVClient
from datetime import datetime, timedelta
import requests


def get_calendar_events(username, password):
    session = requests.Session()
    session.timeout = 10 

    client = DAVClient(
        url="https://caldav.icloud.com",
        username=username,
        password=password
    )
    client.session = session

    principal = client.principal()
    calendars = principal.calendars()

    now = datetime.now()
    start = datetime(now.year, now.month, now.day, 0, 0, 0)
    end = start + timedelta(days=1)

    events = []
    for calendar in calendars:
        try:
            results = calendar.date_search(start=start, end=end)
            for event in results:
                event_data = event.vobject_instance.vevent
                events.append({
                    'time': event_data.dtstart.value.strftime('%I:%M %p'),
                    'title': str(event_data.summary.value),
                    'location': str(event_data.location.value) if hasattr(event_data, 'location') else ''
                })
        except Exception as e:
            print(f"Error fetching calendar {calendar.name}: {e}")
            continue

    return sorted(events, key=lambda x: x['time'])
