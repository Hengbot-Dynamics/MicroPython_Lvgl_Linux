
import uos
import unats as nats
import io

import lv_pm
pm = lv_pm.pm()

class WebreplWrapper(io.IOBase):
    def __init__(self, nc):
        self.nc = nc
        self.sub = nc.subscribe(b"mpy.repl.input")
        self.datalis = []

    def write(self, buf):
        nc.publish(b"mpy.repl.output", buf)
        return len(bytes(buf))

    def read(self, n):
        try:
            if len(self.datalis) == 0:
                result = self.sub.next_msg().__next__()
                result = bytes(result.data).decode()
                if len(result) > 50:
                    exec(result, globals(), globals())
                    nc.publish(b"mpy.repl.output", b'>>> ')
                    return None
                elif result == None:
                    return None
                else:
                    for byte in result:
                        self.datalis.append(byte)
            return self.datalis.pop(0)
        except Exception as e:
            print(e)

nc = nats.connect("127.0.0.1")
Webrepl = WebreplWrapper(nc)
uos.dupterm(Webrepl)