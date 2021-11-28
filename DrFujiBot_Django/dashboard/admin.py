from django.contrib import admin
from django.forms import ModelForm, Select, TextInput

from .models import *
from westwood.models import Game

class CommandAdmin(admin.ModelAdmin):
    list_display = ['command', 'get_output', 'permissions', 'invocation_count', 'cooldown']
    list_filter = ('is_built_in',)
    readonly_fields = ['invocation_count']

    def get_fields(self, request, obj=None):
        if None == obj or not obj.is_built_in:
            return ('command', 'permissions', 'invocation_count', 'cooldown', 'output')
        elif obj.is_built_in:
            return ('command', 'permissions', 'invocation_count', 'cooldown')

    def get_output(self, obj):
        if None != obj.output:
            if len(obj.output.prefix) > 0:
                return obj.output.prefix + ' ' + obj.output.output_text
            else:
                return obj.output.output_text
        else:
            return ''
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

    def add_cooldown(modeladmin, request, queryset):
        queryset.update(cooldown=True)
    add_cooldown.short_description = 'Add cooldown to selected commands'

    def remove_cooldown(modeladmin, request, queryset):
        queryset.update(cooldown=False)
    remove_cooldown.short_description = 'Remove cooldown from selected commands'

    actions = [permit_disabled, permit_broadcaster, permit_moderator, permit_subscriber, permit_everyone, add_cooldown, remove_cooldown]

class TimedMessageAdmin(admin.ModelAdmin):
    fields = ['message', 'minutes_interval', 'current_output_count', 'max_output_count', 'stream_status']
    list_display = ['get_message', 'minutes_interval', 'current_output_count', 'max_output_count', 'stream_status']

    def get_message(self, obj):
        return obj.message.output_text
    get_message.admin_order_field = 'message'
    get_message.short_description = 'Message'

class SimpleOutputAdmin(admin.ModelAdmin):
    list_display = ['output_text', 'prefix']

class SettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value']
    readonly_fields = ['key']
    def get_form(self, request, obj=None, **kwargs):
        class SettingAdminForm(ModelForm):
            class Meta:
                model = Setting
                fields = ('value',)
        class CurrentRunSettingAdminForm(ModelForm):
            class Meta:
                model = Setting
                fields = ('value',)
                run_objects = Run.objects.all().order_by('name')
                run_names = [(run.name, run.name) for run in run_objects]
                widgets={'value': Select(choices=run_names)}
        class CurrentGameSettingAdminForm(ModelForm):
            class Meta:
                model = Setting
                fields = ('value',)
                game_objects = Game.objects.all().order_by('sequence')
                valid_games = [(game.name, game.name) for game in game_objects]
                valid_games.append('National Dex')
                widgets={'value': Select(choices=valid_games)}
        class CooldownSecondsAdminForm(ModelForm):
            class Meta:
                model = Setting
                fields = ('value',)
                widgets={'value': TextInput(attrs={'type': 'number'})}
        class IRCServiceSettingAdminForm(ModelForm):
            class Meta:
                model = Setting
                fields = ('value',)
                valid_options = [('Running', 'Running'), ('Stopped', 'Stopped')]
                widgets={'value': Select(choices=valid_options)}
        class TwitchUsernameSettingAdminForm(ModelForm):
            class Meta:
                model = Setting
                fields = ('value',)
                widgets={'value': TextInput(attrs={'readonly': 'readonly'})}
        class CoinsPerMinuteAdminForm(ModelForm):
            class Meta:
                model = Setting
                fields = ('value',)
                widgets={'value': TextInput(attrs={'type': 'number'})}
        if 'Current Game' == obj.key:
            return CurrentGameSettingAdminForm
        elif 'Current Run' == obj.key:
            return CurrentRunSettingAdminForm
        elif 'Cooldown Seconds' == obj.key:
            return CooldownSecondsAdminForm
        elif 'IRC Service' == obj.key:
            return IRCServiceSettingAdminForm
        elif 'Twitch Username' == obj.key:
            return TwitchUsernameSettingAdminForm
        elif 'Coins Per Minute' == obj.key:
            return CoinsPerMinuteAdminForm
        return SettingAdminForm
    def get_fields(self, request, obj=None):
        return ['key', 'value']
    def has_delete_permission(self, request, obj=None):
        return False

class RunAdmin(admin.ModelAdmin):
    list_display = ['name', 'attempt_number', 'game_setting', 'last_run_output', 'how_far_output']
    def get_form(self, request, obj=None, **kwargs):
        class RunAdminForm(ModelForm):
            class Meta:
                model = Run
                fields = ('name', 'attempt_number', 'game_setting', 'last_run_output', 'how_far_output')
                game_objects = Game.objects.all().order_by('sequence')
                valid_games = [(game.name, game.name) for game in game_objects]
                widgets={'name': TextInput(), 'attempt_number': TextInput(), 'game_setting': Select(choices=valid_games)}
        return RunAdminForm
    def get_fields(self, request, obj=None):
        return ['name', 'attempt_number', 'game_setting', 'last_run_output', 'how_far_output']

class DeathAdmin(admin.ModelAdmin):
    fields = ['nickname', 'time_of_death', 'respect_count', 'run', 'attempt']
    readonly_fields = ['time_of_death', 'respect_count']
    list_display = ['nickname', 'respect_count', 'get_run', 'attempt', 'time_of_death']

    def get_run(self, obj):
        return obj.run.name
    get_run.short_description = 'Run'
    get_run.admin_order_field = 'run'

class QuoteAdmin(admin.ModelAdmin):
    readonly_fields = ['id']
    list_display = ['id', 'quote_text', 'quotee']

class BannedPhraseAdmin(admin.ModelAdmin):
    list_display = ['phrase', 'expiry', 'timeout']

class AfflictionAdmin(admin.ModelAdmin):
    readonly_fields = ['name', 'description']
    list_display = ['name', 'description']
    ordering = ['name']
    def has_delete_permission(self, request, obj=None):
        return False

class AfflictedPokemonAdmin(admin.ModelAdmin):
    list_display = ['nickname', 'affliction_1', 'affliction_2']
    def get_affliction_2(self, obj):
        if None != obj.affliction_2:
            return obj.affliction_2
        else:
            return ''

admin.site.register(Command, CommandAdmin)
admin.site.register(TimedMessage, TimedMessageAdmin)
admin.site.register(SimpleOutput, SimpleOutputAdmin)
admin.site.register(Setting, SettingAdmin)
admin.site.register(Run, RunAdmin)
admin.site.register(Death, DeathAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(BannedPhrase, BannedPhraseAdmin)
admin.site.register(Affliction, AfflictionAdmin)
admin.site.register(AfflictedPokemon, AfflictedPokemonAdmin)
