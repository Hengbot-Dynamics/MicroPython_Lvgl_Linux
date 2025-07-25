import lvgl as lv
import lv_pm
pm = lv_pm.pm()

def create(page):
    print("more")

    def img_event_cb(event):
        pass

    pm.create_page_lis(img_event_cb, pm.path + 'reset/more/more_cartoon.png')
    
    pm.create_png(pm.path+'reset/more/more_canvas_free.png', "自由模式")

    pm.create_page_end()


def unLoad(page):
    print("more_unLoad: unLoad")

page = lv_pm.page(create, unLoad, descrip="more")