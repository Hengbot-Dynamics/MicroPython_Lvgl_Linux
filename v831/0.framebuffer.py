import lvgl as lv
from lv_utils import event_loop

lv.init()

# Register FB display driver

event_loop = event_loop()
disp = lv.linux_fbdev_create()
lv.linux_fbdev_set_file(disp, "/dev/fb0")

# Create a screen and a button

btn = lv.button(lv.screen_active())
btn.align(lv.ALIGN.CENTER, 0, 0)
label = lv.label(btn)
label.set_text("Hello World!")

import time
while True:
    time.sleep_ms(1000)