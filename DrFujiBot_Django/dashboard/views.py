from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from .models import BROADCASTER_ONLY, MODERATOR_ONLY, SUBSCRIBER_ONLY, EVERYONE
from .models import Command, SimpleOutput, Setting
from .lookup_commands import handle_lookup_command

def index(request):
    settings_list = Setting.objects.order_by('key')
    custom_command_list = Command.objects.filter(output__isnull=False).order_by('command')
    builtin_command_list = Command.objects.filter(output__isnull=True).order_by('command')
    context = {'settings_list': settings_list,
               'custom_command_list' : custom_command_list,
               'builtin_command_list' : builtin_command_list}
    return render(request, 'dashboard/index.html', context)

def permitted(is_broadcaster, is_moderator, is_subscriber, permissions):
    if is_broadcaster:
        return permissions >= BROADCASTER_ONLY
    if is_moderator:
        return permissions >= MODERATOR_ONLY
    if is_subscriber:
        return permissions >= SUBSCRIBER_ONLY
    return permissions >= EVERYONE

def drfujibot(request):
    is_broadcaster = request.GET.get('is_broadcaster')
    is_moderator = request.GET.get('is_moderator')
    is_subscriber = request.GET.get('is_subscriber')
    line = request.GET.get('line')

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

    return HttpResponse(response_text)
