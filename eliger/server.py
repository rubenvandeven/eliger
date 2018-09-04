import argparse
from .model import Alarm
from .config import Config
from .tcpserver import AlarmServer
from .webserver import make_server
from .telegrambot import Bot
import json

import tornado.ioloop

def main():
    parser = argparse.ArgumentParser(
        description='Start server to controll eTiger Secual Box V2'
    )
    parser.add_argument('--configFile', '-C', default="eliger-config.json", type=str, help='json file for configuration of ports & tokens.')
    parser.add_argument('--statusFile', '-S', default="eliger-status.json", type=str, help='json file to store runtime status configuration.')

    args = parser.parse_args()

    with open(args.configFile, 'r') as fp:
        settings = json.load(fp)

    alarm = Alarm()
    config = Config(args.statusFile, settings)
    srv = AlarmServer()
    srv.set_alarm_instance(alarm)
    srv.set_config(config)
    srv.listen(settings['tcpPort'])
    http = make_server(alarm=alarm)
    http.listen(settings['httpPort'])

    if len(settings['telegram.token']) > 0:
        bot = Bot(token=settings['telegram.token'], alarm=alarm, config=config)
        bot.start()
        alarm.addStatusListener(bot)
        alarm.addWarningListener(bot)

    print("Start listening on {}, http on port {}".format(settings['tcpPort'], settings['httpPort']))
    tornado.ioloop.IOLoop.current().start()

    if bot:
        bot.stop()
