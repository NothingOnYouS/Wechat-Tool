import itchat
import time
import requests

myUserName = None
last_update_time = None


def send_notification(user_nick_name, text):
    from email.mime.text import MIMEText
    from email.header import Header
    from smtplib import SMTP_SSL
    # qq邮箱smtp服务器
    host_server = 'smtp.exmail.qq.com'
    # pwd为qq邮箱的授权码
    with open("./password", "r") as file:
        pwd = file.read()
    # 发件人的邮箱
    with open("./sender", "r") as file:
        sender = file.read()
    # 收件人邮箱
    with open("./receiver", "r") as file:
        receiver = file.read()
    # 邮件的正文内容
    mail_content = text
    # 邮件标题
    mail_title = 'Wechat %s的信息' % user_nick_name

    # ssl登录
    smtp = SMTP_SSL(host_server)
    smtp.ehlo(host_server)
    smtp.login(sender, pwd)

    msg = MIMEText(mail_content, "plain", 'utf-8')
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender
    msg["To"] = receiver
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()


# 用于自动回复，封装好的装饰器，当接收到的消息是Text，即文字消息
@itchat.msg_register('Text')
def text_reply(msg):
    global last_update_time
    if myUserName == msg.FromUserName:
        last_update_time = time.time()
    else:
        if last_update_time is None or float(float(last_update_time) / 60) / 60 > 10:
            try:
                nick_name = msg.User["NickName"]
                content = msg.Content
                send_notification(nick_name, content)
                return "我是小小开，主人现在看不了微信，我替主人看管微信。你的信息我已经通过邮件通知他了。也可以直接电联+8615900668803。[Hey]".format(msg['Text'])
            except:
                return "我是小小开，邮件系统坏了，我也没法找到他了😞。或许你可以尝试邮箱mail@kai.sh直接联系他。".format(msg['Text'])


if __name__ == '__main__':
    try:
        # enable cmd qr参数是用于在命令行上生成二维码，用于linux服务器
        itchat.auto_login(enableCmdQR=-2)
        myUserName = itchat.get_friends(update=True)[0]["UserName"]
        itchat.run(debug=True)
    except:
        send_notification("System", "你家炸了！")
