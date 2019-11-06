from django.core.validators import RegexValidator
from django.db import models
from django.utils.timezone import now

# Order is important for permissions calculation!
DISABLED = 0
BROADCASTER_ONLY = 1
MODERATOR_ONLY = 2
SUBSCRIBER_ONLY = 3
EVERYONE = 4

PERMISSIONS_CHOICES = (
    (DISABLED, 'Disabled'),
    (BROADCASTER_ONLY, 'Broadcaster Only'),
    (MODERATOR_ONLY, 'Moderator Only'),
    (SUBSCRIBER_ONLY, 'Subscriber Only'),
    (EVERYONE, 'Everyone'),
)

class SimpleOutput(models.Model):
    prefix = models.CharField(max_length=5000, default='', blank=True)
    output_text = models.CharField(max_length=5000)
    def __str__(self):
        return self.prefix + ' ' + self.output_text

class Command(models.Model):
    command = models.CharField(max_length=200, validators=[RegexValidator(regex='^![a-zA-Z0-9]+$', message='Command must start with ! and contain only alphanumeric characters')])
    permissions = models.IntegerField(choices=PERMISSIONS_CHOICES, default=EVERYONE)
    invocation_count = models.IntegerField(default=0)
    is_built_in = models.BooleanField(default=False)
    cooldown = models.BooleanField(default=True)
    last_output_time = models.DateTimeField(default=now)
    output = models.ForeignKey(SimpleOutput, blank=True, null=True, on_delete=models.CASCADE)

class Setting(models.Model):
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

class TimedMessage(models.Model):
    minutes_interval = models.IntegerField(default=15)
    last_output_time = models.DateTimeField(default=now)
    current_output_count = models.IntegerField(default=0)
    max_output_count = models.IntegerField(default=0)
    message = models.ForeignKey(SimpleOutput, on_delete=models.CASCADE)

class Run(models.Model):
    name = models.CharField(max_length=200)
    attempt_number = models.IntegerField(default=1)
    game_setting = models.CharField(max_length=200)
    last_run_output = models.ForeignKey(SimpleOutput, blank=True, null=True, on_delete=models.SET_NULL, related_name='last_run_output')
    how_far_output = models.ForeignKey(SimpleOutput, blank=True, null=True, on_delete=models.SET_NULL, related_name='how_far_output')
    def __str__(self):
        return self.name

class Death(models.Model):
    nickname = models.CharField(max_length=200)
    time_of_death = models.DateTimeField(default=now)
    respect_count = models.IntegerField(default=0)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    attempt = models.IntegerField(default=1)

class Quote(models.Model):
    quote_text = models.CharField(max_length=1000)
    quotee = models.CharField(max_length=200)

class ChatLog(models.Model):
    is_broadcaster = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)
    is_subscriber = models.BooleanField(default=False)
    username = models.CharField(max_length=100)
    line = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(default=now)

class BannedPhrase(models.Model):
    phrase = models.CharField(max_length=200)
    expiry = models.DateTimeField(null=True)

class CoinEntry(models.Model):
    username = models.CharField(max_length=200)
    coins = models.IntegerField(default=0)
    last_daily = models.DateTimeField(default=now)
    has_won = models.BooleanField(default=False)

OPEN = 1
CLOSED = 2
RESOLVED = 3
CANCELLED = 4

EVENT_STATUS_CHOICES = (
    (OPEN, 'Open'),
    (CLOSED, 'Closed'),
    (RESOLVED, 'Resolved'),
    (CANCELLED, 'Cancelled'),
)

class BettingEvent(models.Model):
    name = models.CharField(max_length=200)
    prize_coins = models.IntegerField(default=0)
    status = models.IntegerField(choices=EVENT_STATUS_CHOICES, default=OPEN)
    open_timestamp = models.DateTimeField(default=now)
    closed_timestamp = models.DateTimeField(blank=True, null=True)
    resolved_timestamp = models.DateTimeField(blank=True, null=True)
    cancelled_timestamp = models.DateTimeField(blank=True, null=True)
    num_winners = models.IntegerField(default=0)

class Bet(models.Model):
    username = models.CharField(max_length=200)
    value = models.CharField(max_length=200)
    event = models.ForeignKey(BettingEvent, on_delete=models.CASCADE)
