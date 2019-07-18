import time

import itchat

from Function.AutoReply import AutoReply
from Function.Mail import Mail
from WeSys import WeSys


# 用于自动回复，封装好的装饰器，当接收到的消息是Text，即文字消息
@itchat.msg_register('Text')
def text_reply(msg):
    if WeSys.my_uid == msg.FromUserName:
        WeSys.last_time = float(time.time())
        if msg.ToUserName == "filehelper":
            if WeSys.fh_func is not None:
                WeSys.fh_continue_previous_task(msg)
            else:
                argv = WeSys.fh_check_task(msg)
                task = argv.pop()
                if task == "群发":
                    WeSys.fh_start_new_task(task, argv)
        else:
            if msg.ToUserName in AutoReply.history_message.keys():
                AutoReply.history_message[msg.ToUserName]["MESSAGES"].clear()
    else:
        AutoReply.text_reply(msg)


if __name__ == '__main__':
    try:
        # enable cmd qr参数是用于在命令行上生成二维码，用于linux服务器
        while True:
            try:
                screen = int(input("你的控制台是什么颜色呢？黑色请输入1，白色请输入2\n"))
                if screen in [1, 2]:
                    if screen == 1:
                        qr_in = 2
                    else:
                        qr_in = -2
                    break
            except TypeError:
                print("输入错误")
        itchat.auto_login(enableCmdQR = qr_in)
        WeSys.my_uid = itchat.get_friends(update=True)[0]["UserName"]
        Mail.check_mail_server()
        itchat.run(debug=True)
        a = itchat.get_friends(update=True)[0]
    except itchat:
        Mail.send_mail("Wechat看守系统消息", "你家炸了！")
