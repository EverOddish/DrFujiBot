from .models import Setting

def setting_changed(sender, instance, **kwargs):
    print('Setting "' + instance.key + '" set to "' + instance.value + '"')
