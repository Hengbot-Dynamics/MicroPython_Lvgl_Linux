
import lvgl as lv
from lv_utils import event_loop
import fs_driver
import time
lv.init()
# Register FB display driver

event_loop = event_loop()
disp = lv.linux_fbdev_create()
lv.linux_fbdev_set_file(disp, "/dev/fb0")

fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'L')


# Create a screen and a button

btn = lv.button(lv.screen_active())
btn.align(lv.ALIGN.CENTER, 0, 0)

myfont_cn = lv.binfont_create('L:./alibaba.bin')
label = lv.label(btn)
label.set_style_text_font(myfont_cn, 0)
label.set_text("你好")


img = lv.gif(lv.screen_active())
img.set_src( "L:./astronaut_ezgif.gif")
img.align(lv.ALIGN.CENTER, -50, 0)

while True:
    lv.timer_handler()
    time.sleep_us(5000)