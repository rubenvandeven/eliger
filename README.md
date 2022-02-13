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

## UPDATE 2022

Max818.com is down, which is used by the box to resolve some ip (the traffic to which we then capture).
So we now need to spoof also this domain. I do this using dnsmasq (eg. following [this](https://wiki.debian.org/dnsmasq)). And setting max818.com in my `/etc/hosts` to my server's ip
.
This means we need to access the ESWIFI-XXX (for some reason using the same pw as the hostapd). Then, log in to 10.10.100.254 (user: admin, pw: admin). And manually set DNS in "STA settings". [Later note: this seems to be ignored, instead a static ip for DNS is used]

My current setup (probably some redundancy after tryouts)

```iptables:/etc/iptables/rules.v4
# Generated by iptables-save v1.6.0 on Sun Feb 13 13:20:54 2022
*nat
:PREROUTING ACCEPT [6:3734]
:INPUT ACCEPT [37:1628]
:OUTPUT ACCEPT [4:210]
:POSTROUTING ACCEPT [10:3944]
-A PREROUTING -p tcp -m physdev --physdev-in wlan0 -m tcp --dport 8400 -j REDIRECT --to-ports 8000
-A PREROUTING -i wlan0 -p tcp -m tcp --dport 8400 -j REDIRECT --to-ports 8000
-A PREROUTING -i wlan0 -p tcp -m tcp --dport 8400 -j REDIRECT --to-ports 8000
-A PREROUTING ! -s 192.168.178.25/32 ! -d 192.168.178.25/32 -i br0 -p udp -m udp --dport 53 -j DNAT --to-destination 192.168.178.25
-A PREROUTING ! -s 192.168.178.25/32 ! -d 192.168.178.25/32 -i br0 -p tcp -m tcp --dport 53 -j DNAT --to-destination 192.168.178.25
-A PREROUTING ! -s 192.168.178.25/32 ! -d 192.168.178.25/32 -p tcp -m physdev --physdev-in wlan0 -m tcp --dport 53 -j DNAT --to-destination 192.168.178.25
-A PREROUTING ! -s 192.168.178.25/32 ! -d 192.168.178.25/32 -p udp -m physdev --physdev-in wlan0 -m udp --dport 53 -j DNAT --to-destination 192.168.178.25
-A PREROUTING ! -s 192.168.178.25/32 ! -d 192.168.178.25/32 -i wlan0 -p udp -m udp --dport 53 -j DNAT --to-destination 192.168.178.25
-A PREROUTING ! -s 192.168.178.25/32 ! -d 192.168.178.25/32 -i wlan0 -p tcp -m tcp --dport 53 -j DNAT --to-destination 192.168.178.25
-A PREROUTING -i wlan0 -p udp -m udp --dport 53 -j REDIRECT --to-ports 1234
COMMIT
# Completed on Sun Feb 13 13:20:54 2022
# Generated by iptables-save v1.6.0 on Sun Feb 13 13:20:54 2022
*filter
:INPUT ACCEPT [94672:46551166]
:FORWARD ACCEPT [339898:84102511]
:OUTPUT ACCEPT [31784:8637577]
COMMIT
# Completed on Sun Feb 13 13:20:54 2022

```

saved using `iptables-save > /etc/iptables/rules.v4`

## TODO

* Integrate with home-assistant
    + automatically disable when I get home.
    + send a reminder to enable alarm when everybody leaves the house
    + do whatever you want.
* Create commands to implement other settings (phone numbers/alarm duration/zones/etc.)
    + This means figuring out all the parameters sent by the Box trough its initial json.
* Track who changes the status
