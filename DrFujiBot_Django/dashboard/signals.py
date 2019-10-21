import subprocess
from .models import Setting

def setting_changed(sender, instance, **kwargs):
    if 'IRC Service' == instance.key:
        if 'Running' == instance.value:
            args = ['sc', 'start', 'DrFujiBot IRC']
            subprocess.run(args)
            args = ['sc', 'config', 'DrFujiBot IRC', 'start=', 'auto']
            subprocess.run(args)
        elif 'Stopped' == instance.value:
            args = ['sc', 'stop', 'DrFujiBot IRC']
            subprocess.run(args)
            args = ['sc', 'config', 'DrFujiBot IRC', 'start=', 'demand']
            subprocess.run(args)
