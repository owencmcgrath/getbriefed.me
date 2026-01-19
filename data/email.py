import imaplib
import email


def get_recent_emails(username, password, hours=24):
    try:
        mail = imaplib.IMAP4_SSL("imap.mail.me.com")
        mail.login(username, password)
        mail.select("inbox")

        _, messages = mail.search(None, 'ALL')

        if not messages[0]:
            return []

        email_ids = messages[0].split()
        recent_emails = []

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
                print(f"Error: {e}")
                continue

        mail.close()
        mail.logout()
        return recent_emails

    except Exception as e:
        print(f"Email error: {e}")
        return []
