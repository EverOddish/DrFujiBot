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
    output_text = models.CharField(max_length=5000)
    def __str__(self):
        return self.output_text

class Command(models.Model):
    command = models.CharField(max_length=200, validators=[RegexValidator(regex='^![a-zA-Z0-9]+$', message='Command must start with ! and contain only alphanumeric characters')])
    permissions = models.IntegerField(choices=PERMISSIONS_CHOICES, default=EVERYONE)
    invocation_count = models.IntegerField(default=0)
    is_built_in = models.BooleanField(default=False)
    output = models.ForeignKey(SimpleOutput, blank=True, null=True, on_delete=models.CASCADE)

class Setting(models.Model):
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

class TimedMessage(models.Model):
    minutes_interval = models.IntegerField(default=15)
    last_output_time = models.DateTimeField(default=now)
    message = models.ForeignKey(SimpleOutput, on_delete=models.CASCADE)
