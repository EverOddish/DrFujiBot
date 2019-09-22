from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from .models import Command, SimpleOutput

def index(request):
    command_list = Command.objects.order_by('command')
    context = {'command_list' : command_list}
    return render(request, 'dashboard/index.html', context)

def permitted(is_broadcaster, is_moderator, is_subscriber, permissions):
    if is_broadcaster:
        return permissions >= Command.BROADCASTER_ONLY
    if is_moderator:
        return permissions >= Command.MODERATOR_ONLY
    if is_subscriber:
        return permissions >= Command.SUBSCRIBER_ONLY
    return permissions >= Command.EVERYONE

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
                # Complex Command
                pass

    return HttpResponse(response_text)
