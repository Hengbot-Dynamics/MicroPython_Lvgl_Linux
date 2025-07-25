import ffi
import lvgl as lv

path = __file__[:__file__.rfind('/')+1]
libc = ffi.open(path + "libspilcd.so")

SPILCD_flush = libc.func("v", "SPILCD_flush", "iiiiP")
SPILCD_init = libc.func("i", "SPILCD_init", "")
SPILCD_blwrite = libc.func("v", "DEV_BLPWM_Write", "i")
SPILCD_blread = libc.func("f", "DEV_BLPWM_Read", "")

def lcd_init():
    SPILCD_init()

def lcd_flush(x1,y1,x2,y2,data):
    SPILCD_flush(x1, y1, x2, y2, data)

class Display:
    def __init__(self, width, height):
        lcd_init()
        self.width = width
        self.height = height
        self.buf_size = width * height * 2
        self.buf1 = bytearray(self.buf_size)
        self.buf2 = bytearray(self.buf_size)

        self.disp_drv = lv.display_create(self.width, self.height)
        self.disp_drv.set_color_format(lv.COLOR_FORMAT.RGB565)
        self.disp_drv.set_buffers(self.buf1, self.buf2, self.buf_size, lv.DISPLAY_RENDER_MODE.PARTIAL)
        self.disp_drv.set_flush_cb(self.flush)

    def set_duty(self, high_edge_time):
        SPILCD_blwrite(high_edge_time)

    def get_duty(self):
        return int(SPILCD_blread()*100)

    def flush(self, disp, area, color_p):
        data_view = color_p.__dereference__(self.buf_size)
        data_bytes = bytes(data_view)
        lcd_flush(area.x1,area.y1,area.x2,area.y2,data_bytes)

        disp.flush_ready()
