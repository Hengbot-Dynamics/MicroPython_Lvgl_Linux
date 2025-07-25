# Copyright 2020 The NATS Authors
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from . import unats
from micropython import const
import usocket as socket
import ujson as json

INFO_OP = b'INFO'
CONNECT_OP = b'CONNECT '
PING_OP = b'PING'
PONG_OP = b'PONG'
PUB_OP = b'PUB'
SUB_OP = b'SUB'
UNSUB_OP = b'UNSUB'
OK_OP = b'+OK'
ERR_OP = b'-ERR'

_CRLF_ = b'\r\n'
_SPC_ = b' '
_EMPTY_ = b''
EMPTY = ""
PING = b'PING\r\n'
PONG = b'PONG\r\n'
PUB = b'PUB '
SUB = b'SUB '
MSG = b'MSG '

# Optimize for smaller messages and assume control lines
# of reasonable length to try to control memory usage
# in smaller devices.
DEFAULT_SCRATCH_SIZE = const(2048)
DEFAULT_MAX_CONTROL_LINE_SIZE = const(2048)
DEFAULT_MAX_PAYLOAD_SIZE = const(804800)
DEFAULT_PORT = const(4222)

# Announced on connect
CLIENT_LANG = "micropython"
CLIENT_VERSION = "0.0.1"

class NatsError(Exception):
    pass

class Client():

    def __init__(self):
        self.options = {}
        self._socket = None
        self._server_info = None
        self._ssid = 0
        self._subs = {}

        # For payloads that we receive/send.
        self._msg_buf = bytearray(DEFAULT_MAX_PAYLOAD_SIZE)

        # For assembling proto lines that will be sent.
        self._scratch = bytearray(DEFAULT_SCRATCH_SIZE)

        # For reading protocol lines.
        self._read_buf = bytearray(DEFAULT_MAX_CONTROL_LINE_SIZE)

    def connect(self,
                servers=None,
                name=None,
                pedantic=False,
                verbose=False,
                user=None,
                password=None,
                ):
        # Connect options
        self.options["verbose"] = verbose
        self.options["pedantic"] = pedantic
        if name is not None: self.options["name"] = name
        if user is not None: self.options["user"] = user
        if password is not None: self.options["pass"] = password

        # TODO: Support multiple servers and connect attempts.
        hostname, port = self._process_connect_url(servers)
        self._socket = socket.socket()
        addr = socket.getaddrinfo(servers, port)[0][-1]
        self._socket.connect(addr)

        # TCP connection OK, now send CONNECT
        self._process_connect_init()

    def _process_connect_init(self):
        # Read exactly initial INFO/PONG into the read buf.

        # FIXME: Just read into the read buffer and use startswith
        line = memoryview(self._read_buf[:4])
        self._socket.readinto(line)
        op = bytes(line)
        if INFO_OP in op:
            # TODO: Use readinto to reuse read buf.
            v = self._socket.readline()
            try:
                self._server_info = json.loads(v)
            except:
                raise NatsError("nats: error processing INFO")
        elif PING_OP in line:
            self._socket.write(PONG_OP)

            # NOTE: Recursion
            self._process_connect_init()
            return
        else:
            raise NatsError("unats: error processing INFO")

        opts = {}
        options = self.options
        opts["verbose"] = options["verbose"]
        opts["pedantic"] = options["pedantic"]
        opts["lang"] = CLIENT_LANG
        opts["version"] = CLIENT_VERSION

        # Optional
        if "user" in options: opts["user"] = options["user"]
        if "pass" in options: opts["pass"] = options["pass"]
        if "name" in options: opts["name"] = self.options["name"]

        # Send CONNECT dumping to the stream directly to avoid allocs.
        self._socket.write(CONNECT_OP)
        json.dump(opts, self._socket)
        self._socket.write(_CRLF_)
        self._socket.write(PING)

        # TODO: Use readinto
        op = self._socket.readline()

        # We can get either -ERR or PONG.
        if op.startswith(PONG_OP):
            self._socket.write(PONG)
        elif op.startswith(ERR_OP):
            n = self._socket.readinto(self._read_buf)
            line = memoryview(self._read_buf[:n])
            op = bytes(line)
            err = op.rstrip().lstrip()
            raise NatsError("nats: protocol error %s" % err.decode())
        else:
            raise NatsError("nats: error during connect")

    def publish(self, subject, payload):
        # TODO: Optimize? More syscalls instead better for memory?

        # Reuse scratch buffer to assemble the control line.
        scratch = self._scratch
        pos = len(PUB)
        scratch[:pos] = PUB
        subject_size = len(subject)

        # TODO: Allow subject to be a bytearray already to avoid
        # the extra allocation if needed.
        scratch[pos:pos+subject_size] = bytearray(subject)
        pos += subject_size
        scratch[pos:pos+1] = _SPC_
        payload_size = len(payload)

        # TODO: Better itoa for micropython
        payload_size_str = b"%d" % payload_size
        scratch[pos+1:len(payload_size_str)] = payload_size_str
        pos += len(payload_size_str)+1
        scratch[pos:pos+1] = _CRLF_
        pos += 2
        pub = memoryview(scratch[:pos])
        self._socket.write(pub)
        self._socket.write(payload)
        self._socket.write(_CRLF_)

    def subscribe(
        self,
        subject,
        cb=None,
        queue=None,
        ):
        self._ssid += 1
        ssid = self._ssid

        # Assemble the SUB proto line using scratch buffer.
        scratch = self._scratch
        sub_op_size = len(SUB)
        crlf_size = len(_CRLF_)
        sub_size = len(subject)
        sid_str = b' %d' % ssid
        sid_str_size = len(sid_str)

        pos = sub_op_size
        scratch[:pos] = SUB
        scratch[pos:pos+sub_size] = bytearray(subject)

        # TODO: Add queue

        pos += sub_size
        scratch[pos:pos+sid_str_size] = sid_str

        pos += sid_str_size
        scratch[pos:pos+crlf_size] = _CRLF_
        pos += crlf_size

        # Write into socket using a view from scratch to avoid allocation.
        buf = memoryview(scratch[:pos])
        self._socket.write(buf)
        sub = Subscription()
        sub._subject = subject
        sub._sid = ssid
        sub._queue = queue
        sub._cb = cb
        sub._nc = self

        self._subs[ssid] = sub
        return sub

    def close(self):
        self._socket.close()

    def _process_connect_url(self, connect_url):
        # TODO: Support multiple URL formats and server pool.
        return (connect_url, DEFAULT_PORT)

class Msg(object):
    __slots__ = ('subject', 'reply', 'data', 'sid')

    def __init__(self, subject='', reply='', data=b'', sid=0):
        self.subject = subject
        self.reply = reply
        self.data = data
        self.sid = sid

    def __repr__(self):
        return "<{}: subject='{}' reply='{}' data='{}...'>".format(
            self.__class__.__name__,
            self.subject,
            self.reply,
            self.data[:10].decode(),
        )
    def respond(self, payload):
        # TODO: Send to the socket directly.
        print("Respond to {} with {}", self.reply, payload)

class Subscription(object):
    def __init__(
        self,
        subject='',
        cb=None,
        queue=None,
    ):
        self._subject = subject
        self._queue = queue
        self._cb = cb
        self._nc = None
        self._sid = None

    def next_msg(self):
        nc = self._nc
        while True:
            # TODO: Use readinto and scratch buffer to save allocation.
            msg = Msg()
            line = nc._socket.readline()
            if line.startswith(MSG):
                buf = memoryview(line[len(MSG):])

                # Find subject.
                for (i, c) in enumerate(buf):
                    # SPC
                    if c == 32:
                        msg.subject = bytes(buf[:i])
                        buf = memoryview(bytes(buf[i+1:]))
                        break

                # Find sid though we will most likely not use it in this case.
                sid = None
                for (i, c) in enumerate(buf):
                    # SPC
                    if c == 32:
                        sid = int(bytes(buf[:i]))
                        buf = memoryview(bytes(buf[i+1:]))
                        break

                # Find size
                size = None
                for (i, c) in enumerate(buf):
                    # CRLF
                    if c == 10:
                        size = int(bytes(buf[:i]))
                        break

                # TODO: API where the buffer can be controlled by
                # the user.
                # Use readinto with the expected number of bytes
                # and the blocking read from the socket.
                msg_buf = self._nc._msg_buf

                # Also try to get the extra CRLF into the message buffer
                # we will remove them from the buf in the copy later.
                nc._socket.readinto(msg_buf, size+2)

                # Creates a copy from the bytes that were read.
                msg.data = msg_buf[:size]
                yield msg
            elif line.startswith(PING):
                nc._socket.write(PONG)
            elif line.startswith(INFO_OP):
                # TODO: Handle async info
                pass
            elif line.startswith(ERR_OP):
                # TODO: Handle async errors
                pass
