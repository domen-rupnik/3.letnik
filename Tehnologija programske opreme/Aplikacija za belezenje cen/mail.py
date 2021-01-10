import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_mail(email_naslov, zadeva, sporocilo):

    email_TPO = "tpo@ski-javornik.si"
    email_TPO_geslo = "9245yT65PJ5YRU6w"

    msg = MIMEMultipart()
    msg['From'] = email_TPO
    msg['To'] = email_naslov
    msg['Subject'] = zadeva
    msg.attach(MIMEText(sporocilo, 'plain'))

    try:
        server = smtplib.SMTP('mail.ski-javornik.si: 587')
        server.starttls()
        server.login(email_TPO, email_TPO_geslo)
        server.sendmail(email_TPO, email_naslov, msg.as_string())
        server.quit()

    except Exception as e:
        a = 0