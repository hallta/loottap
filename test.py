

import smtplib
import os
from email.mime.text import MIMEText

s="email subject"
body="this is the body"
sender="hallta@lgmail.com"
to=["hallta@gmail.com"]
pwd=os.environ['GMAIL_PASS']

msg = MIMEText(body)
msg['Subject'] = s
msg['From'] = sender
msg['To'] = ", ".join(to)

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
    smtp_server.login(sender, pwd)
    smtp_server.sendmail(sender, to, msg.as_string())

print("Sent!")