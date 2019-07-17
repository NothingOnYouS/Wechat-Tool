import os
from email.header import Header
from email.mime.text import MIMEText
from smtplib import SMTP_SSL

from System import Paths


class Mail:
    @staticmethod
    def send_mail(mail_title, mail_content):
        with open(os.path.join(Paths.PATH_FULL_SYS_LOCATION, "smtp"), "r") as file:
            smtp_server = file.read()
        with open(os.path.join(Paths.PATH_FULL_SYS_LOCATION, "password"), "r") as file:
            pwd = file.read()
        with open(os.path.join(Paths.PATH_FULL_SYS_LOCATION, "sender"), "r") as file:
            sender = file.read()
        with open(os.path.join(Paths.PATH_FULL_SYS_LOCATION, "receiver", "r")) as file:
            receiver = file.read()

        # ssl登录
        smtp = SMTP_SSL(smtp_server)
        smtp.ehlo(smtp_server)
        smtp.login(sender, pwd)

        msg = MIMEText(mail_content, "plain", 'utf-8')
        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = sender
        msg["To"] = receiver
        smtp.sendmail(sender, receiver, msg.as_string())
        smtp.quit()
