from maix import camera, display, image
import os,inspect
if not os.path.exists("/tmp/my_fifo"):
    os.system("mkfifo /tmp/my_fifo")

def code(func):
    source_lines = inspect.getsource(func).split('\n')[2:]
    indent = len(source_lines[0]) - len(source_lines[0].lstrip())
    str_func = '\n'.join([line[indent:] for line in source_lines if line.strip()])
    with open('mpy_tmp.py', 'w') as file:
        file.write(str_func)

@code
def mpy_code():
    import lvgl as lv
    import os
    try:
        os.stat('/tmp/my_fifo')
    except OSError:
        os.system('mkfifo /tmp/my_fifo')

    class Display:
        def __init__(self, width, height):
            self.width = width
            self.height = height
            self.buf_size = width * height * 3
            self.buf1 = bytearray(self.buf_size)
            self.buf2 = bytearray(self.buf_size)

            self.disp_drv = lv.display_create(self.width, self.height)
            self.disp_drv.set_color_format(lv.COLOR_FORMAT.RGB888)
            self.disp_drv.set_buffers(self.buf1, self.buf2, self.buf_size, lv.DISPLAY_RENDER_MODE.FULL)
            self.disp_drv.set_flush_cb(self.flush)

        def flush(self, disp, area, color_p):
            data_view = color_p.__dereference__(self.buf_size)
            data_bytes = bytes(data_view)
            i = 0
            while True:
                try:
                    with open("/tmp/my_fifo", 'wb') as fifo:
                        fifo.write(data_bytes)
                    break
                except Exception as e:
                    if i >= 3:
                        break
                    i += 1
            
            disp.flush_ready()

    if __name__ == '__main__':
        import time
        from lv_utils import event_loop
        lv.init()

        event_loop = event_loop()
        display = Display(320, 240)

        btn = lv.button(lv.screen_active())
        btn.set_pos(50, 50)
        btn.set_size(120, 50)

        label = lv.label(btn)
        label.set_text("Button")
        label.center()
        
        a = 0
        b = 0
        while True:
            btn.set_pos(a, b)
            a+=1
            b+=1
            if a > 200:
                a = 0
                b = 0
            time.sleep_ms(50)

os.system("micropython ./mpy_tmp.py &")

while True:
    with open("/tmp/my_fifo", 'rb') as fifo:
        while True:
            data = fifo.read()
            if data:

                if len(data) == 320*240*3:
                    display.show(image.load(data, size=(320, 240)))
                    
            else:
                break