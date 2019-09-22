from django.contrib import admin

from .models import Command, SimpleOutput

admin.site.register(Command)
admin.site.register(SimpleOutput)
