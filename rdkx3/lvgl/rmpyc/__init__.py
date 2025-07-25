import _thread
def exec():
    def fun():
        from . import mpy_exec
    _thread.start_new_thread(fun,())

def repl():
    def fun():
        from . import mpy_repl
    _thread.start_new_thread(fun,())

def udp():
    def fun():
        from . import mpy_udp
    _thread.start_new_thread(fun,())