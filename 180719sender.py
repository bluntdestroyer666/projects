"""import smtplib
 
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login("YOUR EMAIL ADDRESS", "YOUR PASSWORD")
 
msg = "YOUR MESSAGE!"
server.sendmail("YOUR EMAIL ADDRESS", "THE EMAIL ADDRESS TO SEND TO", msg)
server.quit()"""

import smtplib
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

fromaddr = 'pythonoptionsalerts@gmail.com'
toaddr = 'samchakerian@gmail'
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = 'subject' # Put day and options alert type here

body = 'Craft elaborate body here. Sent at ...'
msg.attach(MIMEText(body, 'plain'))

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, '4r3e2w1q5t')

text = msg.as_string()
server.sendmail('pythonoptionsalerts@gmail.com', 'samchakerian@gmail.com', text)
server.quit()