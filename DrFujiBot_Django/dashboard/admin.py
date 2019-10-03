from django.contrib import admin

from .models import Command, SimpleOutput, TimedMessage

admin.site.register(Command)
admin.site.register(SimpleOutput)
admin.site.register(TimedMessage)
