import smtplib
from email.mime.text import MIMEText

# tryagain=True

def sendEmail(receiver, content):
    mail_host = 'smtp.163.com'
    mail_user = 'blcu_access_system'
    mail_pass = 'NYVBABPKROUMRMMO'
    sender = 'blcu_access_system@163.com'

    message = MIMEText(content, 'plain', 'utf-8')
    message['Subject'] = '系统通知'
    message['From'] = sender
    message['To'] = receiver

    try:
        smtpObj = smtplib.SMTP(mail_host)
        # 如果需要，使用STARTTLS
        # smtpObj.starttls()
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receiver, message.as_string())
        smtpObj.quit()
        return 'success'
    except smtplib.SMTPException as e:
        return 'error', e

import atexit

def sendEmalibeforeExit(to_who,content):
    # 保存数据的逻辑
    sendEmail(to_who,content)
    # print("正在保存数据...")