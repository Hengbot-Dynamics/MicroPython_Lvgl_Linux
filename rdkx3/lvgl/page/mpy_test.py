import lvgl as lv
import lv_pm

pm = lv_pm.pm()


_test_ = 2


# 测试图层显示
if _test_ == 1:

    descrip_ = "ui_test"


    def unLoad(page):
        print("eyes_unLoad: unLoad")


    # 创建UI横向列表
    def create_test(page):
        print("create ui_test page")

        def img_event_cb(event):
            pm.open_page(descrip_)

        # 暂时使用reset/setting/setting_cartoon.png作为底图，后续底图更换成透明底图，任一图层都在该底图上叠加
        pm.create_page_lis(img_event_cb, pm.path + 'reset/setting/setting_cartoon.png')

        # UI 素材绝对位置
        pm.create_png(pm.path+'/root/hengbot_lvgl/rdkx3/lvgl/reset/layer/250228/1_immobility_01_forefront.png', "1_immobility")
        pm.create_png(pm.path+'/root/hengbot_lvgl/rdkx3/lvgl/reset/layer/250228/2_immobility_02_forefront.png', "2_immobility")

        pm.create_page_end()


    page = lv_pm.page(create_test, unLoad, descrip=descrip_)



# 测试图层堆叠与控制
elif _test_ == 2:

    descrip_ = "layer"

    # 在屏幕中间创建多个图层，可为控制
    def create_layer(page):

        # 从底图依次叠加
        layer_path_list = [
            pm.path + '/root/hengbot_lvgl/rdkx3/lvgl/reset/layer/250228/7_immobility_03_backmost.png',

            # pm.path + '/root/hengbot_lvgl/rdkx3/lvgl/reset/layer/250228/test_2.png',
            # pm.path + '/root/hengbot_lvgl/rdkx3/lvgl/reset/layer/250228/test_3.png',
            pm.path + '/root/hengbot_lvgl/rdkx3/lvgl/reset/layer/250228/6_eye_iris_04.png',

            pm.path + '/root/hengbot_lvgl/rdkx3/lvgl/reset/layer/250228/5_eye_pupil_03.png',
            pm.path + '/root/hengbot_lvgl/rdkx3/lvgl/reset/layer/250228/4_eye_lower_02.png',
            pm.path + '/root/hengbot_lvgl/rdkx3/lvgl/reset/layer/250228/3_eye_upper_01.png',

            # pm.path + '/root/hengbot_lvgl/rdkx3/lvgl/reset/layer/250228/test_1.png',
            pm.path + '/root/hengbot_lvgl/rdkx3/lvgl/reset/layer/250228/2_immobility_02_forefront.png',

            pm.path + '/root/hengbot_lvgl/rdkx3/lvgl/reset/layer/250228/1_immobility_01_forefront.png',
        ]

        # 创建图层堆叠
        pm.create_png_layers(layer_path_list, descrip_)


    def unLoad(page):
        print("layer_unLoad: unLoad")

    page = lv_pm.page(create_layer, unLoad, descrip=descrip_)