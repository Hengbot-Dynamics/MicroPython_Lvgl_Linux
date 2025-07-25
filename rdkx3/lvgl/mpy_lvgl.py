import lvgl as lv

path = __file__[:__file__.rfind('/')+1]

if __name__ == '__main__':
    import time
    from lv_utils import event_loop
    import fs_driver

    lv.init()
    event_loop = event_loop()
    fs_drv = lv.fs_drv_t()
    fs_driver.fs_register(fs_drv, 'L')

    import drive

    import lv_pm
    pm = lv_pm.pm()
    pm.path = path
    
    import page
    pm.open_page(0)
    import rmpyc
    rmpyc.udp()

    # 开启nats服务接收数据
    rmpyc.exec()

    # 显示前将屏幕上的内容清除
    pm.clear_show()

    while True:
        now_time = time.time()

        ''' 自定义则去掉这个
            if now_time - pm.back_counter > 30:
                if not pm.show_obj[0]:
                    pm.show("./reset/start.gif")
            else:
                if pm.show_obj[1] in ("gif", "express"):
                    pm.clear_show()
            if now_time - pm.back_counter > 0.2 and pm.show_obj[1] == "cam":
                pm.clear_show()
        '''

        time.sleep_ms(500)
