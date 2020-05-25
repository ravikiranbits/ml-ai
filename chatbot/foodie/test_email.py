from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_core.actions.action import Action
from rasa_core.events import SlotSet
from rasa_core.events import Restarted
from collections import OrderedDict
import zomatopy
import json
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import pandas as pd

gmail_user = 'd72a4dc62a4e46'  #typr your email id here
gmail_password = '178cf7dddd8f0f' #typr your password here
sent_from = gmail_user  
to = str(gmail_user)
msg = MIMEMultipart('alternative')
msg['Subject'] = "Restaurant Details"
msg['From'] = gmail_user
msg['To'] = to
html = "<html><body>Hello</body></html>"
part2 = MIMEText(html, 'html')
msg.attach(part2)
server = smtplib.SMTP('smtp.mailtrap.io',2525)
server.ehlo()
server.login(gmail_user, gmail_password)
server.sendmail(sent_from, to, msg.as_string())
server.close()