# 零. Examples（示例）

| 示例                                                  | 说明                                           |
| ----------------------------------------------------- | ---------------------------------------------- |
| [0.framebuffer.py](v831/0.framebuffer.py)             | 利用帧缓冲显示 Hello World！                   |
| [1.file_system.py](v831/1.file_system.py)             | 利用文件系统显示 GIF 和中文                    |
| [2.key.py](v831/2.key.py)                             | 按键输入                                       |
| [3.msdev.py](v831/3.msdev.py)                         | 鼠标输入                                       |
| [4.mpy_output.py](v831/4.mpy_output.py)               | 将图像显示数据利用命名管道输出                 |
| [4.py_display.py](v831/4.py_display.py)               | 使用 python 将图像显示数据从命名管道取出并显示 |
| [5.py_single_display.py](v831/5.py_single_display.py) | 单文件整合例程 4                               |
| [6.mpy_widgets.py](v831/6.mpy_widgets.py)             | 常用控件                                       |

例程 4 需要一起运行，[4.mpy_output.py](v831/4.mpy_output.py) 在 micropython 中运行，[4.py_display.py](v831/4.py_display.py) 在 python 中运行

[lib](lib) 从 [micropython-lib](https://github.com/micropython/micropython-lib) 中提取了 os 模块，比  micropython 自带的 os 模块 多提供 popen 等功能

```python
import os

rt=os.popen("ls")
print(rt.read())
```

v831 需将 libffi.so.8 ld-musl-armhf.so.1 复制至 /usr/lib `cp libffi.so.8 /usr/lib`  `cp ld-musl-armhf.so.1 /usr/lib`

rdkx3 不使用 Framebuffer

# 一. Framebuffer Driver（利用帧缓冲显示）

![framebuffer](resource/framebuffer.png)

Usage（用法）

```python
disp = lv.linux_fbdev_create()
lv.linux_fbdev_set_file(disp, "/dev/fb0")
```

# 二. File System Interfaces（文件系统接口）

Usage（用法）

```python
import fs_driver
fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'L')
```

### 1. 显示 GIF

![GIF](resource/GIF.gif)

##### (1) 使用文件系统

```python
img = lv.gif(lv.screen_active())
img.set_src( "L:/root/astronaut_ezgif.gif")
```

##### (2) 从 bytes 中创建

```python
img_bulb_gif = lv.image_dsc_t({
    "header": { "w": 0, "h": 0,  "cf": lv.COLOR_FORMAT....},
    "data_size": 0,
    "data": gif_data,
})

img = lv.gif(lv.screen_active())
img.set_src( img_bulb_gif)
```

### 2. 显示中文

在 [Font Converter — LVGL](https://lvgl.io/tools/fontconverter) 中，根据提示填写相关信息，将 .ttf 字体文件中指定字符转换为 .bin

alibaba.bin 中处理了'你''好'两个字符

![zh](resource/zh.jpg)

```python
myfont_cn = lv.binfont_create('L:/root/alibaba.bin')
label = lv.label(btn)
label.set_style_text_font(myfont_cn, 0)
label.set_text("你好")
```

# 三. Input device interface（输入设备接口）

创建输入设备

```python
indev = lv.indev_create()
indev.set_type(lv.INDEV_TYPE....)
indev.set_read_cb(read_cb)

def read_cb(indev, data) -> int:
```

### 1. 按键输入

![key](resource/key.gif)

按钮分配给屏幕的特定坐标。 如果按下按钮，它将模拟按下指定坐标。

```python
indev = lv.indev_create()
indev.set_type(lv.INDEV_TYPE.BUTTON)
indev.set_read_cb(read_cb)
point = lv.point_t()
point.x = x
point.y = y
indev.set_button_points(point)

def read_cb(indev, data) -> int:
    data.state = lv.INDEV_STATE.PRESSED if ((is_pressed() & 1) == 1) else lv.INDEV_STATE.RELEASED
    return 0
```

示例仅供演示按钮输入，有时会无法切换，推荐使用下面的方式实现切换

```python
button.scroll_to_view(lv.ANIM.ON)
```

### 2. 鼠标输入

![ms](resource/ms.gif)

```python
indev = lv.indev_create()
indev.set_type(lv.INDEV_TYPE.POINTER)
indev.set_read_cb(read_cb)

def read_cb(indev, data) -> int:
    data.point.x += getDeltaX()
    data.point.y -= getDeltaY()
    # Handle coordinate overflow cases
    data.point.x = min(data.point.x, lv.screen_active().get_width() - 1)
    data.point.y = min(data.point.y, lv.screen_active().get_height() - 1)
    data.point.x = max(data.point.x, 0)
    data.point.y = max(data.point.y, 0)
    data.state = lv.INDEV_STATE.PRESSED if ((is_pressed() & 1) == 1) else lv.INDEV_STATE.RELEASED
    return 0
```

# 四. Display interface（显示接口）

创建显示

```python
buf_size = width * height * ...
buf1 = bytearray(buf_size)
buf2 = bytearray(buf_size)

disp_drv = lv.display_create(width, height)
disp_drv.set_color_format(lv.COLOR_FORMAT....)
disp_drv.set_buffers(buf1, buf2, buf_size, lv.DISPLAY_RENDER_MODE....)
disp_drv.set_flush_cb(flush_cb)

def flush_cb(disp, area, color_p):
    data_view = color_p.__dereference__(self.buf_size)
    data_bytes = bytes(data_view)
    display(data_bytes)
    disp.flush_ready()
```

# 五.Foreign Function Interface（语言交互接口）

```python
import ffi
libc = ffi.open("./libspilcd.so")

SPILCD_flush = libc.func("v", "SPILCD_flush", "iiiiP")
SPILCD_init = libc.func("i", "SPILCD_init", "")

SPILCD_init()
SPILCD_flush(x1, y1, x2, y2, data)
```

提供 RDK X3 SPI LCD 显示的[示例](rdkx3/spilcd)，[WiringPi](https://gitee.com/study-dp/WiringPi) 当前使用 commit e927bf0409e9466e0e5eb54061dfcfe79becaefc

使用 `gcc -shared -o libspilcd.so SPILCD.c rgb2bgr.c DEV_Config.c -lwiringPi -fPIC ; ./micropython mpy_lvgl.py` 编译并执行


# udp控制图层移动缩放旋转

报文格式
```json
{
  "eye_iris": {
    "pos_y": 0,
    "pos_z": 0,
    "rot_x": 0,
    "scale_y": 1.0,
    "scale_z": 1.0
  },
  "eye_pupil": {
    "pos_y": 0,
    "pos_z": 0,
    "rot_x": 0,
    "scale_y": 1.0,
    "scale_z": 1.0
  },
  "eye_upper": {
    "pos_z": 0,
    "scale_z": 1.0
  },
  "eye_lower": {
    "pos_z": 0,
    "scale_z": 1.0
  }
}

```

udp转发端口8770

参考链接：https://hengbothome.feishu.cn/wiki/Uht5wchICiW2vBksfRycMVksnp0?from=from_copylink
