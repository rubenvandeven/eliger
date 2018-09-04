import datetime

class Alarm(object):
    """
    Model representing the Alarm status.

    Stored in memory only as it isconfigured on first call to server
    """
    configuredStatus = 0

    # statusListeners are called on change of status (sg_ctrl)
    statusListeners = []
    # warning listeners are called on an incomming warning message (sg_warn)
    warningListeners = []
    eventLog = []

    _ctrl =0

    def __init__(self):
        super(Alarm, self).__init__()

    @property
    def status(self):
        return self._ctrl

    @status.setter
    def status(self, value):
        status = min(2,max(0,int(value)))
        if status != self._ctrl:
            self._ctrl = status
            self.callStatusListeners()

    @property
    def statusName(self):
        names = ['off', 'on', 'home']
        return names[self.status]

    def callStatusListeners(self):
        for l in self.statusListeners:
            l.notifyStatus(self.statusName)

    def callWarningListeners(self, warningCode):
        for l in self.warningListeners:
            l.notifyWarning(warningCode)

    def triggerEvent(self, msg):
        self.eventLog.append((datetime.datetime.now(), msg))
        if(len(self.eventLog) > 20):
            self.eventLog.pop(0)

        texts = {
            "4" : "_Lost mainline power_",
            "5" : "_Mainline power restored_",
            "12-1" : "_Enable alarm using remote_",
            "13-1" : "_Alarm in Home mode_",
            "14-1" : "_Disable alarm using remote_",
            "15-1" : "*SOS*",
            "17-1" : "*Burglar alert!!*", # TODO make sure this repeatedly sends until alarm is disabled
        }
        if msg in texts:
            text = texts[msg]
        else:
            text = msg

        self.callWarningListeners(text)

    def is_configred(self):
        return self.configuredStatus == 7

    def setConfig0(self, productId, data):
        """
        Configure using first call data

        config that comes with sg_status=0

        productid: Id of prodct
        sg_ctrl: alarm on (1)/off (0)/home (2)
        sg_aate: ?? (eg: "0")
        sg_acpe: ?? (eg: "1")
        sg_lcae: ?? (eg: "0")
        sg_gfae: ?? (eg: "0")
        sg_kpte: ?? (eg: "0")
        sg_svle: Alarm siren enable/disable (eg: "1")
        sg_wswidtchen: ?? (eg: "0")
        sg_wtoneen: ?? (eg: "0")
        sg_bswitchen: ?? (eg: "1")
        sg_btoneen: ?? (eg: "1")
        sg_wlswitchen: ?? (eg: "1")
        sg_wltoneen: ?? (eg: "1")
        sg_armupen: ?? (eg: "0")
        sg_disarmupen: ?? (eg: "0")
        sg_gsmen: ?? (eg: "1")
        sg_gpsen: ?? (eg: "0")
        sg_telen: ?? (eg: "0")
        sg_dateformat: ?? (eg: "1")
        sg_callrecycle: ?? (eg: "3")
        sg_rtimes: ?? (eg: "3")
        sg_sinretime: Siren duration on alarm in minutes (eg: "3")
        sg_backligh: ?? (eg: "8")
        sg_delayentry: Entry delay in seconds (eg: "0")
        sg_delayexit: Exit delay in seconds (eg: "0")
        sg_auarmtime: ?? (eg: "0000")
        sg_audisarmtime: ?? (eg: "0000")
        sg_proseries: Product series? (eg: "054B48363543188324")
        sg_admincode: SMS passcode for admin (eg: "123456")
        sg_usercode: SMS passcode for user (eg: "1234")
        sg_duresscode: ?? (eg: "8888")
        sg_doorcode: ?? (eg: "0000")
        sg_userid: ?? (eg: "0000")
        sg_heartnum: ?? (eg: "00300")
        sg_about: Probably code version (eg: "ver100")
        sg_language: English? (eg: "0001")
        sg_languageall: ?? (eg: "1")
        sg_gprsapn: ?? (eg: "cmnet")
        sg_gprsip: ?? (eg: "112.99.103.195")
        sg_gprsloip: ?? (eg: "54.67.63.65")
        sg_gprsport: ?? (eg: "8400")
        sg_gprsloport: ?? (eg: "8400")
        sg_gprsmode: ?? (eg: "1")
        sg_wifiSSID: Configured SSID of wifi (eg: "wifiSSID")
        sg_wifisn: Configured password of wifi (eg: "wifiPassword")
        sg_wifiip: Host called by box (eg: "max818.com")
        sg_wifiloip: Resolved host of wifiip (eg: "54.67.63.65")
        sg_wifiport: ?? (eg: "8400")
        sg_wifiloport: ?? (eg: "8400")
        sg_wifimode: ?? (eg: "1")
        sg_netip: ?? (eg: "112.99.103.195")
        sg_netloip: ?? (eg: "54.67.63.65")
        sg_netport: ?? (eg: "8400")
        sg_netloport: ?? (eg: "8400")
        sg_netmode: ?? (eg: "1")
        sg_netdhcpen: ?? (eg: "0")
        """

        self._productId = productId
        self._ctrl = data.get("sg_ctrl")
        self._aate = data.get("sg_aate")
        self._acpe = data.get("sg_acpe")
        self._lcae = data.get("sg_lcae")
        self._gfae = data.get("sg_gfae")
        self._kpte = data.get("sg_kpte")
        self._svle = data.get("sg_svle")
        self._wswidtchen = data.get("sg_wswidtchen")
        self._wtoneen = data.get("sg_wtoneen")
        self._bswitchen = data.get("sg_bswitchen")
        self._btoneen = data.get("sg_btoneen")
        self._wlswitchen = data.get("sg_wlswitchen")
        self._wltoneen = data.get("sg_wltoneen")
        self._armupen = data.get("sg_armupen")
        self._disarmupen = data.get("sg_disarmupen")
        self._gsmen = data.get("sg_gsmen")
        self._gpsen = data.get("sg_gpsen")
        self._telen = data.get("sg_telen")
        self._dateformat = data.get("sg_dateformat")
        self._callrecycle = data.get("sg_callrecycle")
        self._rtimes = data.get("sg_rtimes")
        self._sinretime = data.get("sg_sinretime")
        self._backligh = data.get("sg_backligh")
        self._delayentry = data.get("sg_delayentry")
        self._delayexit = data.get("sg_delayexit")
        self._auarmtime = data.get("sg_auarmtime")
        self._audisarmtime = data.get("sg_audisarmtime")
        self._proseries = data.get("sg_proseries")
        self._admincode = data.get("sg_admincode")
        self._usercode = data.get("sg_usercode")
        self._duresscode = data.get("sg_duresscode")
        self._doorcode = data.get("sg_doorcode")
        self._userid = data.get("sg_userid")
        self._heartnum = data.get("sg_heartnum")
        self._about = data.get("sg_about")
        self._language = data.get("sg_language")
        self._languageall = data.get("sg_languageall")
        self._gprsapn = data.get("sg_gprsapn")
        self._gprsip = data.get("sg_gprsip")
        self._gprsloip = data.get("sg_gprsloip")
        self._gprsport = data.get("sg_gprsport")
        self._gprsloport = data.get("sg_gprsloport")
        self._gprsmode = data.get("sg_gprsmode")
        self._wifiSSID = data.get("sg_wifiSSID")
        self._wifisn = data.get("sg_wifisn")
        self._wifiip = data.get("sg_wifiip")
        self._wifiloip = data.get("sg_wifiloip")
        self._wifiport = data.get("sg_wifiport")
        self._wifiloport = data.get("sg_wifiloport")
        self._wifimode = data.get("sg_wifimode")
        self._netip = data.get("sg_netip")
        self._netloip = data.get("sg_netloip")
        self._netport = data.get("sg_netport")
        self._netloport = data.get("sg_netloport")
        self._netmode = data.get("sg_netmode")
        self._netdhcpen = data.get("sg_netdhcpen")

        self.configuredStatus += 1

    def setConfig1(self, data):
        """
        Config that comes with status=1

        Not sure yet what most mean (something todo with devices connected)

        "sg_localrf":"188324",
        "sg_tele":"0,4,,,,,,",
        "sg_msm":"0,4,,,,,,",
        "sg_cms":"0,1,",
        "sg_remmote":"0,9,9ADB81,",
        "sg_rfid":"0,49,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",
        "sg_zone":"0,49,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
        """

        self._localrf = data.get("sg_localrf")
        self._tele = data.get("sg_tele").split(",")
        self._msm = data.get("sg_msm").split(",")
        self._cms = data.get("sg_cms").split(",")
        self._remmote = data.get("sg_remmote").split(",")
        self._rfid = data.get("sg_rfid").split(",")
        self._zone = data.get("sg_zone").split(",")

        self.configuredStatus += 2

    def setConfig2(self, data):
        """
        Config that comes with status=2

        The names configured for the zones (triggers) & remotes

        "sg_remotename":"0,9,,,,,,,,,,,",
        "sg_idname":"0,49,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",
        "sg_zonename":"0,49,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
        """

        self._remotename = data.get("sg_remotename").split(",")
        self._idname = data.get("sg_idname").split(",")
        self._zonename = data.get("sg_zonename").split(",")

        self.configuredStatus += 4

    def addStatusListener(self, listenerObject):
        self.statusListeners.append(listenerObject)
        pass

    def addWarningListener(self, listenerObject):
        self.warningListeners.append(listenerObject)
        pass

    def getAllConfig(self):
        items = self.__dict__.items()
        #[print(f"attribute: {k}    value: {v}") for k, v in items]
        return items

    msgQueue = []
    def queueRequest(self, msg, name="unknown"):
        if msg not in self.msgQueue:
            self.msgQueue.append((msg, name))
            return True
        return False

    def requestStatusChange(self, status):
        status = min(2, max(0, int(status)))
        return "{{\"sg_ctrl\":\"{}\"}}".format(status)

    def updateFromMsg(self, msg):
        if 'sg_ctrl' in msg.data['msg']:
            self.status = msg.data['msg']['sg_ctrl']

        #TODO: put all setConfig here as well
