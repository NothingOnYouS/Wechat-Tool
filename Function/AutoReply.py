import os
import random
import smtplib
import time
import threading

import itchat

from Function.Mail import Mail
from System import Paths
from WeSys import WeSys


class AutoReply:
    history_message = {}
    check_thread = None
    first_prefix = None
    other_prefix = None
    first_flag = True
    mail_title = 'Wechat %s 的信息'
    modal = ["哇哦，这样嘛？！", "妈耶！", "嘿嘿～。", "啦啦啦~", "噗～", "嘻嘻～", "矮油～"]
    sentences = ["（悄悄记下来通知主人）📝",
                 "折个纸飞机通知主人（咻～）✈️",
                 "（哼哧，哼哧。腿跑断了也要通知到主人）🏃️",
                 "开车通知主人。（嗯，通向幼儿园的车，请刷学生卡）🚌",
                 "开车通知主人。（北京市第三交通委提醒您，喝车不开酒）🚘",
                 "搭高铁通知主人！（chua, chua, chua 好快呦）🚄",
                 "就算搭火箭也要通知到主人！（10, 9, 8, 7, 6,....）🚀",
                 "嘀叭叭，滴叭叭，嘀嘀叭叭，开着快乐家家车，找主人去～🚍",
                 "那个电车好酷哦～搭电车去找主人。(当～当～当～)🚋",
                 "干了这杯酒找主人去。（咕嘟～咕嘟～）🍺",
                 "库洛里多创造的库洛牌啊，请你舍弃旧形象，重新改变，以你的新主人小开开之名命令你，把这个消息送给我主人！（砰～）🎩"]

    @staticmethod
    def text_reply(msg):
        AutoReply.__pre_get_wait_length()
        AutoReply.__pre_get_bot_name()
        AutoReply.__pre_get_contact_method()
        uname = msg.User["RemarkName"] if msg.User["RemarkName"] != "" else msg.User["NickName"]
        uid = msg.User["UserName"]

        if uid not in AutoReply.history_message.keys():
            prefix = AutoReply.first_prefix
            AutoReply.history_message[uid] = {"UNAME": uname, "MESSAGES": []}
            AutoReply.first_flag = True
        else:
            prefix = AutoReply.other_prefix
            AutoReply.first_flag = False
        if float(float(time.time() - WeSys.last_time) / 60) > WeSys.auto_reply_wait_min:
            try:
                mail_content = msg.Content
                mail_title = AutoReply.mail_title % uname
                Mail.send_mail(mail_title, mail_content)
                if AutoReply.first_flag:
                    sentence = AutoReply.sentences[random.randint(0, len(AutoReply.sentences) - 1)]
                    itchat.send(AutoReply.other_prefix + AutoReply.first_prefix + "主人似乎长时间离开微信了，我替他看着微信呢。", uid)
                    if WeSys.auto_reply_contact_method is not None:
                        itchat.send(AutoReply.other_prefix + "唔，你要是急着找主人的话，请直接联系 %s。[Hey]" % WeSys.auto_reply_contact_method, uid)
                    itchat.send(AutoReply.other_prefix + "诶，有消息。" + sentence, uid)
                else:
                    modal = AutoReply.modal[random.randint(0, len(AutoReply.modal)) - 1]
                    sentence = AutoReply.sentences[random.randint(0, len(AutoReply.sentences) - 1)]
                    itchat.send(prefix + modal+sentence, uid)
            except (TypeError, smtplib.SMTPServerDisconnected, smtplib.SMTPAuthenticationError, smtplib.SMTPException):
                if AutoReply.first_flag:
                    itchat.send(AutoReply.first_prefix + "我，我，我，我走丢了，大哭😭。我找不到我主人了。", uid)
                    if WeSys.auto_reply_contact_method is not None:
                        itchat.send(AutoReply.other_prefix + "唔，你要是急着找主人的话，请直接联系 %s。[可怜]" % WeSys.auto_reply_contact_method, uid)
                else:
                    itchat.send(AutoReply.other_prefix + "你直接去找主人好嘛[可怜]，我也找不到主人了。", uid)
        else:
            AutoReply.history_message[uid]["MESSAGES"].append(msg.Content)
            if AutoReply.check_thread is None:
                AutoReply.check_thread = threading.Thread(target=AutoReply.__check_update, args=())
                AutoReply.check_thread.start()

    @staticmethod
    def __pre_get_wait_length():
        if WeSys.auto_reply_wait_min is None:
            with open(os.path.join(Paths.PATH_FULL_SYS_LOCATION, "Config/auto_reply_wait_min"), "r") as file:
                try:
                    WeSys.auto_reply_wait_min = float(file.read())
                    if WeSys.auto_reply_wait_min < 0:
                        WeSys.auto_reply_wait_min = 10
                        itchat.send("自动回复等待时间配置错误，设置默认等待时间10分钟", 'filehelper')
                except (TypeError, FileNotFoundError):
                    WeSys.auto_reply_wait_min = 10
                    itchat.send("自动回复等待时间配置错误，设置默认等待时间10分钟", 'filehelper')

    @staticmethod
    def __pre_get_bot_name():
        if WeSys.auto_reply_boot_name is None:
            with open(os.path.join(Paths.PATH_FULL_SYS_LOCATION, "Config/auto_reply_bot_name"), "r") as file:
                try:
                    WeSys.auto_reply_boot_name = file.read()
                    if WeSys.auto_reply_boot_name == "":
                        WeSys.auto_reply_boot_name = "小机器人"
                except FileNotFoundError:
                    WeSys.auto_reply_boot_name = "小机器人"
                AutoReply.first_prefix = "我是%s，" % WeSys.auto_reply_boot_name
                AutoReply.other_prefix = "(%s)" % WeSys.auto_reply_boot_name

    @staticmethod
    def __check_update():
        while True:
            wait_sec = float(float(time.time() - WeSys.last_time))
            if wait_sec > WeSys.auto_reply_wait_min * 60:
                wait_sec = WeSys.auto_reply_wait_min * 60
            time.sleep(wait_sec + 0.001)
            last_now_len = float(float(time.time() - WeSys.last_time) / 60)
            if last_now_len > WeSys.auto_reply_wait_min:
                if len(AutoReply.history_message) > 0:
                    for uid, uid_dict in AutoReply.history_message.items():
                        content = ""
                        title = AutoReply.mail_title % uid_dict["UNAME"]
                        if len(uid_dict["MESSAGES"]) > 0:
                            itchat.send(AutoReply.other_prefix + AutoReply.first_prefix + "主人似乎长时间离开微信了，我来替他看微信啦！", uid)
                            for message in uid_dict["MESSAGES"]:
                                if content == "":
                                    content += ("%s" % message)
                                else:
                                    content += ("\n%s" % message)
                            try:
                                Mail.send_mail(title, content)
                                sentence = AutoReply.sentences[random.randint(0, len(AutoReply.sentences) - 1)]
                                itchat.send(AutoReply.other_prefix + "唔，你要是急着找主人的话，请直接联系 %s。[Hey]" % WeSys.auto_reply_contact_method, uid)
                                itchat.send(AutoReply.other_prefix + sentence, uid)
                            except (smtplib.SMTPException, smtplib.SMTPServerDisconnected):
                                itchat.send(AutoReply.other_prefix + "我，我，我，我走丢了，大哭😭。我找不到我主人了。", uid)
                                itchat.send(AutoReply.other_prefix + "唔，你要是急着找主人的话，请联系 %s。[可怜]" % WeSys.auto_reply_contact_method, uid)
                            uid_dict["MESSAGES"].clear()


    @staticmethod
    def __pre_get_contact_method():
        if WeSys.auto_reply_contact_method is None:
            with open(os.path.join(Paths.PATH_FULL_SYS_LOCATION, "Config/auto_reply_contact_method"), "r") as file:
                try:
                    WeSys.auto_reply_contact_method = file.read()
                    if WeSys.auto_reply_contact_method == "":
                        WeSys.auto_reply_contact_method = None
                except FileNotFoundError:
                    WeSys.auto_reply_contact_method = None


