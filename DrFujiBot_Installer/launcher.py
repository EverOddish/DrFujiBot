import os
import subprocess

def start():
    install_path = os.path.join(os.environ['LOCALAPPDATA'], 'Programs', 'DrFujiBot')
    httpd_path = os.path.join(install_path, 'Apache24', 'bin', 'httpd.exe')

    # Start Apache
    try:
        subprocess.call([httpd_path, '-n', '"DrFujiBot Apache"', '-k', 'start'])
    except:
        pass

    # Open dashboard
    try:
        subprocess.call(['explorer.exe', 'http://localhost:41945/admin'])
    except:
        pass
