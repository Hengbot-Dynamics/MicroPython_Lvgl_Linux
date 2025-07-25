import lvgl as lv
from lv_utils import event_loop

lv.init()

# Register FB display driver

event_loop = event_loop()
disp = lv.linux_fbdev_create()
lv.linux_fbdev_set_file(disp, "/dev/fb0")

# Create a screen and a button

cont_col = lv.obj(lv.screen_active())
cont_col.set_size(240, 320)
# cont_col.align_to(cont_row, lv.ALIGN.OUT_BOTTOM_MID, 0, 5)
cont_col.set_flex_flow(lv.FLEX_FLOW.COLUMN)


# Add items to the column
obj = lv.button(cont_col)
obj.set_size(lv.pct(100), lv.SIZE_CONTENT)

label = lv.label(obj)
label.set_text("HELLO")
label.center()

bar1 = lv.bar(cont_col)
bar1.set_size(200, 20)
bar1.center()
bar1.set_value(70, lv.ANIM.OFF)

cb = lv.checkbox(cont_col)
cb.set_text("TEST")

dd = lv.dropdown(cont_col)
dd.set_options("\n".join([
    "Apple",
    "Banana",
    "Orange"]))

dd.align(lv.ALIGN.TOP_MID, 0, 20)


with open("./astronaut_ezgif.gif", "rb") as f:
    gif_data = f.read()
img_bulb_gif = lv.image_dsc_t({
    "data_size": 0,
    "data": gif_data,
})

img = lv.gif(cont_col)
img.set_src(img_bulb_gif)

slider = lv.slider(cont_col)
slider.set_value(20, lv.ANIM.OFF)

sw = lv.switch(cont_col)
sw.add_state(lv.STATE.CHECKED)

import time
while True:
    time.sleep_ms(1000)