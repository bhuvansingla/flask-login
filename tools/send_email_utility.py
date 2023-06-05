import smtplib

AUTO_MAIL = 'noreply.teamlabomba@gmail.com'
APP_PASSWORD = "wydydghyesmfahwq"
def send_email_utility(subject,message,sender_email,recipient_email):
    # connect to SMTP server
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        
        # log in to SMTP server
        smtp.login(AUTO_MAIL, APP_PASSWORD)

        
        # create email message
        email_message = f'Subject: {subject}\n\n{message}'
        
        # send email
        smtp.sendmail(sender_email, recipient_email, email_message)
   