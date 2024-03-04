import smtplib, ssl
from email.message import EmailMessage

def send_message(email_configuration, subject, message):
    try:
        msg = EmailMessage()
        msg.set_content(message)

        msg['Subject'] = subject
        msg['From'] = email_configuration['sender_email']
        msg['To'] = email_configuration['receiver_email']
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(email_configuration['smtp_server'], email_configuration['port'], context=context) as server:
            server.login(email_configuration['sender_email'], email_configuration['password'])
            server.send_message(msg)
    except Exception:
        print('Could not send email message')