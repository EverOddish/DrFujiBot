from django.db import models

class Command(models.Model):
    command_text = models.CharField(max_length=200)
    permissions = models.IntegerField(default=0)
    creation_date = models.DateTimeField()
    invocations = models.IntegerField(default=0)

class CommandOutput(models.Model):
    command = models.ForeignKey(Command, on_delete=models.CASCADE)
    output_text = models.CharField(max_length=5000)
    counter = models.IntegerField(default=0)
