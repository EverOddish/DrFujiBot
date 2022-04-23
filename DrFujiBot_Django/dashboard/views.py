import certifi
import datetime
import json
import jwt
import os
import requests
import subprocess
import urllib

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from scheduled_tasks.uptime_check import get_uptime

from .admin_commands import handle_admin_command
from .lookup_commands import handle_lookup_command
from .coin_commands import handle_coin_command
from .models import DISABLED, BROADCASTER_ONLY, MODERATOR_ONLY, SUBSCRIBER_ONLY, EVERYONE
from .models import UNSPECIFIED, ONLINE_ONLY, OFFLINE_ONLY
from .models import Command, SimpleOutput, Setting, TimedMessage, ChatLog, BannedPhrase
from .utility import twitch_api_request, CLIENT_ID, populate_placeholders

def index(request):
    settings_list = Setting.objects.order_by('key')
    timed_message_list = TimedMessage.objects.all().order_by('minutes_interval')
    custom_command_list = Command.objects.filter(output__isnull=False).order_by('command')
    builtin_command_list = Command.objects.filter(output__isnull=True).order_by('command')
    context = {'settings_list': settings_list,
               'timed_message_list': timed_message_list,
               'custom_command_list' : custom_command_list,
               'builtin_command_list' : builtin_command_list}
    return render(request, 'dashboard/index.html', context)

def console(request):
    context = {}
    return render(request, 'dashboard/console.html', context)

def permitted(is_broadcaster, is_moderator, is_subscriber, permissions):
    if permissions == DISABLED:
        return False
    if 'True' == is_broadcaster:
        return permissions >= BROADCASTER_ONLY
    if 'True' == is_moderator:
        return permissions >= MODERATOR_ONLY
    if 'True' == is_subscriber:
        return permissions >= SUBSCRIBER_ONLY
    return permissions >= EVERYONE

def get_permission_message(permissions):
    if permissions == DISABLED:
        # Do not display any permissions warnings for disabled commands, as they could be the same as other bots
        # and might be disabled on purpose to allow the other bot to handle the command.
        return None
    elif permissions == BROADCASTER_ONLY:
        return 'only permitted for the broadcaster'
    elif permissions == MODERATOR_ONLY:
        return 'only permitted for moderators'
    elif permissions == SUBSCRIBER_ONLY:
        return 'only permitted for subscribers'

def drfujibot(request):
    response_text = ''
    is_broadcaster = request.GET.get('is_broadcaster')
    is_moderator = request.GET.get('is_moderator')
    is_subscriber = request.GET.get('is_subscriber')
    username = request.GET.get('username')
    line = request.GET.get('line')

    # Note: This function gets called a lot in larger Twitch streams, so be mindful of performance.

    # Check for banned phrases first, and don't continue if banned.
    if 'True' != is_broadcaster and 'True' != is_moderator:
        banned_phrase_matches = BannedPhrase.objects.all()
        for phrase_object in banned_phrase_matches:
            if None != phrase_object.phrase and phrase_object.phrase.lower() in line.lower():
                return HttpResponse('/timeout ' + username + ' ' + str(phrase_object.timeout))

    chat_log = ChatLog(is_broadcaster=is_broadcaster, is_moderator=is_moderator, is_subscriber=is_subscriber, username=username, line=line)
    chat_log.save()

    # The rest of this function is for commands only, so don't even bother if the line doesn't start with '!'
    if line.startswith('!'):
        line_pieces = line.split(' ')
        command = line_pieces[0]

        command_query_set = Command.objects.filter(command__iexact=command)
        if len(command_query_set) >= 1:
            cmd = command_query_set[0]
            if permitted(is_broadcaster, is_moderator, is_subscriber, cmd.permissions):
                now = datetime.datetime.now(datetime.timezone.utc)

                should_output = False
                if cmd.cooldown:
                    cooldown_setting = Setting.objects.filter(key='Cooldown Seconds')[0]
                    cooldown_seconds = int(cooldown_setting.value)
                    if now < cmd.last_output_time:
                        # The command's last output time is in the future.
                        # This can occur if system time was modified for Desmume/in-game clock purposes.
                        # Allow the command to be output, and the last output time will be set back to a normal value.
                        should_output = True
                    elif now - cmd.last_output_time >= datetime.timedelta(seconds=cooldown_seconds):
                        should_output = True
                else:
                    should_output = True

                if should_output:
                    if cmd.output:
                        if len(cmd.output.prefix) > 0:
                            response_text = cmd.output.prefix + ' ' + cmd.output.output_text
                        else:
                            response_text = cmd.output.output_text
                        response_text = populate_placeholders(response_text)
                    else:
                        response_text = handle_lookup_command(line)
                        if None == response_text or len(response_text) == 0:
                            response_text = handle_admin_command(line)
                            if None == response_text or len(response_text) == 0:
                                response_text = handle_coin_command(line, username)
                    cmd.invocation_count += 1
                    cmd.last_output_time = now
                    cmd.save()
            else:
                message = get_permission_message(cmd.permissions)
                if message:
                    response_text = 'Sorry, ' + command + ' is ' + message +'. If you would like to use this bot on your own computer, you can find it at https://github.com/EverOddish/DrFujiBot/releases'

        if isinstance(response_text, list):
            response_text = '\n'.join(response_text)

    return HttpResponse(response_text)

def timed_messages(request):
    response_text = ''

    now = datetime.datetime.now(datetime.timezone.utc)

    timed_messages = TimedMessage.objects.all()
    for timed_message in timed_messages:
        interval = datetime.timedelta(minutes=timed_message.minutes_interval)
        if now - timed_message.last_output_time > interval:
            should_output = False

            if timed_message.stream_status == UNSPECIFIED:
                should_output = True
            else:
                uptime = get_uptime()
                if uptime:
                    # Stream is live
                    if timed_message.stream_status == ONLINE_ONLY:
                        should_output = True
                else:
                    # Stream is not live
                    if timed_message.stream_status == OFFLINE_ONLY:
                        should_output = True

            if should_output:
                if len(timed_message.message.prefix) > 0:
                    response_text = timed_message.message.prefix + ' ' + timed_message.message.output_text
                else:
                    response_text = timed_message.message.output_text
                response_text = populate_placeholders(response_text)
                timed_message.last_output_time = now
                if timed_message.max_output_count > 0:
                    timed_message.current_output_count += 1
                timed_message.save()

                if timed_message.max_output_count > 0 and timed_message.current_output_count >= timed_message.max_output_count:
                    timed_message.message.delete()
                    timed_message.delete()

                # Only output one timed message at a time. Others will be picked up next time around.
                break

    return HttpResponse(response_text)

def authorize(request):
    context = {}
    return render(request, 'dashboard/authorize.html', context)

def restart_twitch_service():
    # Cause the Twitch service to restart the chat bot
    twitch_service_reload_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Release', 'reload.txt')
    with open(twitch_service_reload_path, 'w') as f:
        f.write("reload config")

def save_access_token(request):
    access_token = request.GET.get('access_token')
    id_token = request.GET.get('id_token')

    if id_token:
        web_key_request = urllib.request.Request('https://id.twitch.tv/oauth2/keys')
        web_key_response = urllib.request.urlopen(web_key_request, cafile=certifi.where())
        web_key_content = web_key_response.read().decode('utf-8')
        web_keys = json.loads(web_key_content)
        for web_key in web_keys['keys']:
            if web_key['alg'] == 'RS256':
                key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(web_key))
                token = jwt.decode(id_token, key, algorithms='RS256', audience=CLIENT_ID)

                # Convert user ID to username
                user_id = token['sub']
                url = 'https://api.twitch.tv/helix/users?id=' + user_id
                user_data = twitch_api_request(url)
                if user_data:
                    channel = user_data['data'][0]['login']
                    display_name = user_data['data'][0]['display_name']

                    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Release', 'config.json')
                    config = {}

                    with open(config_path, 'r') as config_file:
                        config = json.load(config_file)

                    config['twitch_channel'] = channel
                    config['twitch_oauth_token'] = access_token

                    with open(config_path, 'w') as config_file:
                        config_file.write(json.dumps(config))

                    username_setting = Setting.objects.get(key='Twitch Username')
                    username_setting.value = channel
                    username_setting.save()

                    quotee_setting = Setting.objects.get(key='Quotee')
                    quotee_setting.value = display_name
                    quotee_setting.save()

                restart_twitch_service()

    return redirect('/admin/')

def restart_drfujibot_service(request):
    context = {}
    restart_twitch_service()
    return render(request, 'dashboard/restart_drfujibot_service.html', context)
