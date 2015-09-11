#! /usr/bin/env python
# coding: utf-8
__author__ = 'ZhouHeng'

from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import thread
from datetime import datetime
from My_PC import pc_info


class MyEmailManager:
    def __init__(self):
        self.m_user = "zhouheng615"
        self.m_password = "msg245"
        self.email_server = "163.com"
        self.sender = "晶云平台"
        self.developer_emails = ["zhou5315938@163.com", "15136519943@163.com"]

    def encoded(self, s, encoding):
        return s.encode(encoding) if isinstance(s, unicode) else s

    def send_mail(self, to, sub, content):
        try:
            encoding = 'utf-8'
            SMTP = smtplib.SMTP
            smtp = SMTP("smtp.%s" % self.email_server, 25)
            # smtp.set_debuglevel(True)
            user = "%s@%s" % (self.m_user, self.email_server)
            smtp.starttls()
            smtp.login(user, self.m_password)
            user = self.encoded(user, encoding)
            user = '{nick_name} <{user}>'.format(nick_name=self.encoded(self.sender, encoding), user=user)
            msg = MIMEMultipart('alternative')
            msg['From'] = user
            msg['To'] = self.encoded(to, encoding)
            msg['Subject'] = Header(self.encoded(sub, encoding), encoding)
            msg.attach(MIMEText(self.encoded(content, encoding), "html", encoding))
            smtp.sendmail(user, to, msg.as_string())
            smtp.quit()
            return True
        except Exception, e:
            print(e)
            return False

    def send_mail_thread(self, to, sub, content):
        return thread.start_new_thread(self.send_mail, (to, sub, content))

    def send_success(self, email):
        try:
            html_read = open('../Web2/templates/Email/Apply_Success.html', 'r')
            content = html_read.read()
            return self.send_mail(email, "晶云 精准医疗平台", content)
        except Exception, e:
            print(e)
            return False

    def send_system_exp(self, api_url, request_data, error_message, developer):
        try:
            content = "api_url: %s" % api_url
            content += "<br>request_data: %s" % request_data
            content += "<br>error message: %s" % error_message
            content += "<br>service info: %s" % pc_info
            content += "<br>Now is: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            developer_email = ""
            if developer < len(self.developer_emails):
                developer_email = self.developer_emails[0]
                self.send_mail_thread(developer_email, "晶云平台系统异常提醒", content)
                return True
            return False
        except Exception, e:
            print(e.args)
            return False
