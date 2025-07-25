import os
import lvgl as lv

class BUTTON:
    def __init__(self, gpioId):
        sendMsg_1='echo '
        sendMsg_2=' > /sys/class/gpio/export'
        sendMsg_3=' > /sys/class/gpio/unexport'
        sendMsg_4='echo "in" > /sys/class/gpio/gpio'
        sendMsg_5='/direction'
        sendMsg_6='/sys/class/gpio/gpio'
        sendMsg_7='/value'
        self.gpio=str(224+gpioId)
        self.msgStart=sendMsg_1+self.gpio+sendMsg_2
        self.msgMode=sendMsg_4+self.gpio+sendMsg_5
        self.msgDel=sendMsg_1+self.gpio+sendMsg_3
        self.msgGet=sendMsg_6+self.gpio+sendMsg_7

    def is_pressed(self):
        try:
            os.stat(self.msgGet)
        except OSError:
            os.system(self.msgStart)
        # if(os.access(self.msgGet, os.F_OK) is False):
        #     os.system(self.msgStart)
        os.system(self.msgMode)
        with open(self.msgGet, "rb") as self.file:
            self.getValue=int(self.file.read())
        if self.getValue != 1:
            return True
        else:
            return False
        
    def __del__(self):
        os.system(self.msgDel)

class key_indev:
    def __init__(self,key,x,y):
        self.key = key
        # Register LVGL indev driver
        self.indev = lv.indev_create()
        self.indev.set_type(lv.INDEV_TYPE.BUTTON)
        self.indev.set_read_cb(self.cb)
        point = lv.point_t()
        point.x = x
        point.y = y
        self.indev.set_button_points(point)

    def cb(self, indev, data) -> int:
        # print(self.key.is_pressed())
        data.state = lv.INDEV_STATE.PRESSED if ((self.key.is_pressed() & 1) == 1) else lv.INDEV_STATE.RELEASED
        return 0


if __name__ == '__main__':
    from lv_utils import event_loop

    key_l = BUTTON(13)
    key_r = BUTTON(14)

    lv.init()

    event_loop = event_loop()
    disp = lv.linux_fbdev_create()
    lv.linux_fbdev_set_file(disp, "/dev/fb0")


    key = key_indev(key_l,20,160)
    key = key_indev(key_r,220,160)

    panel = lv.obj(lv.screen_active())
    panel.set_size(240, 120)
    panel.set_scroll_snap_x(lv.SCROLL_SNAP.CENTER)
    panel.set_flex_flow(lv.FLEX_FLOW.ROW)
    panel.align(lv.ALIGN.CENTER, 0, 20)

    for i in range(5):
        but = lv.button(panel)
        but.set_size(150, lv.pct(100))
        lab = lv.label(but)
        lab.set_text("Button " + str(i + 1))

        lab.align(lv.ALIGN.CENTER, 0, 0)
    panel.move_to_index(0)
    panel.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    panel.update_snap(lv.ANIM.ON)

    import time
    while True:
        time.sleep_ms(1000)

