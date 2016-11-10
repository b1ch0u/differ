# coding: utf8

import os.path

import smtplib
from email.mime.text import MIMEText

import pyPdf
import urllib2

from StringIO import StringIO

BASE_FILENAME = '/home/sebastien/prez_python/differ/'

msg = ('Bonjour {first},\n'
       '\n'
       'Il semble que ton emploi du temps vient d\'être modifié.\n'
       'Pour rappel, tu le trouveras ici : {url}\n'
       '\n'
       'Force et honneur.')

generic_url = 'https://etu.math.upmc.fr/math/planning.php?type=Personne&valeur={login}&periode=2016%2D2017%20P%E9riode%201&/planning.pdf'

def getPDFContent(o):
    content = ""
    # Load PDF into pyPDF
    pdf = pyPdf.PdfFileReader(o)
    # Iterate pages
    for i in range(0, pdf.getNumPages()):
        # Extract text from page and add to content
        page_content = pdf.getPage(i).extractText().encode('utf-8').strip()[142:-35]
        #print (page_content)
        content += page_content + "\n"
    # Collapse whitespace
    #content = " ".join(content.replace("\xa0", " ").strip().split())
    return content

def get_user_calendar(login):
    req = urllib2.urlopen(generic_url.format(login=login))
    s = req.read()
    io = StringIO(s)
    text = getPDFContent(io)
    #with open('tmp.pdf', 'w') as f:
        #f.write(s)
    return text

class User:
    def __init__(self, first, login, mail, getter, notifier):
        self.first = first
        self.login = login
        self.mail = mail
        self.getter = getter
        self.notifier = notifier
        self.log_filename = BASE_FILENAME + login + '.txt'
        if os.path.isfile(self.log_filename):
            with open(self.log_filename, 'r') as f:
                self.doc = f.read()
            print ('found file')
        else:
            self._fetch_file_content()
            with open(self.log_filename, 'w') as f:
                f.write(self.doc)

    def _fetch_file_content(self):
        print ('fetching ...')
        self.doc = self.getter(self.login)
        print ('... done')

    def check_if_updated(self):
        up_to_date_doc = self.getter(self.login)
        if up_to_date_doc != self.doc:
            print ('found a difference, sending mail')
            self.notifier(self.mail, msg.format(first=self.first, url=generic_url.format(login=self.login)))
            self.doc = up_to_date_doc
            with open(self.log_filename, 'w') as f:
                f.write(up_to_date_doc)

def send_notification_mail(recipient_address, msg):
    msg = MIMEText(msg, 'plain', 'utf-8')
    sender_address = 'no-reply@jdlm.tech'
    msg['Subject'] = '[DIFFER] Ton emploi du temps a été modifié'
    msg['From'] = sender_address
    msg['To'] = recipient_address

    server = smtplib.SMTP('smtp.jdlm.tech')
    server.login('sebastien@jdlm.tech', '')
    server.sendmail(sender_address, [recipient_address], msg.as_string())
    server.quit()

seb = User('Sébastien', '3404838', 'sebastien@jdlm.tech', get_user_calendar, send_notification_mail)
seb.check_if_updated()
