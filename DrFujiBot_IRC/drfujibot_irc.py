import irc.bot
import json
import os
import requests
import socket
import sys
import threading
import time

# These are necessary because of the standalone Python installation
file_dir = os.path.join(os.path.dirname(__file__), '..', 'pkgs', 'win32')
sys.path.append(file_dir)

file_dir = os.path.join(os.path.dirname(__file__), '..', 'pkgs', 'win32', 'lib')
sys.path.append(file_dir)

try:
    import win32event
    import win32service
    import win32serviceutil
    import servicemanager
except ImportError:
    pass

def unscramble(scrambled):
    unscrambled = ''
    for i in range(0, 30, 2):
        unscrambled += scrambled[i]
    for i in range(1, 30, 2):
        unscrambled += scrambled[i]
    return unscrambled

class DrFujiBot(irc.bot.SingleServerIRCBot):
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path) as f:
            self.settings = json.load(f)

            # The purpose of scrambling the token is mainly to prevent bots from scraping the token from GitHub.
            # Please do not use this token for any other purpose than the normal functions of DrFujiBot. Thank you.
            token = 'oauth:' + unscramble(self.settings['twitch_oauth_token'])

            twitch_channel = self.settings['twitch_channel'].lower()
            if len(twitch_channel) > 0:
                irc.bot.SingleServerIRCBot.__init__(self, [('irc.twitch.tv', 6667, token)], twitch_channel, twitch_channel)
                self.channel = '#' + twitch_channel.lower()
                self.session = requests.Session()
                self.timed_message_thread = threading.Thread(target=self.timed_message_loop)
                self.timed_message_thread.start()

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        self.c = c
        c.join(self.channel)
        print('Joined chat for ' + self.channel)
        c.cap('REQ', ":twitch.tv/tags")

    def on_privmsg(self, c, e):
        pass

    def on_whisper(self, c, e):
        pass

    def on_dccmsg(self, c, e):
        pass

    def on_dccchat(self, c, e):
        pass

    def on_pubmsg(self, c, e):
        line = e.arguments[0]
        if line.startswith("!"):
            print(line)
            is_broadcaster = False
            is_moderator = False
            is_subscriber = False

            for tag in e.tags:
                if tag['key'] == 'bits':
                    pass
                elif tag['key'] == 'badges':
                    if tag['value']:
                        badges = tag['value'].split(',')
                        for b in badges:
                            if b.split('/')[0] == 'broadcaster':
                                is_broadcaster = True
                            elif b.split('/')[0] == 'moderator':
                                is_moderator = True
                            elif b.split('/')[0] == 'subscriber':
                                is_subscriber = True

            parameters = {'is_broadcaster': is_broadcaster, 'is_moderator': is_moderator, 'is_subscriber': is_subscriber, 'line': line}
            try:
                response = self.session.get('http://127.0.0.1:41945/dashboard/drfujibot', params=parameters)
                if len(response.text) > 0:
                    print(response.text)
                    self.output_msg(response.text)
            except Exception as e:
                print(e)

    def output_msg(self, output):
        MAX_MESSAGE_SIZE = 480
        chunk_size = MAX_MESSAGE_SIZE - 10
        chunks = [output[i:i + chunk_size] for i in range(0, len(output), chunk_size)]
        j = 1
        for ch in chunks:
            if len(chunks) > 1:
                ch = '(' + str(j) + '/' + str(len(chunks)) + ') ' + ch
            self.c.privmsg(self.channel, ch)
            j += 1

    def timed_message_loop(self):
        while True:
            # Ask the server once per minute for a timed message (if any)
            try:
                response = self.session.get('http://127.0.0.1:41945/dashboard/timed_messages')
                if len(response.text) > 0:
                    print(response.text)
                    self.output_msg(response.text)
            except Exception as e:
                print(e)
            time.sleep(60)

try:
    class DrFujiBotService(win32serviceutil.ServiceFramework):
        _svc_name_ = 'DrFujiBot IRC'
        _svc_display_name_ = 'DrFujiBot IRC'
        _svc_description_ = 'Connects to Twitch chat to relay commands to the local DrFujiBot Django instance'
        _exe_name_ = sys.executable
        _exe_args_ = '"' + os.path.abspath(sys.argv[0]) + '"'

        @classmethod
        def parse_command_line(cls):
            win32serviceutil.HandleCommandLine(cls)

        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            socket.setdefaulttimeout(60)
            self.bot = None

        def log(self, msg):
            servicemanager.LogInfoMsg(str(msg))

        def SvcStop(self):
            self.log('Service is stopping.')
            if self.bot:
                self.bot.disconnect()

            self.ReportServiceStatus(win32service.SERVICE_STOPPED)

        def SvcDoRun(self):
            self.log('Service is starting.')
            self.bot = DrFujiBot()
            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                  servicemanager.PYS_SERVICE_STARTED,
                                  (self._svc_name_, ''))
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.log('Service is running.')
            self.bot.start()

except NameError:
    pass

if '__main__' == __name__:
    print('Welcome to DrFujiBot 2.0')
    if len(sys.argv) == 1:
        try:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(DrFujiBotService)
            servicemanager.StartServiceCtrlDispatcher()
        except NameError:
            print('Running on non-Windows, only debug mode is available!')
            print('Usage: python3 drfujibot_irc.py debug')
    elif len(sys.argv) >= 2 and 'debug' == sys.argv[1]:
        bot = DrFujiBot()
        bot.start()
    else:
        DrFujiBotService.parse_command_line()
