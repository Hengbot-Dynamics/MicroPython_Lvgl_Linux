import lvgl as lv
import lv_pm
pm = lv_pm.pm()

def create(page):
    print("home")

    def img_event_cb(event):
        tmp = ["", "more", "setting", "aifunc", "", "", ""]
        tmp = tmp[pm.get_lis_index()]
        if tmp:
            print(tmp)
            pm.open_page(tmp)
            

    pm.create_page_lis(img_event_cb, pm.path + 'reset/home/home_cartoon.png')

    pm.create_png(pm.path+'reset/home/home_canvas_freemode.png', "遥控模式")
    pm.create_png(pm.path+'reset/home/home_canvas_more.png', "more")
    pm.create_png(pm.path+'reset/home/home_canvas_setting.png', "setting")
    pm.create_png(pm.path+'reset/home/home_canvas_aifunc.png', "aifunc")
    pm.create_png(pm.path+'reset/home/home_canvas_self_balance.png', "自平衡")
    pm.create_png(pm.path+'reset/home/home_canvas_motions.png', "动作组")
    pm.create_png(pm.path+'reset/home/home_canvas_poweroff.png', "关机")

    pm.create_page_end()

def unLoad(page):
    print("home_unLoad: unLoad")

page = lv_pm.page(create, unLoad, descrip="home")