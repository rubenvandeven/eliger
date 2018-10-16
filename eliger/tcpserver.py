from tornado.tcpserver import TCPServer
from tornado.iostream import StreamClosedError

from urllib.parse import parse_qs
import json

class AlarmServer(TCPServer):
    def set_alarm_instance(self, alarm):
        # alarm: model/Alarm
        self.alarm = alarm

    def set_config(self, config):
        # config: config/Config
        self.config = config

    async def handle_stream(self, stream, address):
        print("Connection from", address)
        self.alarm.queueRequest("welcome", name="system")

        while True:
            try:
                if len(self.alarm.msgQueue):
                    response, responseTriggererName = self.alarm.msgQueue.pop(0)
                else:
                    requestCode = 0 # 1 seems to force resend of previous message, rather than trigger config load
                    try:
                        response = '{{"productid":"{}","code":{},"msg":"0"}}\n\r'.format(self.alarm.productId, requestCode)
                    except AttributeError as e:
                        response = '{{"code":{},"msg":"0"}}\n\r'.format(requestCode)

                    responseTriggererName = "unknown"

                await stream.write(str.encode(response))
                print("> {}".format(response))

                data = await stream.read_until(b"\n")
                msg = Message(data)
                print("< {}".format(msg))

                if msg.data['sg_status'] == "0":
                    print("! set config 0")
                    self.alarm.setConfig0(msg.data['productid'], msg.data['msg'])
                if msg.data['sg_status'] == "1":
                    print("! set config 1")
                    self.alarm.setConfig1(msg.data['msg'])
                if msg.data['sg_status'] == "2":
                    print("! set config 2")
                    self.alarm.setConfig2(msg.data['msg'])
                if msg.data['sg_status'] == "8":
                    print("! alarm status has changed")
                    self.alarm.triggerEvent("Alarm status has been changed by {}".format(responseTriggererName))
                    # self.alarm.status =

                if 'sg_warn' in msg.data['msg']:
                    print('! Message {}'.format(msg.data['msg']) )
                    self.alarm.triggerEvent(msg.data['msg']['sg_warn'])

                self.alarm.updateFromMsg(msg)

            except StreamClosedError:
                break

class Message(object):
    """docstring for Message."""
    data = {}

    def __init__(self, queryString):
        data = parse_qs(queryString)

        for k in data:
            # Box never sends data another way, so let's simplify it:
            self.data[k.decode("utf-8")] = data[k][0].decode("utf-8")

        if 'msg' in self.data:
            self.data['msg'] = json.loads(self.data['msg'])

    def __str__(self):
        output = "Message: "
        for k in self.data:
            output += "{}: {}".format(k, str(self.data[k]))
        return output
