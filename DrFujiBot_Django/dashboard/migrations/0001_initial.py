# Generated by Django 2.2.5 on 2019-09-15 14:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Command',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('command_text', models.CharField(max_length=200)),
                ('permissions', models.IntegerField(default=0)),
                ('creation_date', models.DateTimeField()),
                ('invocations', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='CommandOutput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('output_text', models.CharField(max_length=5000)),
                ('counter', models.IntegerField(default=0)),
                ('command', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.Command')),
            ],
        ),
    ]
