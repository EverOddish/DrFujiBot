import os
import subprocess

def start():
    install_path = os.path.join(os.environ['LOCALAPPDATA'], 'DrFujiBot')
    httpd_path = os.path.join(install_path, 'Apache24', 'bin', 'httpd.exe')

    # Start Apache
    subprocess.call([httpd_path, '-n', '"DrFujiBot Apache"', '-k', 'start'])

    # Open dashboard
    subprocess.call(['explorer.exe', 'http://localhost:41945/admin'])
