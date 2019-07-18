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
    first_prefix = "我是小小开，"
    other_prefix = "(小小开)"
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
                 "干了这杯酒找主人去。（咕嘟～咕嘟～）🍺"]

    @staticmethod
    def text_reply(msg):
        AutoReply.__pre_get_wait_length()
        uname = msg.User["RemarkName"] if msg.User["RemarkName"] != "" else msg.User["NickName"]
        uid = msg.User["UserName"]
        if float(float(time.time() - WeSys.last_time) / 60) > WeSys.auto_reply_wait_min:
            first_flag = True
            if uid not in AutoReply.history_message.keys():
                prefix = AutoReply.first_prefix
                AutoReply.history_message[uid] = {"UNAME": uname, "MESSAGES": [msg.Content]}
            else:
                prefix = AutoReply.other_prefix
                first_flag = False
            try:
                mail_content = msg.Content
                mail_title = AutoReply.mail_title % uname
                Mail.send_mail(mail_title, mail_content)
                if first_flag:
                    sentence = AutoReply.sentences[random.randint(0, len(AutoReply.sentences) - 1)]
                    itchat.send(AutoReply.other_prefix + AutoReply.first_prefix + "主人似乎长时间离开微信了，我替他看着微信呢。", uid)
                    itchat.send(AutoReply.other_prefix + "唔，你要是急着找主人的话，请电话直接联系+8615900668803。[Hey]", uid)
                    itchat.send(AutoReply.other_prefix + "诶，有消息。" + sentence, uid)
                else:
                    modal = AutoReply.modal[random.randint(0, len(AutoReply.modal)) - 1]
                    sentence = AutoReply.sentences[random.randint(0, len(AutoReply.sentences) - 1)]
                    itchat.send(prefix + modal+sentence, uid)
            except (TypeError, smtplib.SMTPServerDisconnected):
                itchat.send(AutoReply.first_prefix + "我，我，我，我走丢了，大哭😭。我找不到我主人了。", uid)
                return (AutoReply.other_prefix + "唔，你要是急着找主人的话，请电话直接联系+8615900668803。[可怜]").format(msg['Text'])
        else:
            if uid not in AutoReply.history_message.keys():
                AutoReply.history_message[uid] = {"UNAME": uname, "MESSAGES": [msg.Content]}
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
                except:
                    WeSys.auto_reply_wait_min = 10

    @staticmethod
    def __check_update():
        while True:
            wait_sec = float(float(time.time() - WeSys.last_time))
            a = WeSys.auto_reply_wait_min * 60
            if wait_sec > WeSys.auto_reply_wait_min * 60:
                wait_sec = WeSys.auto_reply_wait_min * 60
            time.sleep(wait_sec + 1)
            last_now_len = float(float(time.time() - WeSys.last_time) / 60)
            a = AutoReply.history_message
            if last_now_len > WeSys.auto_reply_wait_min:
                if len(AutoReply.history_message) > 0:
                    for uid, uid_dict in AutoReply.history_message.items():
                        if len(uid_dict["MESSAGES"]) > 0:
                            try:
                                title = AutoReply.mail_title % uid_dict["UNAME"]
                                content = ""
                                for message in uid_dict["MESSAGES"]:
                                    if content == "":
                                        content += ("%s" % message)
                                    else:
                                        content += ("\n%s" % message)
                                Mail.send_mail(title, content)
                                sentence = AutoReply.sentences[random.randint(0, len(AutoReply.sentences) - 1)]
                                itchat.send(AutoReply.other_prefix + AutoReply.first_prefix + "主人似乎长时间离开微信了，我来替他看微信啦！", uid)
                                itchat.send(AutoReply.other_prefix + "唔，你要是急着找主人的话，请电话直接联系+8615900668803。[Hey]", uid)
                                itchat.send(AutoReply.other_prefix + sentence, uid)
                            except itchat:
                                itchat.send(AutoReply.first_prefix + "我，我，我，我走丢了，大哭😭。我找不到我主人了。", uid)
                                itchat.send(AutoReply.other_prefix + "唔，你要是急着找主人的话，请电话直接联系+8615900668803。[可怜]", uid)
                            uid_dict["MESSAGES"].clear()
            else:
                AutoReply.history_message = {}
