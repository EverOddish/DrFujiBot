import subprocess
from .models import Setting

def setting_changed(sender, instance, **kwargs):
    if 'IRC Service' == instance.key:
        try:
            if 'Running' == instance.value:
                args = ['sc', 'start', 'DrFujiBot Twitch Service']
                subprocess.run(args)
                args = ['sc', 'config', 'DrFujiBot Twitch Service', 'start=', 'auto']
                subprocess.run(args)
            elif 'Stopped' == instance.value:
                args = ['sc', 'stop', 'DrFujiBot Twitch Service']
                subprocess.run(args)
                args = ['sc', 'config', 'DrFujiBot Twitch Service', 'start=', 'demand']
                subprocess.run(args)
        except:
            pass
