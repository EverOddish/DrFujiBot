from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from .models import Command

def index(request):
    command_list = Command.objects.order_by('-creation_date')
    context = {'command_list' : command_list}
    return render(request, 'dashboard/index.html', context)

def drfujibot(request):
    is_broadcaster = request.GET.get('is_broadcaster')
    is_moderator = request.GET.get('is_moderator')
    is_subscriber = request.GET.get('is_subscriber')
    line = request.GET.get('line')
    response_text = ''

    if '!test' == line:
        response_text = 'It works!'

    return HttpResponse(response_text)
