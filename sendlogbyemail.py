# -*- coding: utf-8 -*-
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))

class EmailSender(object):

	def __init__(self, fa, pw, ta, ss):
		self.from_addr = fa
		self.password = pw
		self.to_addr = ta
		self.smtp_server = ss

	def packPlainText(self, bodytext, fr = '', to = '', subj = ''):
		self.__msg = MIMEText(bodytext, 'plain', 'utf-8')
		self.__msg['From'] = _format_addr(fr)
		self.__msg['To'] = _format_addr(to)
		self.__msg['Subject'] = Header(subj, 'utf-8').encode()

	def send(self):
		server = smtplib.SMTP(self.smtp_server, 25)
		server.set_debuglevel(1)
		server.login(self.from_addr, self.password)
		server.sendmail(self.from_addr, [self.to_addr], self.__msg.as_string())
		server.quit()

if (__name__ == '__main__'):
	testsender = EmailSender('senderemail', 'senderpw', 'receiveremail', 'smtp.163.com')
	testsender.packPlainText('Hello World!', 'happy_pycoder', 'happy_c++coder', 'Hello')
	testsender.send()