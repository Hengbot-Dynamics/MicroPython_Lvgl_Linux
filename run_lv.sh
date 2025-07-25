if pgrep -f "micropython mpy_lvgl.py" > /dev/null; then
    kill $(pgrep -f "micropython mpy_lvgl.py") # 终止进程
    echo "micropython mpy_lvgl.py 进程以kill掉"
else
    echo "micropython mpy_lvgl.py 进程未运行"
fi

pkill -f "micropython -X heapsize=6553600 mpy_lvgl.py"


cd /root/hengbot_lvgl/rdkx3/lvgl &&
chmod 777 ./micropython &&
./micropython -X heapsize=6553600 mpy_lvgl.py