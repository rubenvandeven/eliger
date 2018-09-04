from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import telegram


class Bot(object):
    """docstring for Bot."""
    chat_ids = []
    valid_chat_ids = []

    def __init__(self, token, alarm, config):
        super(Bot, self).__init__()
        self.token = token
        self.alarm = alarm
        self.config = config

        self.chat_ids = config.get('telegram.chat_ids', [])
        self.valid_chat_ids = config.get('telegram.valid_chat_ids', [])

        self.updater = Updater(self.token)
        self.updater.dispatcher.add_handler(CommandHandler('start', self.handleStart))
        self.updater.dispatcher.add_handler(CommandHandler('help', self.handleHelp))
        self.updater.dispatcher.add_handler(CommandHandler('settings', self.handleSettings))
        self.updater.dispatcher.add_handler(CommandHandler('on', self.handleOn))
        self.updater.dispatcher.add_handler(CommandHandler('off', self.handleOff))
        self.updater.dispatcher.add_handler(CommandHandler('home', self.handleHome))
        self.updater.dispatcher.add_handler(CommandHandler('status', self.handleStatus))
        self.updater.dispatcher.add_handler(CommandHandler('siren', self.handleSiren, pass_args=True))
        self.updater.dispatcher.add_handler(CommandHandler('custom', self.handleCustom, pass_args=True))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.inlineCallbackQuery))
        self.updater.dispatcher.add_handler(CommandHandler('grant', self.handleGrant, pass_args=True))
        self.updater.start_polling()

    def start(self):
        self.updater.start_polling()

    def stop(self):
        self.updater.stop()

    def notifyStatus(self, status):
        self.broadcastMessage("Alarm is now *{}*".format(status), parse_mode=telegram.ParseMode.MARKDOWN)

    def notifyWarning(self, msg):
        self.broadcastMessage("{}".format(msg), parse_mode=telegram.ParseMode.MARKDOWN)

    def validateChat(self, bot, update):
        print("= message in {}".format(update.message.chat_id))

        # collect all chat_ids engaging, so we can validate /grant calls later
        self.addChatId(update.message.chat_id)

        if update.message.chat_id not in self.valid_chat_ids:
            print("=> Rejected chat {}".format(update.message.chat_id))
            update.message.reply_text("Sorry, you don't have access.")
            self.broadcastMessage(
                "Rejected chat {} ({})".format(update.message.chat_id, update.message.from_user.first_name),
                reply_markup = telegram.InlineKeyboardMarkup([[telegram.InlineKeyboardButton("Grant access", callback_data='/grant {}'.format(update.message.chat_id))]]))
            return False

        return True

    def broadcastMessage(self, msg, parse_mode=None, reply_markup=None):
        for chat_id in self.valid_chat_ids:
            self.updater.bot.send_message(chat_id=chat_id, text=msg, parse_mode=parse_mode, reply_markup=reply_markup)

    def inlineCallbackQuery(self, bot, update):
        query = update.callback_query
        print(update, query)
        if query.data.split(" ")[0] == "/grant":
            chat_id = int(query.data.split(" ")[1])
            msg = self.grant(chat_id, query.message.chat.first_name)
        else:
            msg = "unknown action"

        bot.edit_message_text(text=msg,
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)

    def handleStart(self, bot, update):
        if not self.validateChat(bot, update):
            return False

        keyboard = telegram.ReplyKeyboardMarkup([["/off","/home","/on"]], resize_keyboard=True)
        update.message.reply_text("Control the alarm", reply_markup=keyboard)

    def handleHelp(self, bot, update):
        if not self.validateChat(bot, update):
            return False

        update.message.reply_text("Send command /on or /off to change alarm status.")


    def handleSettings(self, bot, update):
        if not self.validateChat(bot, update):
            return False

        update.message.reply_text("Not really used, sorry!")

    def hello(self, bot, update):
        if not self.validateChat(bot, update):
            return False

        update.message.reply_text(
            'Hello {}'.format(update.message.from_user.first_name))

    def handleOn(self, bot, update):
        if not self.validateChat(bot, update):
            return False

        print("= Command On in {}".format(update.message.chat_id))
        self.alarm.queueRequest(self.alarm.requestStatusChange(1))

    def handleOff(self, bot, update):
        if not self.validateChat(bot, update):
            return False

        print("= Command Off in {}".format(update.message.chat_id))
        self.alarm.queueRequest(self.alarm.requestStatusChange(0))

    def handleHome(self, bot, update):
        if not self.validateChat(bot, update):
            return False

        print("= Command Home in {}".format(update.message.chat_id))
        self.alarm.queueRequest(self.alarm.requestStatusChange(2), name=update.message.from_user.first_name)

    def handleStatus(self, bot, update):
        if not self.validateChat(bot, update):
            return False

        print("= Command Status in {}".format(update.message.chat_id))

        update.message.reply_text("Alarm is {}".format(self.alarm.statusName))

    def handleSiren(self,bot,update, args):
        if not self.validateChat(bot, update):
            return False

        print("= Command Siren in {}".format(update.message.chat_id))
        if len(args) < 1:
            try:
                value = "on" if self.alarm._svle > 0 else "off"
            except AttributeError as e:
                value = "unknown"
            update.message.reply_text(
                "Siren currently **{}**\n\n/siren on - Enable siren\n/siren off - Disable siren".format(value),
                parse_mode=telegram.ParseMode.MARKDOWN
                )
        else:
            arg = args[0].lower()
            if arg == "off":
                value = 0
            elif arg == "on":
                value = 1
            elif int(arg) == 0:
                value = 0
            else:
                value = 1

            req = "{{\"sg_svle\":\"{}\"}}".format(value)
            update.message.reply_text("Send: {}".format(req))
            self.alarm.queueRequest(req)

    def handleCustom(self, bot, update, args):
        if not self.validateChat(bot, update):
            return False
        print("= Command CUSTOM in {}".format(update.message.chat_id))
        print(args)
        if len(args) < 1:
            update.message.reply_text("Requires some code")

        cmd = " ".join(args)
        update.message.reply_text("Send: {}".format(cmd))
        self.alarm.queueRequest(cmd)

    def addChatId(self, chat_id):
        if chat_id not in self.chat_ids:
            self.chat_ids.append(chat_id)
            self.config.set('telegram.chat_ids', self.chat_ids)

    def addValidChatId(self, chat_id):
        if chat_id not in self.valid_chat_ids:
            self.valid_chat_ids.append(chat_id)
            self.config.set('telegram.valid_chat_ids', self.valid_chat_ids)

    def grant(self, chat_id, from_name=""):
        chat_id = int(chat_id)
        if chat_id in self.valid_chat_ids:
            return "Already added {}".format(chat_id)
        elif chat_id not in self.chat_ids:
            return "Unknown chat id '{}'".format(chat_id)
        else:
            self.addValidChatId(chat_id)
            self.updater.bot.send_message(chat_id=chat_id, text="{} granted you control over the alarm".format(from_name))
            return "Granted '{}' control over alarm".format(chat_id)

    def handleGrant(self, bot, update, args):
        if not self.validateChat(bot, update):
            return False

        for arg in args:
            msg = self.grant(chat_id, update.message.from_user.first_name)
