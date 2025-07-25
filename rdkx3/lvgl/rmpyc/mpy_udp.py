import socket
import io
import sys
import time

import lv_pm
pm = lv_pm.pm()

import os
import re
import json

def get_wlan0info():
    essid, signal_level = "", ""
    rt = os.popen("iwconfig wlan0")
    tmp = rt.readlines()
    if "unassociated" in tmp[0]:
        return False
    essid_pattern = r'ESSID:"(.*?)"'
    match = re.search(essid_pattern, tmp[0])
    if match:
        essid = match.group(1)

    signal_level_pattern = r'Signal level=(\d+)/100'
    match = re.search(signal_level_pattern, tmp[6])

    if match:
        signal_level = match.group(1)

    rt = os.popen("ip -4 addr show wlan0 | grep 'inet' | awk '{print $2}' | cut -d/ -f1")
    ipaddr = rt.read()[:-1]

    return [essid, signal_level, ipaddr] if all([essid, signal_level, ipaddr]) else False

def decode_addr(addr):
    tmp = tuple(addr)
    high_byte = tmp[2]
    low_byte = tmp[3]
    port = (high_byte << 8) + low_byte
    addr = str(tmp[4])+'.'+str(tmp[5])+'.'+str(tmp[6])+'.'+str(tmp[7])
    return addr, port

class ioexec(io.IOBase):
    def __init__(self):
        self.nc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = socket.getaddrinfo('0.0.0.0', 8770)[0][4]
        self.nc.bind(addr)
        self.target = socket.getaddrinfo('0.0.0.0', 8267)[0][4]
        self.public_tag = socket.getaddrinfo('239.1.1.1', 10000)[0][4]

    def write(self, buf):
        self.nc.sendto(buf, self.target)
        return len(bytes(buf))
    
    def public_msg(self, buf):
        self.nc.sendto(buf, self.public_tag)
        return len(bytes(buf))

    def read(self, n):
        data, addr = self.nc.recvfrom(102400)
        ip, _ = decode_addr(addr)
        self.target = socket.getaddrinfo(ip, 8267)[0][4]
        return data
    
udpio = ioexec()
pm.remote_msg = udpio.public_msg

def exec_print(*args, **kwargs):
    
    flags = ['>', '<', 'object', 'at', '0x']
    args_repr = [repr(a) for a in args if any(
        f not in repr(a) for f in flags)]
    kwargs_repr = [f"{k}={repr(v)}" if not callable(
        v) else f"{k}={v.__name__}" for k, v in kwargs.items()]
    signature = ", ".join(args_repr + kwargs_repr)
    udpio.write(signature.encode())

import micropython
def mpy_exec(data):
    global print
    tmp = print
    print = exec_print
    try:
        exec(data, globals(), globals())
    except Exception as e:
        # sys.print_exception(e, udpio)
        print("exec",sys.exc_info())
        udpio.write(str(sys.exc_info()).encode())
    print = tmp
    udpio.write(b'>>> ')
    

layer_data = {}
def get_layer_data(data):
    return layer_data if layer_data != {} else False



result_last = None

layer_data_last = {}
layer_data_last["eye_iris_pos_y"] = 0
layer_data_last["eye_iris_pos_z"] = 0
layer_data_last["eye_iris_rot_x"] = 0
layer_data_last["eye_iris_scale_y"] = 1
layer_data_last["eye_iris_scale_z"] = 1

layer_data_last["eye_pupil_pos_y"] = 0
layer_data_last["eye_pupil_pos_z"] = 0
layer_data_last["eye_pupil_rot_x"] = 0
layer_data_last["eye_pupil_scale_y"] = 1
layer_data_last["eye_pupil_scale_z"] = 1

layer_data_last["eye_upper_pos_z"] = 0
layer_data_last["eye_upper_scale_z"] = 1

layer_data_last["eye_lower_pos_z"] = 0
layer_data_last["eye_lower_scale_z"] = 1


while True:
    result = udpio.read(None)
    pm.reload_counter()

    # print(result, len(result))


    if len(result) < 1000:
        try:
            if result != result_last:
                result_last = result

                # print("udp_recv_data: ", result)

                last = time.time()

                ''' 暂时去掉
                    micropython.schedule(mpy_exec, result)
                '''

                data = json.loads(result.decode())

                # 获取各图层的数据
                eye_iris_ = data.get("eye_iris", {})
                eye_pupil_ = data.get("eye_pupil", {})
                eye_upper_ = data.get("eye_upper", {})
                eye_lower_ = data.get("eye_lower", {})

                # 处理 eye_iris 数据
                eye_iris_pos_y = eye_iris_.get("pos_y", layer_data_last["eye_iris_pos_y"])
                eye_iris_pos_z = eye_iris_.get("pos_z", layer_data_last["eye_iris_pos_z"])
                eye_iris_rot_x = eye_iris_.get("rot_x", layer_data_last["eye_iris_rot_x"])
                eye_iris_scale_y = eye_iris_.get("scale_y", layer_data_last["eye_iris_scale_y"])
                eye_iris_scale_z = eye_iris_.get("scale_z", layer_data_last["eye_iris_scale_z"])

                # 处理 eye_pupil 数据
                eye_pupil_pos_y = eye_pupil_.get("pos_y", layer_data_last["eye_pupil_pos_y"])
                eye_pupil_pos_z = eye_pupil_.get("pos_z", layer_data_last["eye_pupil_pos_z"])
                eye_pupil_rot_x = eye_pupil_.get("rot_x", layer_data_last["eye_pupil_rot_x"])
                eye_pupil_scale_y = eye_pupil_.get("scale_y", layer_data_last["eye_pupil_scale_y"])
                eye_pupil_scale_z = eye_pupil_.get("scale_z", layer_data_last["eye_pupil_scale_z"])

                # 处理 eye_upper 数据
                eye_upper_pos_z = eye_upper_.get("pos_z", layer_data_last["eye_upper_pos_z"])
                eye_upper_scale_z = eye_upper_.get("scale_z", layer_data_last["eye_upper_scale_z"])

                # 处理 eye_lower 数据
                eye_lower_pos_z = eye_lower_.get("pos_z", layer_data_last["eye_lower_pos_z"])
                eye_lower_scale_z = eye_lower_.get("scale_z", layer_data_last["eye_lower_scale_z"])


                # get data
                layer_data["eye_iris_pos_y"] = eye_iris_pos_y
                layer_data["eye_iris_pos_z"] = eye_iris_pos_z
                layer_data["eye_iris_rot_x"] = eye_iris_rot_x
                layer_data["eye_iris_scale_y"] = eye_iris_scale_y
                layer_data["eye_iris_scale_z"] = eye_iris_scale_z
                
                layer_data["eye_pupil_pos_y"] = eye_pupil_pos_y
                layer_data["eye_pupil_pos_z"] = eye_pupil_pos_z
                layer_data["eye_pupil_rot_x"] = eye_pupil_rot_x
                layer_data["eye_pupil_scale_y"] = eye_pupil_scale_y
                layer_data["eye_pupil_scale_z"] = eye_pupil_scale_z

                layer_data["eye_upper_pos_z"] = eye_upper_pos_z
                layer_data["eye_upper_scale_z"] = eye_upper_scale_z

                layer_data["eye_lower_pos_z"] = eye_lower_pos_z
                layer_data["eye_lower_scale_z"] = eye_lower_scale_z

                layer_data_last = layer_data

                print("layer_data: ", layer_data, "layer_data_get_time_ms: ", (last - time.time()) / 1000, "\n")

                micropython.schedule(lambda val: pm.update_layer_data(layer_data), None)

        except RuntimeError as e:
            print("==> Schedule RuntimeError!!!")
    else:
        if result[0] == 0xff and result[1] == 0xd8:
            try:
                micropython.schedule(pm.show, result)
            except RuntimeError as e:
                print("schedule")

