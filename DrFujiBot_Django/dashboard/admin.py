from django.contrib import admin

from .models import Command, CommandOutput

admin.site.register(Command)
admin.site.register(CommandOutput)
