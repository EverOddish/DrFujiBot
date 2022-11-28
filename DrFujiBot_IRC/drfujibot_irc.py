import irc.bot
import os
import requests
import socket
import sys
import threading
import time

class DrFujiBot(irc.bot.SingleServerIRCBot):
    def __init__(self, debug):
        self.c = None
        self.debug = debug

        token = 'oauth:' + os.environ['TWITCH_OAUTH_TOKEN']

        self.twitch_channel = os.environ['TWITCH_CHANNEL'].lower()

        irc.bot.SingleServerIRCBot.__init__(self, [('irc.twitch.tv', 6667, token)], self.twitch_channel, self.twitch_channel)
        self.channel = '#' + self.twitch_channel.lower()
        self.session = requests.Session()
        self.timed_message_thread = threading.Thread(target=self.timed_message_loop)
        self.timed_message_thread.start()

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        self.c = c
        c.join(self.channel)
        if self.debug:
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
        if self.debug:
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

        username = e.source.nick
        parameters = {'is_broadcaster': is_broadcaster, 'is_moderator': is_moderator, 'is_subscriber': is_subscriber, 'username': username, 'line': line}
        try:
            response = self.session.get('http://127.0.0.1:41945/dashboard/drfujibot', params=parameters)
            # Don't print errors from the server
            if len(response.text) > 0 and '<!DOCTYPE html>' not in response.text:
                lines = response.text.split('\n')
                for line in lines:
                    print(line)
                    self.output_msg(line)
        except Exception as e:
            if self.debug:
                print(str(e))

    def output_msg(self, output):
        MAX_MESSAGE_SIZE = 480
        chunk_size = MAX_MESSAGE_SIZE - 10
        chunks = [output[i:i + chunk_size] for i in range(0, len(output), chunk_size)]
        j = 1
        for ch in chunks:
            if len(chunks) > 1:
                ch = '(' + str(j) + '/' + str(len(chunks)) + ') ' + ch
            if self.c:
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
                if self.debug:
                    print(str(e))
            time.sleep(30)

if '__main__' == __name__:
    print('Welcome to DrFujiBot 2.0')
    bot = DrFujiBot(debug=True)
    bot.start()
