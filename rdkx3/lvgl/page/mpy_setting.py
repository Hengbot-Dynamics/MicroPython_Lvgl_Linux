import lvgl as lv
import lv_pm
pm = lv_pm.pm()

def create(page):
    print("setting")

    def img_event_cb(event):
        tmp = ["set_bios", "set_vol", "wifi", "", "", "", ""]
        tmp = tmp[pm.get_lis_index()]
        if tmp == 'wifi':
            pm.remote_msg(b'wifi')
        elif tmp:
            print(tmp)
            print(pm.open_page(tmp))

    pm.create_page_lis(img_event_cb, pm.path + 'reset/setting/setting_cartoon.png')
    
    pm.create_png(pm.path+'reset/setting/setting_canvas_bios.png', "set_bios")
    pm.create_png(pm.path+'reset/setting/setting_canvas_volume.png', "set_vol")
    pm.create_png(pm.path+'reset/setting/setting_canvas_wifi.png', "WIFI")
    pm.create_png(pm.path+'reset/setting/setting_canvas_calibration.png', "动作标定")
    pm.create_png(pm.path+'reset/setting/setting_canvas_develop.png', "开发者模式")
    pm.create_png(pm.path+'reset/setting/setting_canvas_language.png', "语言")
    pm.create_png(pm.path+'reset/setting/setting_canvas_sysscan.png', "系统检查")

    pm.create_page_end()


def unLoad(page):
    print("setting_unLoad: unLoad")

page = lv_pm.page(create, unLoad, descrip="setting")