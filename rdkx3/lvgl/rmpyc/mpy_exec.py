import unats as nats
import io
import sys

import lv_pm
pm = lv_pm.pm()

import cmodule
import re
import json

def get_wlan0info():
    essid, signal_level = "", ""
    rt = cmodule.rpopen("iwconfig wlan0")
    try:
        tmp = rt.split("\n")
        if "unassociated" in tmp[0]:
            return False
        essid_pattern = r'ESSID:"(.*?)"'
        match = re.search(essid_pattern, tmp[0])
        if match:
            essid = match.group(1)

        signal_level_pattern = r'Signal level=(\d+)/100'
        match = re.search(signal_level_pattern, tmp[6])
    except:
        return False

    if match:
        signal_level = match.group(1)

    rt = cmodule.rpopen("ip -4 addr show wlan0 | grep 'inet' | awk '{print $2}' | cut -d/ -f1")
    ipaddr = rt[:-1]
    return [essid, signal_level, ipaddr] if all([essid, signal_level, ipaddr]) else False

class ioexec(io.IOBase):
    def __init__(self):
        self.nc = nats.connect("127.0.0.1")
        self.sub = self.nc.subscribe(b"mpy.repl.input")
        self.sub = self.nc.subscribe(b"modbus.battery.collection")
        self.sub = self.nc.subscribe(b"modbus.lvgl_layer.collection") # nats控制lvgl图层运动
        self.datalis = []

    def write(self, buf):
        self.nc.publish(b"mpy.repl.output", buf)
        return len(bytes(buf))

    def public_msg(self, buf):
        self.nc.publish(b"mpy.repl.callback", buf)
        return len(bytes(buf))

    def read(self, n):
        return self.sub.next_msg().__next__()
    
natsio = ioexec()

pm.remote_msg = natsio.public_msg

def exec_print(*args, **kwargs):
    
    flags = ['>', '<', 'object', 'at', '0x']
    args_repr = [repr(a) for a in args if any(
        f not in repr(a) for f in flags)]
    kwargs_repr = [f"{k}={repr(v)}" if not callable(
        v) else f"{k}={v.__name__}" for k, v in kwargs.items()]
    signature = ", ".join(args_repr + kwargs_repr)
    natsio.write(signature.encode())

import micropython
def mpy_exec(data):
    global print
    tmp = print
    print = exec_print
    exec(data, globals(), globals())
    print = tmp
    natsio.write(b'>>> ')
    
while True:
    result = natsio.read(None)
    tmp = result.data

    
    if result.subject == b'mpy.repl.input':
        try:
            micropython.schedule(mpy_exec, tmp)
            pm.reload_counter()
        except Exception as e:
            # sys.print_exception(e, natsio)
            natsio.write(str(sys.exc_info()).encode())
    if result.subject == b"modbus.battery.collection":
        if pm.show_obj[1] in ("gif", "express"):
            continue
        data = json.loads(tmp.decode())
        # print(data)
        b = data.get("remaining_power_percentage")
        battery = int(b // 25.1)
        wlan0info = get_wlan0info()
        if wlan0info:
            essid, signal_level, ipaddr = wlan0info
            signal_level = int(int(signal_level) // 25.1)
            micropython.schedule(lambda val: pm.updata_info(signal_level, battery, ipaddr), None)
        else:
            micropython.schedule(lambda val: pm.updata_info(0, battery, ""), None)

    # # 获取lvgl各图层的pos、scale、rot数据
    # if result.subject == b"modbus.lvgl_layer.collection":
    #     data = json.loads(tmp.decode())

    #     # 获取各图层的数据
    #     eye_iris_ = data.get("eye_iris", 0)
    #     eye_pupil_ = data.get("eye_pupil", 0)
    #     eye_upper_ = data.get("eye_upper", 0)
    #     eye_lower_ = data.get("eye_lower", 0)

    #     # print("eye_iris:", eye_iris_)
    #     # print("eye_pupil:", eye_pupil_)
    #     # print("eye_upper:", eye_upper_)
    #     # print("eye_lower:", eye_lower_)

    #     eye_iris_pos_y = eye_iris_["pos_y"]
    #     eye_iris_pos_z = eye_iris_["pos_z"]
    #     eye_iris_rot_x = eye_iris_["rot_x"]
    #     eye_iris_scale_y = eye_iris_["scale_y"]
    #     eye_iris_scale_z = eye_iris_["scale_z"]
    #     # print("eye_iris:", eye_iris_pos_y, eye_iris_pos_z, eye_iris_rot_x, eye_iris_scale_y, eye_iris_scale_z)

    #     eye_pupil_pos_y = eye_pupil_["pos_y"]
    #     eye_pupil_pos_z = eye_pupil_["pos_z"]
    #     eye_pupil_rot_x = eye_pupil_["rot_x"]
    #     eye_pupil_scale_y = eye_pupil_["scale_y"]
    #     eye_pupil_scale_z = eye_pupil_["scale_z"]
    #     # print("eye_pupil:", eye_pupil_pos_y, eye_pupil_pos_z, eye_pupil_rot_x, eye_pupil_scale_y, eye_pupil_scale_z)

    #     eye_upper_pos_z = eye_upper_["pos_z"]
    #     eye_upper_scale_z = eye_upper_["scale_z"]
    #     # print("eye_upper:", eye_upper_pos_z, eye_upper_scale_z)

    #     eye_lower_pos_z = eye_lower_["pos_z"]
    #     eye_lower_scale_z = eye_lower_["scale_z"]
    #     # print("eye_lower:", eye_lower_pos_z, eye_lower_scale_z)


    #     # get data
    #     layer_data["eye_iris_pos_y"] = int(eye_iris_pos_y * 10000)
    #     layer_data["eye_iris_pos_z"] = int(eye_iris_pos_z * 10000)
    #     layer_data["eye_iris_rot_x"] = eye_iris_rot_x
    #     layer_data["eye_iris_scale_y"] = eye_iris_scale_y
    #     layer_data["eye_iris_scale_z"] = eye_iris_scale_z
        
    #     layer_data["eye_pupil_pos_y"] = int(eye_pupil_pos_y * 10000)
    #     layer_data["eye_pupil_pos_z"] = int(eye_pupil_pos_z * 10000)
    #     layer_data["eye_pupil_rot_x"] = eye_pupil_rot_x
    #     layer_data["eye_pupil_scale_y"] = eye_pupil_scale_y
    #     layer_data["eye_pupil_scale_z"] = eye_pupil_scale_z

    #     layer_data["eye_upper_pos_z"] = int(eye_upper_pos_z * 10000)
    #     layer_data["eye_upper_scale_z"] = eye_upper_scale_z

    #     layer_data["eye_lower_pos_z"] = int(eye_lower_pos_z * 10000)
    #     layer_data["eye_lower_scale_z"] = eye_lower_scale_z

    #     # print(layer_data)

    #     micropython.schedule(lambda val: pm.update_layer_data(layer_data), None)


