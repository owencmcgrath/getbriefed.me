from twilio.rest import Client
from config import TWILIO_SID, TWILIO_TOKEN, TWILIO_NUMBER, YOUR_NUMBER


def call_with_briefing(briefing_text):
    client = Client(TWILIO_SID, TWILIO_TOKEN)

    tts_text = briefing_text.replace('"', '').replace("'", '')

    call = client.calls.create(
        twiml=f'<Response><Say voice="Polly.Kendra">{tts_text}</Say></Response>',
        to=YOUR_NUMBER,
        from_=TWILIO_NUMBER
    )

    print(f"✓ Call initiated: {call.sid}")
    return call.sid
