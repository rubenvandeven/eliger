# eLIGER - Automate the eTIGER alarm

Stop the eTIGER Secual Box v2 from phoning home & control it trough Telegram (or integrate it with your home automation)

Possible works for other devices from eTIGER, MaxSmart (SG2?) or Chuango as well.

## Why?

I own an eTIGER Secual Box v2. Out of dissatisfaction with the app I started exploring the possibility to create my own app.

It turned out the app sends passwords unencrypted & the box itself communicates trough an unencrypted TCP stream with a max818 server in China. Sublime security... 🤦

Nevertheless, this made it easy to hijack the Secual Box's connection and setup a private server using [MITM](https://en.wikipedia.org/wiki/Man-in-the-middle_attack).

## Telegram Commands

See [telegrambot.py](eliger/telegrambot.py) for all commands.

* __/on__: Enable alarm
* __/off__: Disable alarm.
* __/home__: Set alarm to _home_ mode.
* __/status__: Inquery whether alarm is on/off.
* __/siren [on|off]__: enable or disable the sound of the siren. Usefull when triggering the alarm for testing.
* __/custom__: Send anything you want over the TCP stream to the Secual Box. Primarily used to set variables that do not have their own command (which are most)
* __/grant__: Grant another chat control over the alarm. Note that this person can also issue grants.
* __/start/help/settings__: Commands implemented for Telegram's sake.

The three commands to set the alarm status (on/off/home) can quickly be sent trough [the custom keyboard](https://core.telegram.org/bots#keyboards) that is sent on _/start_.

## Start the server

Setup your computer as WiFi hotspot (I use a [rpi with hostapd](https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md) ) and use iptables to redirect traffic. Since we use a bridged interface, physdev module is needed to [capture the traffic](http://bwachter.lart.info/linux/bridges.html):

```bash
sudo iptables -t nat -A PREROUTING -m physdev --physdev-in wlan0 -p tcp --dport 8400 -j REDIRECT --to-port 8000
```

Copy the `eliger-config.example.json` to `eliger-config.json` and edit for your needs.

* The `telegram.token` is the token of your [telegram bot](https://core.telegram.org/bots#6-botfather).
* The `valid_chat_ids` is an array of telegram chat_ids that is allowed to control the alarm. setting one 'superuser' in the config should be good enough, as other chats can be confirmed by this person. Probably the easiest way to resolve these is to start the server using `python3 bin/eliger_server`: then use your telegram to chat with the bot. The chat_id should be outputted to the terminal.

To have some failsafe, run eLiger trough supervisord:

```bash
sudo ln -s /home/pi/eliger/supervisor.conf /etc/supervisor/conf.d/etiger.conf
sudo supervisorctl reread
sudo supervisorctl update
```

## TODO

* Integrate with home-assistant
    + automatically disable when I get home.
    + send a reminder to enable alarm when everybody leaves the house
    + do whatever you want.
* Create commands to implement other settings (phone numbers/alarm duration/zones/etc.)
    + This means figuring out all the parameters sent by the Box trough its initial json.
* Track who changes the status
