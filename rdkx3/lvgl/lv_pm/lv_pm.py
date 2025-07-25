import lvgl as lv
import os
import time
from . import lv_anim
from . import fs_bytesio

path = __file__[:__file__.rfind('/')+1]

def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

def _appear_complete_cb(pm_page, options):
    if pm_page.willAppear:
        pm_page.willAppear(pm_page.page)

def _back_appear_complete_cb(pm_page, options):
    if pm_page.didAppear:
        pm_page.didAppear(pm_page.page)

def _disAppear_complete_cb(pm_page, options):
    # todo
    if options == open_options.ANIM_NONE:
        pm_page.page.add_flag(lv.obj.FLAG.HIDDEN)
    if pm_page.willDisappear:
        pm_page.willDisappear(pm_page.page)
    # if options.open_tag == open_options.TARGET_SELF:
    pm_page.unLoad(pm_page.page)
    pm_page.page.clean()

def _back_disAppear_complete_cb(pm_page, options):
    # todo
    if options == open_options.ANIM_NONE:
        pm_page.page.add_flag(lv.obj.FLAG.HIDDEN)
    if pm_page.didDisappear:
        pm_page.didDisappear(pm_page.page)
    pm_page.unLoad(pm_page.page)
    pm_page.page.clean()


class open_options():
    ANIM_NONE = 0
    ANIM_SLIDE = 1
    ANIM_FADE = 2
    ANIM_POPUP = 3

class page():
    def __init__(self, onLoad, unLoad, descrip=None, willAppear=None, didAppear=None, willDisappear=None, didDisappear=None, returnable=True, screen = lv.screen_active()):
        screen.remove_flag(lv.obj.FLAG.SCROLLABLE)
        self.page = lv.obj(screen)
        self.page.remove_flag(lv.obj.FLAG.SCROLLABLE)
        self.page.set_style_border_width(0, lv.STATE.DEFAULT)
        self.page.set_style_radius(0, lv.STATE.DEFAULT)
        self.page.set_style_pad_all(0, lv.STATE.DEFAULT)
        self.page.add_flag(lv.obj.FLAG.HIDDEN)
        self.page.set_height(screen.get_height())
        self.page.set_width(screen.get_width())

        self.onLoad = onLoad
        self.willAppear = willAppear
        self.didAppear = didAppear
        self.willDisappear = willDisappear
        self.didDisappear = didDisappear
        self.unLoad = unLoad
        self.returnable = returnable

        self.descrip = descrip

        self.__back = False
        self.__options = None

class _pm():
    def __init__(self):
        self.history = []
        self.router = []
        # turn off the scroll bar
        lv.screen_active().set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    
    def add_page(self, page):
        self.router.append(page)
        return len(self.router) - 1
    
    def open_page(self, id, options=open_options.ANIM_NONE):
        if (id > len(self.router) - 1) or id < 0:
            return False, "id err"
        self.history.append(id)
        pm_page = self.router[id]
        
        pm_page.__options = options
        pm_page.__back = False
        if len(self.history) > 1:
            prev_pm_page = self.router[self.history[-2]]
            prev_pm_page.__back = False
            if prev_pm_page.willDisappear:
                prev_pm_page.willDisappear(prev_pm_page.page)
            lv_anim._pm_anim_disAppear(prev_pm_page, pm_page.__options, _disAppear_complete_cb)
        pm_page.onLoad(pm_page.page)
        pm_page.page.remove_flag(lv.obj.FLAG.HIDDEN)
        pm_page.page.move_foreground()
        if pm_page.willAppear:
            pm_page.willAppear(pm_page.page)
        lv_anim._pm_anim_appear(pm_page, pm_page.__options, _appear_complete_cb)
    
    def back(self):
        
        pm_page = self.router[self.history.pop()]
        pm_page.__back = True
        if pm_page.willDisappear:
            pm_page.willDisappear(pm_page.page)
        lv_anim._pm_anim_disAppear(pm_page, pm_page.__options, _back_disAppear_complete_cb)

        while not self.router[self.history[-1]].returnable:
            self.history.pop()
            if len(self.history) < 1:
                return False
        prev_pm_page = self.router[self.history[-1]]
        prev_pm_page.__back = True
        if prev_pm_page.willDisappear:
            prev_pm_page.willDisappear(prev_pm_page.page)

        prev_pm_page.onLoad(prev_pm_page.page)
        prev_pm_page.page.remove_flag(lv.obj.FLAG.HIDDEN)
        prev_pm_page.page.move_foreground()
        lv_anim._pm_anim_appear(prev_pm_page, pm_page.__options, _back_appear_complete_cb)
        return True


@singleton
class pm(_pm):
    def __init__(self, mouse=None, kpath=path, *args, **kargs):
        super().__init__(*args, **kargs)
        self.mouse = mouse
        self.path = kpath
        self.font = lv.binfont_create('L:./reset/alibaba.bin')
        fs_drv = lv.fs_drv_t()
        fs_bytesio.fs_register(fs_drv, 'A')
        self.page_descrip_dict={}
        self.__page_init()
        self.show_obj = [None, None]
        dip = lv.display_get_default()
        theme = lv.theme_default_init(dip, lv.palette_main(lv.PALETTE.BLUE), lv.palette_main(lv.PALETTE.RED), True, lv.font_default())
        dip.set_theme(theme)
        self.back_counter = -31
        self.signal_level = 0
        self.battery_level = 0
        self.ipaddr = ""
        self.img_wifi = None
        self.img_battery = None
        self.lab_ipaddr = None
        self.wifi_lis = []
        self.batt_lis = []

        # 图层对象
        self.layer_background = None
        self.layer_eye_iris = None
        self.layer_eye_pupil = None
        self.layer_eye_lower = None
        self.layer_eye_lower = None
        self.layer_immobility_back = None
        self.layer_immobility_front = None

        # 图层数据
        self.layer_data = {}

        # 图片缩放基准
        self.scale = 256


        # 屏幕参数
        self.screen_width  = lv.screen_active().get_width()
        self.screen_height = lv.screen_active().get_height()

        self.screen_center_y = int(self.screen_width / 2)
        self.screen_center_z = int(self.screen_height / 2)



        for i in range(1,5):
            with open(path + f'../reset/WiFi/Wifi-{i}.png', 'rb') as f:
                png_data = f.read()
            img = lv.image_dsc_t({
                "data_size": len(png_data),
                "data": png_data,
            })
            self.wifi_lis.append(img)
            with open(path + f'../reset/WiFi/battery{i}.png', 'rb') as f:
                png_data = f.read()
            img = lv.image_dsc_t({
                "data_size": len(png_data),
                "data": png_data,
            })
            self.batt_lis.append(img)
    
    def __page_init(self):
        self.panel = None
        self.lis = []
        self.lis_cb = None
        self.lis_descrip_dict={}
        self.bar = None
        self.msgbox = None

    def reload_counter(self):
        self.back_counter = time.time()

    def get_page_index_descrip(self, index):
        return self.router[index].descrip if len(self.router) > index else None
    
    def get_page_descrip_index(self, descrip):
        return self.page_descrip_dict.get(descrip)

    def get_page_index(self):
        return self.history[-1] if len(self.history) else None

    def get_page_descrip(self):
        return self.get_page_index_descrip(self.get_page_index()) if len(self.history) else None
    
    def get_lis_index_descrip(self, index):
        return self.lis[index][1] if len(self.lis) else None
    
    def get_lis_descrip_index(self, descrip):
        return self.lis_descrip_dict.get(descrip)
    
    def get_lis_index(self):
        return int((self.panel.get_scroll_x()+47)/128) if self.panel else None

    def get_lis_descrip(self):
        return self.get_lis_index_descrip(self.get_lis_index()) if len(self.lis) else None

    def add_page(self, page):
        self.page_descrip_dict[page.descrip] = super().add_page(page)

    def open_page(self, obj, options=open_options.ANIM_FADE):

        if type(obj) == str:
            id = self.get_page_descrip_index(obj)
            if id is None:
                return False
        else:
            id = obj
        
        if self.history and id == self.history[-1]:
            return False
        self.__page_init()
        super().open_page(id, options)

        if len(self.history) > 1 and self.mouse:
            def back_cb(event):
                if(event.get_code() == lv.EVENT.RELEASED):
                    if self.mouse.y - 5 > 70:
                        self.back()
            def back_home_cb(event):
                if(event.get_code() == lv.EVENT.RELEASED):
                    if lv.screen_active().get_height() - self.mouse.y > 70:
                        self.back_home()
            ret = lv.button(self.router[self.history[-1]].page)
            ret.set_size(240, 20)
            # ret.set_style_opa(0, lv.STATE.DEFAULT)
            ret.align(lv.ALIGN.TOP_MID,0,0)
            ret.add_flag(lv.obj.FLAG.CLICKABLE)
            # ret.add_event_cb(drag_PRESS_cb,lv.EVENT.PRESSING,None)
            ret.add_event_cb(back_cb,lv.EVENT.RELEASED,None)

            ret_home = lv.button(self.router[self.history[-1]].page)
            ret_home.set_size(240, 20)
            # ret_home.set_style_opa(0, lv.STATE.DEFAULT)
            ret_home.align(lv.ALIGN.TOP_MID,0,lv.screen_active().get_height()-20)
            ret_home.add_flag(lv.obj.FLAG.CLICKABLE)
            # ret_home.add_event_cb(drag_PRESS_cb,lv.EVENT.PRESSING,None)
            ret_home.add_event_cb(back_home_cb,lv.EVENT.RELEASED,None)

    def enter(self):
        if self.lis_cb:
            self.lis_cb(None)

    def back(self):
        if len(self.history) < 2:
            return False
        self.__page_init()
        return super().back()

    def back_home(self):
        # if len(self.history) < 2:
        #     return False, "history < 2"
        pm_page = self.router[self.history.pop()]
        pm_page.__back = True
        if pm_page.willDisappear:
            pm_page.willDisappear(pm_page.page)
        lv_anim._pm_anim_disAppear(pm_page, pm_page.__options, _back_disAppear_complete_cb)

        prev_pm_page = self.router[0]
        self.history = []
        self.history.append(0)
        prev_pm_page.__back = True
        if prev_pm_page.willDisappear:
            prev_pm_page.willDisappear(prev_pm_page.page)

        prev_pm_page.onLoad(prev_pm_page.page)
        prev_pm_page.page.remove_flag(lv.obj.FLAG.HIDDEN)
        prev_pm_page.page.move_foreground()
        lv_anim._pm_anim_appear(prev_pm_page, pm_page.__options, _back_appear_complete_cb)
        return True

    def create_page_lis(self, lis_cb, bg_path):

        with open(bg_path, 'rb') as f:
            png_data = f.read()
        bg = lv.image_dsc_t({
            "data_size": len(png_data),
            "data": png_data,
        })
        background = lv.image(self.router[self.history[-1]].page)
        background.set_src(bg)
        background.center()

        panel_style = lv.style_t()
        panel_style.init()
        panel_style.set_bg_opa(lv.OPA.TRANSP)
        panel_style.set_border_width(0)

        self.panel = lv.obj(background)
        self.panel.set_size(240, 240)
        self.panel.set_scroll_snap_x(lv.SCROLL_SNAP.CENTER)
        self.panel.set_flex_flow(lv.FLEX_FLOW.ROW)
        self.panel.align(lv.ALIGN.CENTER, 0, -20)
        self.panel.add_style(panel_style, lv.PART.MAIN)

        self.panel.add_flag(lv.obj.FLAG.CLICKABLE)
        self.panel.add_event_cb(lis_cb, lv.EVENT.CLICKED, None)

        self.lis_cb = lis_cb

    def create_png(self, path, descrip):
        
        with open(path, 'rb') as f:
            png_data = f.read()
        img = lv.image_dsc_t({
            "data_size": len(png_data),
            "data": png_data,
        })
        obj = lv.image(self.panel)
        obj.set_src(img)
        obj.center()
        obj.set_size(120,240)

        self.lis.append([obj, descrip])
        self.lis_descrip_dict[descrip] = len(self.lis) - 1

    def create_page_end(self):
        self.panel.move_to_index(0)
        self.panel.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.panel.update_snap(lv.ANIM.ON)
        self.panel.move_foreground()
        self.panel.set_scroll_dir(lv.DIR.HOR)


    # 创建图层堆叠
    def create_png_layers(self, layer_path_list, descrip_):

        # 获取图层数量
        layer_num = len(layer_path_list)
        print("layer_num: ", layer_num)

        for layer_index in range(layer_num):
            # print("layer_index: ", layer_index)

            layer_path = layer_path_list[layer_index]
            print("layer_path: ", layer_path)

            # 解析图像
            with open(layer_path, 'rb') as f:
                png_data = f.read()
            img = lv.image_dsc_t({
                "data_size": len(png_data),
                "data": png_data,
            })

            # 绑定图像
            if layer_index == 0:
                self.layer_background = lv.image(self.router[self.history[-1]].page)
                self.layer_background.set_src(img)
                self.layer_background.center()
            elif layer_index == 1:
                self.layer_eye_iris = lv.image(self.router[self.history[-1]].page)
                self.layer_eye_iris.set_src(img)
                self.layer_eye_iris.center()
            elif layer_index == 2:
                self.layer_eye_pupil = lv.image(self.router[self.history[-1]].page)
                self.layer_eye_pupil.set_src(img)
                self.layer_eye_pupil.center()
            elif layer_index == 3:
                self.layer_eye_lower = lv.image(self.router[self.history[-1]].page)
                self.layer_eye_lower.set_src(img)
                self.layer_eye_lower.center()
            elif layer_index == 4:
                self.layer_eye_upper = lv.image(self.router[self.history[-1]].page)
                self.layer_eye_upper.set_src(img)
                self.layer_eye_upper.center()
            elif layer_index == 5:
                self.layer_immobility_back = lv.image(self.router[self.history[-1]].page)
                self.layer_immobility_back.set_src(img)
                self.layer_immobility_back.center()
            elif layer_index == 6:
                self.layer_immobility_front = lv.image(self.router[self.history[-1]].page)
                self.layer_immobility_front.set_src(img)
                self.layer_immobility_front.center()


    # 更新图层数据
    def update_layer_data(self, layer_data):
        last = time.time()
        self.layer_data = layer_data
        # print("self.layer_data: ", self.layer_data)

        # 测试屏幕参数和边界
        # print("self.screen_width: ", self.screen_width, "self.screen_height: ", self.screen_height)
        # print("self.screen_center_y: ", self.screen_center_y, "self.screen_center_z: ", self.screen_center_z)
        # print("\n")


        # 解析并计算各图层参数
        '''
            pos
            - 画布相对于屏幕中心位置的像素值，其报文数据类型必须为整型，范围为屏幕分辨率的一半[120, 142]，若报文数据越界，显示层会做越界处理
            - 图片在屏幕上显示是以屏幕左上角显示为基准，图片移动基准定在屏幕左上角或者屏幕中心是一致的，只需要在乎所变的像素点即可

            
            scale
            - 缩放，其报文数据类型为浮点型，表示缩放比例，1.0为不缩放，0.5为缩小一半，2.0为放大两倍，边界为[0.0, 2.0]，若报文数据越界，显示层会做越界处理
            - 0->消失 128->缩小一半 256->不缩放 512->放大两倍  
            - 将 factor 设置为 256 或 LV_SCALE_NONE 可禁用缩放。较大的值会放大图像（例如 512 两倍大小），较小的值会缩小图像（例如 128 一半大小）。分数缩放使用按比例更大或更小的值，例如 281 表示放大 10%。


            rotation
            - 为旋转角度，其报文数据类型为整形，表示图层旋转角度，0/360为不旋转，+90为顺时针旋转90度，-90为逆时针旋转90度
            - 900->顺时针旋转90度 0/360->不旋转 -900->逆时针旋转90度
        '''

        eye_iris_pos_y_ = self.layer_data["eye_iris_pos_y"]
        eye_iris_pos_z_ = self.layer_data["eye_iris_pos_z"]
        eye_iris_rot_x_ = self.layer_data["eye_iris_rot_x"]
        eye_iris_scale_y_ = self.layer_data["eye_iris_scale_y"]
        eye_iris_scale_z_ = self.layer_data["eye_iris_scale_z"]

        eye_pupil_pos_y_ = self.layer_data["eye_pupil_pos_y"]
        eye_pupil_pos_z_ = self.layer_data["eye_pupil_pos_z"]
        eye_pupil_rot_x_ = self.layer_data["eye_pupil_rot_x"]
        eye_pupil_scale_y_ = self.layer_data["eye_pupil_scale_y"]
        eye_pupil_scale_z_ = self.layer_data["eye_pupil_scale_z"]

        eye_lower_pos_z_ = self.layer_data["eye_lower_pos_z"]
        eye_lower_scale_z_ = self.layer_data["eye_lower_scale_z"]

        eye_upper_pos_z_ = self.layer_data["eye_upper_pos_z"]
        eye_upper_scale_z_ = self.layer_data["eye_upper_scale_z"]


        eye_iris_pos_y = int(eye_iris_pos_y_)
        eye_iris_pos_z = int(eye_iris_pos_z_)
        eye_iris_rot_x = int(eye_iris_rot_x_ * 10)
        eye_iris_scale_y = int(self.scale * eye_iris_scale_y_)
        eye_iris_scale_z = int(self.scale * eye_iris_scale_z_)


        eye_pupil_pos_y = int(eye_pupil_pos_y_)
        eye_pupil_pos_z = int(eye_pupil_pos_z_)
        eye_pupil_rot_x = int(eye_pupil_rot_x_ * 10)
        eye_pupil_scale_y = int(self.scale * eye_pupil_scale_y_)
        eye_pupil_scale_z = int(self.scale * eye_pupil_scale_z_)


        eye_lower_pos_z = int(eye_lower_pos_z_)
        eye_lower_scale_z = int(self.scale * eye_lower_scale_z_)

        eye_upper_pos_z = int(eye_upper_pos_z_)
        eye_upper_scale_z = int(self.scale * eye_upper_scale_z_)

        print(
            "eye_iris_pos_y: ", eye_iris_pos_y, "eye_iris_pos_z: ", eye_iris_pos_z,
            "eye_iris_rot_x: ", eye_iris_rot_x, "eye_iris_scale_y", eye_iris_scale_y, "eye_iris_scale_z: ", eye_iris_scale_z
            )
        print(
                "eye_pupil_pos_y: ", eye_pupil_pos_y, "eye_pupil_pos_z: ", eye_pupil_pos_z,
                "eye_pupil_rot_x: ", eye_pupil_rot_x, "eye_pupil_scale_y", eye_pupil_scale_y, "eye_pupil_scale_z: ", eye_pupil_scale_z
            )
        print("eye_lower_pos_z: ", eye_lower_pos_z, "eye_lower_scale_z: ", eye_lower_scale_z)
        print("eye_upper_pos_z: ", eye_upper_pos_z, "eye_upper_scale_z: ", eye_upper_scale_z)
        print("\n\n")


        # 设置图层参数
        if self.layer_eye_iris:
            self.layer_eye_iris.set_pos(eye_iris_pos_y, eye_iris_pos_z)
            self.layer_eye_iris.set_scale_x(eye_iris_scale_y)
            self.layer_eye_iris.set_scale_y(eye_iris_scale_z)
            self.layer_eye_iris.set_rotation(eye_iris_rot_x)


        if self.layer_eye_pupil:
            self.layer_eye_pupil.set_pos(eye_pupil_pos_y, eye_pupil_pos_z)
            self.layer_eye_pupil.set_scale_x(eye_pupil_scale_y)
            self.layer_eye_pupil.set_scale_y(eye_pupil_scale_z)
            self.layer_eye_pupil.set_rotation(eye_pupil_rot_x)

        if self.layer_eye_lower:
            eye_lower_pos_y = self.layer_eye_lower.get_x()
            self.layer_eye_lower.set_pos(eye_lower_pos_y, eye_lower_pos_z)
            self.layer_eye_lower.set_scale_y(eye_lower_scale_z)

        if self.layer_eye_upper:
            eye_upper_pos_y = self.layer_eye_upper.get_x()
            self.layer_eye_upper.set_pos(eye_upper_pos_y, eye_upper_pos_z)
            self.layer_eye_upper.set_scale_y(eye_upper_scale_z)

        now = time.time()
        print("layer data update time ms: ", (last - now) / 1000)

        

    def create_bar(self, cb, bg_path):
        with open(bg_path, 'rb') as f:
            png_data = f.read()
        
        bg = lv.image_dsc_t({
            "data_size": len(png_data),
            "data": png_data,
        })

        background = lv.image(self.router[self.history[-1]].page)
        background.set_src(bg)
        background.center()

        self.bar = lv.bar(background)
        self.bar.set_pos(45, 97)
        self.bar.set_size(150, 10)

        def set_value(val):
            self.bar.set_value(val, lv.ANIM.ON)
            # print(val)
            if val == 100:
                background.clean()
                cb(background)

        anim = lv.anim_t()
        anim.set_path_cb(lv.anim_t.path_ease_out)
        anim.set_time(1500)
        anim.set_repeat_count(1)
        anim.set_values(0,100)
        anim.set_custom_exec_cb(lambda a,val: set_value(val))
        anim.start()

    def set_bar_val(self, val):
        if self.bar:
            self.bar.set_value(val, lv.ANIM.ON)
            return True
        return False

    def get_bar_val(self):
        return self.bar.get_value() if self.bar else False
    
    def show(self, data):
        if len(data) > 1000:
            if self.show_obj[1] != "cam":
                self.clear_show()
                self.show_obj[0] = lv.image(lv.layer_top())
                self.show_obj[0].center()
                self.show_obj[1] = "cam"
            fs_bytesio.byte_data = data
            self.show_obj[0].set_src("A:cam.jpg")
        else:
            stat = os.stat(data)
            if stat[0]&0o170000 == 0o040000:
                # 目录
                if self.show_obj[1] != "express":
                    self.clear_show()
                    self.show_obj[0] = lv.animimg(lv.layer_top())
                    self.show_obj[0].center()
                    self.show_obj[1] = "express"
                lis = sorted(os.listdir(data))
                file_lis = []
                for file in lis:
                    file_lis.append((data + '/' + file).encode())
                self.show_obj[0].set_src(file_lis, len(file_lis))
                self.show_obj[0].set_duration(len(file_lis) * 20)
                self.show_obj[0].set_repeat_count(lv.ANIM_REPEAT_INFINITE)
                self.show_obj[0].start()
            elif stat[0]&0o170000 == 0o100000:
                # 文件
                if self.show_obj[1] != "gif":
                    self.clear_show()
                    self.show_obj[0] = lv.gif(lv.layer_top())
                    self.show_obj[0].center()
                    self.show_obj[1] = "gif"
                    def click(event):
                        self.clear_show()
                    self.show_obj[0].add_flag(lv.obj.FLAG.CLICKABLE)
                    self.show_obj[0].add_event_cb(click,lv.EVENT.RELEASED,None)
                self.show_obj[0].set_src("L:" + data)

    def clear_show(self):
        # lv.layer_top()
        if self.show_obj[0]:
            self.show_obj[0].delete()
        self.show_obj = [None, None]

    def message(self, text="", caption="", type=True):
        tempcard_touched = False
        msg_panel_h = 80
        temp_card = lv.tileview(lv.layer_top())
        temp_card.set_size(200,80)
        temp_card.set_style_bg_color(lv.color_hex(0x555555), lv.PART.MAIN)
        temp_card.set_style_radius(15, lv.PART.MAIN)
        temp_card.remove_flag(lv.obj.FLAG.SCROLLABLE)
        temp_card.align(lv.ALIGN.TOP_MID, 0, -40)
        temp_card.set_style_opa(230, lv.STATE.DEFAULT)

        def tempcard_ready_cb(tempcard):
            tmp = lv.anim_t()
            tmp.init()
            tmp.set_var(tempcard)
            tmp.set_custom_exec_cb(lambda a,val: tempcard.set_y(val))
            tmp.set_path_cb(lv.anim_t.path_ease_out)
            tmp.set_completed_cb(lambda a: tempcard.delete())
            tmp.set_delay(3000)
            tmp.set_time(300)
            tmp.set_values(10, -msg_panel_h)
            tmp.start()

        click_point1 = lv.point_t()
        click_point2 = lv.point_t()
        def tempcard_press_cb(e):
            nonlocal tempcard_touched, a
            tempcard = e.get_target_obj()
            lv.anim_t.custom_delete(a, None)

            if not tempcard_touched:
                lv.indev_active().get_point(click_point1)
                tempcard_touched = True
                return
            else:
                lv.indev_active().get_point(click_point2)
            j=click_point2.y-click_point1.y
            click_point1.y=click_point2.y
            if j < 0:
                tempcard.set_y(tempcard.get_y() + j)

        def tempcard_released_cb(e):
            nonlocal tempcard_touched
            tempcard = e.get_target_obj()
            tempcard_touched = False
            tmp = lv.anim_t()
            tmp.init()
            tmp.set_var(tempcard)
            tmp.set_custom_exec_cb(lambda a,val: tempcard.set_y(val))
            tmp.set_time(200)
            if tempcard.get_y() < -msg_panel_h/3:
                tmp.set_completed_cb(lambda a: tempcard.delete())
                tmp.set_values(tempcard.get_y(), -msg_panel_h)
            else:
                tmp.set_completed_cb(lambda a: tempcard_ready_cb(tempcard))
                tmp.set_values(tempcard.get_y(), 10)
            tmp.start()

        temp_card.add_event_cb(tempcard_press_cb,lv.EVENT.PRESSING,None)
        temp_card.add_event_cb(tempcard_released_cb,lv.EVENT.RELEASED,None)
        # temp_card.add_event_cb(event_cb,lv.EVENT.SHORT_CLICKED,None)


        if type:
            with open(path + '../reset/msg/bot.png', 'rb') as f:
                png_data = f.read()
        else:
            with open(path + '../reset/msg/user.png', 'rb') as f:
                png_data = f.read()

        img = lv.image_dsc_t({
            "data_size": len(png_data),
            "data": png_data,
        })
        # 55*55
        msg_icon = lv.image(temp_card)
        msg_icon.set_src(img)
        msg_icon.set_pos(10,10)

        title_lable = lv.label(temp_card)
        title_lable.set_style_text_font(self.font, 0)
        title_lable.set_text(caption)
        title_lable.set_pos(80,15)
        title_lable.set_style_text_color(lv.color_hex(0xffffffff), 0)

        txt_lable = lv.label(temp_card)
        txt_lable.set_style_text_font(self.font, 0)
        txt_lable.set_text(text)
        txt_lable.set_pos(80,45)
        txt_lable.set_style_text_color(lv.color_hex(0xffffffff), 0)

        a = lv.anim_t()
        a.init()
        a.set_var(temp_card)
        a.set_custom_exec_cb(lambda a,val: temp_card.set_y(val))
        a.set_time(300)
        a.set_path_cb(lv.anim_t.path_ease_out)
        a.set_completed_cb(lambda a: tempcard_ready_cb(temp_card))
        a.set_values(-msg_panel_h,10)
        a.start()

    def scroll_to_view(self, obj):
        if type(obj) == int:
            tmp = self.lis[obj][0]
        elif type(obj) == str:
            tmp = self.lis[self.get_lis_descrip_index(obj)][0]
        else:
            tmp = obj
        tmp.scroll_to_view(lv.ANIM.ON)# , lv.ANIM.ON

    def scroll_prev(self):
        tmp = self.get_lis_index()
        if tmp:
            self.scroll_to_view(tmp - 1)
            return True
        else:
            return False

    def scroll_next(self):
        tmp = self.get_lis_index()
        if tmp == len(self.lis) - 1:
            return False
        else:
            self.scroll_to_view(tmp + 1)
            return True

    def updata_info(self, signal_level, battery_level, ipaddr):
        if self.img_wifi is None:
            self.img_wifi = lv.image(lv.layer_top())
            self.img_wifi.set_pos(20, 220)
        if signal_level != self.signal_level:
            self.signal_level = signal_level
            self.img_wifi.set_src(self.wifi_lis[self.signal_level])

        if self.img_battery is None:
            self.img_battery = lv.image(lv.layer_top())
            self.img_battery.set_pos(198, 220)
        if battery_level != self.battery_level:
            self.battery_level = battery_level
            self.img_battery.set_src(self.batt_lis[self.battery_level])

        if self.lab_ipaddr is None:
            self.lab_ipaddr = lv.label(lv.layer_top())
            self.lab_ipaddr.align(lv.ALIGN.BOTTOM_MID,0,-30)
            self.lab_ipaddr.set_style_text_color(lv.color_hex(0xffffffff), 0)
        if ipaddr != self.ipaddr:
            self.ipaddr = ipaddr
            self.lab_ipaddr.set_text(self.ipaddr)

    def remote_msg(self, msg):
        pass
