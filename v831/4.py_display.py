from maix import camera, display, image
import os
if not os.path.exists("/tmp/my_fifo"):
    os.system("mkfifo /tmp/my_fifo")

os.system("micropython ./4.mpy_output.py &")

while True:
    with open("/tmp/my_fifo", 'rb') as fifo:
        while True:
            data = fifo.read()
            if data:

                if len(data) == 320*240*3:
                    display.show(image.load(data, size=(320, 240)))
                    
            else:
                break