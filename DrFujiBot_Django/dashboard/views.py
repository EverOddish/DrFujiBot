import datetime

from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from .models import DISABLED, BROADCASTER_ONLY, MODERATOR_ONLY, SUBSCRIBER_ONLY, EVERYONE
from .models import Command, SimpleOutput, Setting, TimedMessage, ChatLog, BannedPhrase
from .lookup_commands import handle_lookup_command
from .admin_commands import handle_admin_command

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

def drfujibot(request):
    is_broadcaster = request.GET.get('is_broadcaster')
    is_moderator = request.GET.get('is_moderator')
    is_subscriber = request.GET.get('is_subscriber')
    username = request.GET.get('username')
    line = request.GET.get('line')

    chat_log = ChatLog(is_broadcaster=is_broadcaster, is_moderator=is_moderator, is_subscriber=is_subscriber, username=username, line=line)
    chat_log.save()

    if 'True' != is_broadcaster and 'True' != is_moderator:
        banned_phrase_matches = BannedPhrase.objects.all()
        for phrase_object in banned_phrase_matches:
            print(phrase_object.phrase.lower())
            if phrase_object.phrase.lower() in line.lower():
                return HttpResponse('/timeout ' + username + ' 1')

    line_pieces = line.split(' ')
    command = line_pieces[0]

    response_text = ''
    command_query_set = Command.objects.filter(command__iexact=command)
    if len(command_query_set) >= 1:
        cmd = command_query_set[0]
        if permitted(is_broadcaster, is_moderator, is_subscriber, cmd.permissions):
            if cmd.output:
                response_text = cmd.output.output_text
            else:
                response_text = handle_lookup_command(line)
                if None == response_text or len(response_text) == 0:
                    response_text = handle_admin_command(line)

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
            response_text = timed_message.message.output_text
            timed_message.last_output_time = now
            timed_message.save()
            # Only output one timed message at a time. Others will be picked up next time around.
            break

    return HttpResponse(response_text)
