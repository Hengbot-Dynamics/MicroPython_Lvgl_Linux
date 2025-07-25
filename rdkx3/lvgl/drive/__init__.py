import lvgl as lv
from .mpy_display import Display
display = Display(240, 284)
import lv_pm
pm = lv_pm.pm()
pm.set_duty = display.set_duty
pm.get_duty = display.get_duty
display.set_duty(0)

# 250227-硬件上暂无触摸，先注释
# from .mpy_mouse import mouse_indev
# mouse = mouse_indev(lv.layer_sys())
# pm.mouse = mouse
