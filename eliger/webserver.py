import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, alarm):
        self.alarm = alarm

    def get(self):
        newStatus = self.get_query_argument('ctrl', default=alarmOn)
        # if newStatus != alarmOn:
        #     alarmOn = min(3,max(0,int(newStatus)))
        #     self.write("Changed!")
        # self.write("Current status is {}".format(alarmOn))
        self.write("""
        <a href="?ctrl=1">On</a>
        <a href="?ctrl=2">Home</a>
        <a href="?ctrl=0">Off</a>
        """)
        settings = self.alarm.getAllConfig()
        self.write("<dl>")
        for setting, value in settings:
            self.write("<dt>{}</dt><dd>{}</dd>".format(setting, value))
        self.write("</dl>")

def make_server(alarm):
    return tornado.web.Application([
        (r"/", MainHandler, dict(alarm=alarm)),
    ])
