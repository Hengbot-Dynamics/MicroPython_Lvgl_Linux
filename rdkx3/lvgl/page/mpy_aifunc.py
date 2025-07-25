import lvgl as lv
import lv_pm
pm = lv_pm.pm()

def create(page):
    print("aifunc")

    def img_event_cb(event):
        pass

    pm.create_page_lis(img_event_cb, pm.path + 'reset/aifunc/aifunc_cartoon.png')
    
    # png_create('./reset/aifunc/aifunc_canvas_color_traking.png')
    pm.create_png(pm.path+'reset/aifunc/aifunc_canvas_color_traking.png', "颜色识别")
    pm.create_png(pm.path+'reset/aifunc/aifunc_canvas_detect.png', "物体识别")
    pm.create_png(pm.path+'reset/aifunc/aifunc_canvas_person.png', "人脸识别")

    pm.create_page_end()


def unLoad(page):
    print("aifunc_unLoad: unLoad")

page = lv_pm.page(create, unLoad, descrip="aifunc")