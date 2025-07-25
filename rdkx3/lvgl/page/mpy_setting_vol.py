import lvgl as lv
import cmodule
import lv_pm
pm = lv_pm.pm()

def create(page):
    print("setting_vol")

    # amixer get 'Headphone' | grep -oP '\[\d+\%\]' | sed 's/[^0-9]//g' | head -1
    rt = cmodule.rpopen("amixer get 'Headphone' | grep -oP '\[\d+\%\]' | sed 's/[^0-9]//g' | head -1")
    vol = int(rt)
    

    def img_event_cb(event):
        pass

    pm.create_page_lis(img_event_cb, pm.path + 'reset/setting/setting_cartoon.png')

    def vol_change(event):
        if(event.get_code() == lv.EVENT.RELEASED):
            rt = cmodule.rpopen("amixer set 'Headphone' " + str(event.get_target_obj().get_value()))

    slider = lv.slider(page)
    slider.set_range(0, 45)
    slider.set_pos(45, 100)
    slider.set_size(150, 10)
    slider.set_value(vol, lv.ANIM.ON)
    slider.add_event_cb(vol_change,lv.EVENT.RELEASED,None)

    def bl_change(event):
        if(event.get_code() == lv.EVENT.RELEASED):
            pm.set_duty(event.get_target_obj().get_value())

    slider = lv.slider(page)
    slider.set_range(30, 100)
    slider.set_pos(45, 142)
    slider.set_size(150, 10)
    slider.set_value(pm.get_duty(), lv.ANIM.ON)
    slider.add_event_cb(bl_change,lv.EVENT.RELEASED,None)


def unLoad(page):
    print("setting_unLoad: unLoad")

page = lv_pm.page(create, unLoad, descrip="set_vol")