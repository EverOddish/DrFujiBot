from django.contrib import admin
from django.forms import ModelForm, Select, TextInput

from .models import Command, SimpleOutput, TimedMessage, Setting, Run, Death
from .models import DISABLED, BROADCASTER_ONLY, MODERATOR_ONLY, SUBSCRIBER_ONLY, EVERYONE
from westwood.models import Game

class CommandAdmin(admin.ModelAdmin):
    list_display = ['command', 'get_output', 'permissions']

    def get_fields(self, request, obj=None):
        if None == obj or not obj.is_built_in:
            return ('command', 'permissions', 'output')
        elif obj.is_built_in:
            return ('command', 'permissions')

    def get_output(self, obj):
        return obj.output.output_text if None != obj.output else ''
    get_output.admin_order_field = 'output'
    get_output.short_description = 'Output Text'

    def has_delete_permission(self, request, obj=None):
        if obj:
            return not obj.is_built_in
        else:
            return True

    def permit_disabled(modeladmin, request, queryset):
        queryset.update(permissions=DISABLED)
    permit_disabled.short_description = 'Set selected commands to Disabled'

    def permit_broadcaster(modeladmin, request, queryset):
        queryset.update(permissions=BROADCASTER_ONLY)
    permit_broadcaster.short_description = 'Set selected commands to Broadcaster Only'

    def permit_moderator(modeladmin, request, queryset):
        queryset.update(permissions=MODERATOR_ONLY)
    permit_moderator.short_description = 'Set selected commands to Moderator Only'

    def permit_subscriber(modeladmin, request, queryset):
        queryset.update(permissions=SUBSCRIBER_ONLY)
    permit_subscriber.short_description = 'Set selected commands to Subscriber Only'

    def permit_everyone(modeladmin, request, queryset):
        queryset.update(permissions=EVERYONE)
    permit_everyone.short_description = 'Set selected commands to Everyone'

    actions = [permit_disabled, permit_broadcaster, permit_moderator, permit_subscriber, permit_everyone]

class TimedMessageAdmin(admin.ModelAdmin):
    fields = ['message', 'minutes_interval']
    list_display = ['get_message', 'minutes_interval']

    def get_message(self, obj):
        return obj.message.output_text
    get_message.admin_order_field = 'message'
    get_message.short_description = 'Message'

class SimpleOutputAdmin(admin.ModelAdmin):
    list_display = ['output_text']

class SettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value']
    readonly_fields = ['key']
    def get_form(self, request, obj=None, **kwargs):
        class SettingAdminForm(ModelForm):
            class Meta:
                model = Setting
                fields = ('value',)
                game_objects = Game.objects.all().order_by('sequence')
                valid_games = [(game.name, game.name) for game in game_objects]
                widgets={'value': Select(choices=valid_games)}
        return SettingAdminForm
    def get_fields(self, request, obj=None):
        return ['key', 'value']
    def has_delete_permission(self, request, obj=None):
        return False

class RunAdmin(admin.ModelAdmin):
    list_display = ['name', 'attempt_number', 'game_setting']
    def get_form(self, request, obj=None, **kwargs):
        class RunAdminForm(ModelForm):
            class Meta:
                model = Run
                fields = ('name', 'attempt_number', 'game_setting')
                game_objects = Game.objects.all().order_by('sequence')
                valid_games = [(game.name, game.name) for game in game_objects]
                widgets={'name': TextInput(), 'attempt_number': TextInput(), 'game_setting': Select(choices=valid_games)}
        return RunAdminForm
    def get_fields(self, request, obj=None):
        return ['name', 'attempt_number', 'game_setting']

class DeathAdmin(admin.ModelAdmin):
    fields = ['nickname', 'respect_count', 'run']
    readonly_fields = ['respect_count']
    list_display = ['nickname', 'respect_count', 'get_run']

    def get_run(self, obj):
        return obj.run.name
    get_run.short_description = 'Run'
    get_run.admin_order_field = 'run'

admin.site.register(Command, CommandAdmin)
admin.site.register(TimedMessage, TimedMessageAdmin)
admin.site.register(SimpleOutput, SimpleOutputAdmin)
admin.site.register(Setting, SettingAdmin)
admin.site.register(Run, RunAdmin)
admin.site.register(Death, DeathAdmin)
