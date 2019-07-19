import time

from Function.Broadcasting import Broadcasting


class WeSys:
    my_uid = None
    last_time = time.time()

    fh_obj = None
    fh_func = None
    fh_start_dict = {"群发": {"fhobj": Broadcasting, "fh_func": "broadcasting_prepare"}}
    fh_funct_dict = {"broadcasting_prepare": {"TRUE": "broadcasting_confirm", "CONTINUE": None, "FALSE": None},
                     "broadcasting_confirm": {"TRUE": None, "CONTINUE": "broadcasting_confirm", "FALSE": None}}

    auto_reply_wait_min = None
    auto_reply_boot_name = None
    auto_reply_contact_method = None

    @staticmethod
    def fh_start_new_task(task, argv):
        WeSys.fh_obj = WeSys.fh_start_dict[task]["fhobj"]()
        WeSys.fh_func = getattr(WeSys.fh_obj, WeSys.fh_start_dict[task]["fh_func"])
        WeSys.fh_continue_previous_task(argv)

    @staticmethod
    def fh_continue_previous_task(argv):
        try:
            result = WeSys.fh_func(argv)
        except Exception:
            result = "FALSE"
        c_method_name = WeSys.fh_funct_dict[WeSys.fh_func.__name__][result]
        if c_method_name is not None:
            WeSys.fh_func = getattr(WeSys.fh_obj, WeSys.fh_funct_dict[WeSys.fh_func.__name__][result])
        else:
            WeSys.fh_func = None
            WeSys.fh_obj = None

    @staticmethod
    def fh_check_task(msg):
        content_list = msg.Content.split("|")
        content_list.reverse()
        return content_list
