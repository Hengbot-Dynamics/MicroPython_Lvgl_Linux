import lvgl as lv
import lv_pm
pm = lv_pm.pm()

def wait_bar(page):

    bg = lv.obj(page)
    bg.set_style_border_width(0, lv.STATE.DEFAULT)
    bg.set_style_pad_all(0, lv.STATE.DEFAULT)
    bg.set_height(lv.screen_active().get_height())
    bg.set_width(lv.screen_active().get_width())
    bg.set_style_bg_opa(0, lv.STATE.DEFAULT)
    bg.remove_flag(lv.obj.FLAG.SCROLLABLE)
    
    def creat_anim(obj):
        anim = lv.anim_t()
        anim.set_path_cb(lv.anim_t.path_overshoot)
        anim.set_time(500)
        anim.set_repeat_count(1)
        anim.set_values(240,100)
        anim.set_custom_exec_cb(lambda a,val: obj.set_x(val))
        return anim

    def creat_label(y, text = "Text"):
        label = lv.label(bg)
        label.set_pos(240, y)
        label.set_size(lv.SIZE_CONTENT, lv.SIZE_CONTENT)
        label.set_text(text)
        label.set_style_text_color(lv.color_hex(0xffffffff), 0)
        return label
    
    with open(pm.path + 'reset/false_b.png', 'rb') as f:
        true_data = f.read()

    with open(pm.path + 'reset/false.png', 'rb') as f:
        false_data = f.read()

    def creat_torf(y, torf = True):
        if torf:
            image_dsc = lv.image_dsc_t({
                "data_size": len(true_data),
                "data": true_data,
            })
        else:
            image_dsc = lv.image_dsc_t({
                "data_size": len(false_data),
                "data": false_data,
            })

        img = lv.image(bg)
        img.set_src(image_dsc)
        img.set_size(25, 25)
        img.set_pos(60, y)

    label1 = creat_label(80, "IMU")
    label2 = creat_label(110, "KEY")
    label3 = creat_label(140, "Battery")
    label4 = creat_label(170, "WIFI Driver")
    label5 = creat_label(200, "M-FFFFFFF")

    img1 = creat_torf(78)
    img2 = creat_torf(108)
    img3 = creat_torf(138)
    img4 = creat_torf(168)
    img5 = creat_torf(198)

    anim1 = creat_anim(label1)
    anim2 = creat_anim(label2)
    anim3 = creat_anim(label3)
    anim4 = creat_anim(label4)
    anim5 = creat_anim(label5)

    timeline = lv.anim_timeline_create()
    timeline.add(0,anim1)
    timeline.add(150,anim2)
    timeline.add(300,anim3)
    timeline.add(450,anim4)
    timeline.add(600,anim5)

    timeline.start()


def create(page):
    print("setting_bios")
    pm.create_bar(wait_bar,pm.path + 'reset/setting/setting_cartoon.png')


def unLoad(page):
    print("setting_unLoad: unLoad")

page = lv_pm.page(create, unLoad, descrip="set_bios")