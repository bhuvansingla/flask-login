import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

AUTO_MAIL = 'noreply.teamlabomba@gmail.com'
APP_PASSWORD = "wydydghyesmfahwq"

def send_email_utility(subject, message, sender_email, recipient_email_list):
    if isinstance(recipient_email_list, list):
        recipient_email = ', '.join(recipient_email_list) #convert to comma separated string if there is a list, otherwise
        #simple string
    else:
        recipient_email = recipient_email_list
        
    # Create a MIMEText object
    email_message = MIMEText(message, 'plain', 'utf-8')
    email_message['Subject'] = subject
    email_message['From'] = formataddr((AUTO_MAIL, sender_email))
    email_message['To'] = recipient_email

    # Connect to SMTP server
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        # Log in to SMTP server
        smtp.login(AUTO_MAIL, APP_PASSWORD)

        # Send the email
        smtp.send_message(email_message)
