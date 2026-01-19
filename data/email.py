import imaplib
import email
from datetime import datetime, timedelta


def get_recent_emails(username, password, hours=24, unread_only=False):
    try:
        mail = imaplib.IMAP4_SSL("imap.mail.me.com")
        mail.login(username, password)
        mail.select("inbox")

        # Build search criteria
        if unread_only:
            search_criteria = 'UNSEEN'
        else:
            date = (datetime.now() - timedelta(hours=hours)
                    ).strftime("%d-%b-%Y")
            search_criteria = f'(SINCE {date})'

        _, messages = mail.search(None, search_criteria)

        if not messages[0]:
            return []

        email_ids = messages[0].split()
        recent_emails = []

        # Get last 10 emails
        for email_id in email_ids[-10:]:
            try:
                _, msg_data = mail.fetch(email_id, '(BODY.PEEK[])')

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        subject = str(msg.get("Subject", "(No subject)"))
                        from_ = str(msg.get("From", "Unknown"))

                        recent_emails.append({
                            'from': from_,
                            'subject': subject
                        })
                        break

            except Exception as e:
                continue

        mail.close()
        mail.logout()
        return recent_emails

    except Exception as e:
        print(f"Email error: {e}")
        return []
