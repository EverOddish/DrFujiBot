# DrFujiBot

If you are using DrFujiBot and need help, check the [FAQ page](https://github.com/EverOddish/DrFujiBot/wiki/Frequently-Asked-Questions)

# Description

DrFujiBot is a client-side Twitch chat bot that provides a command-based interface to Pokemon data. This repository represents the re-write of the original server-side version of the bot ([OpenFuji](https://github.com/EverOddish/OpenFuji)). The code and data are significantly more readable, extendable, and easier to work on. The intention of the re-write was to eliminate the need for a server to host the bot, and to make rapid updates much easier to implement.

The primary goal of DrFujiBot is to be as easy to install and use as possible. Very little configuration is required out-of-the-box, but customization is possible for advanced users.

Improvements over the original OpenFuji:

 * No server or access requests, just download, install and run
 * Web-based configuration dashboard
   * Easy configuration of timed messages, custom command output, per-command permissions, and many other settings
 * Automatic configuration backup
 * More specific data per generation or game, extra data not available in other data sets
 * Fully up-to-date database including Pokemon Sword & Shield data (Generation 8)
 * ROM hack data (Drayano hacks, Kaizo hacks, etc.)

# Components

## DrFujiBot Django

The interface and database on which DrFujiBot relies are managed by Django (a Python web framework). Django provides the ability to manage all data and custom commands and settings, and to handle any command requests in a dynamic fashion. The Django instance runs locally on the user's computer, and is never exposed to the wider internet. The user may control the bot settings via their favourite web browser by browsing to the local Django administration web site. The IRC component (described in the next section) will also query the Django instance for command output.

Django itself requires a web server to host its implementation. Apache was chosen as the web server to host the Django instance, as it can run as a Windows service in the background of the host system.

## DrFujiBot IRC

This component is a simple IRC chat bot written in Python. It somewhat resembles a very stripped-down version of the original OpenFuji. Performance and reliability issues were encountered with this approach, so it has been deprecated in favour of the DrFujiBot Twitch component as of DrFujiBot version 2.0.7.

## DrFujiBot Twitch

The Twitch component is written in C# and acts as an intermediary between Twitch chat and the local Django instance. It will do basic command parsing, determine permissions, and forward requests to Django for command output. The component runs as a Windows service in the background of the host system.

## DrFujiBot Installer

This component contains NSIS (Nullsoft Scriptable Install System) scripts that package up Python, Django, Apache, and DrFujiBot itself into a Windows installer. This results in DrFujiBot being installed as a regular Windows program on the user's system, which can later be uninstalled if desired.

## Westwood

DrFujiBot relies on the [Westwood](https://github.com/EverOddish/Westwood) data set. Westwood defines Pokemon data in a human-readable format, then generates database models and data that can be used by projects such as DrFujiBot. See the Westwood project description for more information.

# Contributing

If you aren't familiar with Git or GitHub, read through the [Getting Started with GitHub Desktop](https://help.github.com/en/desktop/getting-started-with-github-desktop) guide.

If you want to contribute to Westwood, see the [Westwood](https://github.com/EverOddish/Westwood) project for instructions.

## Requirements for building a release

On a Windows system:

 * Install NSIS
   * Install the ZipDLL plugin
   * Install the TextReplace
 * Install Apache 2.4 from `DrFujiBot_Installer\prebuilt\httpd-2.4.41-win32-VC15.zip` to `C:\Apache24`
 * Set the `MOD_WSGI_APACHE_ROOTDIR` environment variable to `C:\Apache24`
 * Install Python 3.7.9 32-bit
 * `pip install -r requirements.txt`

## Setup for the Django component

1. Install Python 3 and GitHub Desktop (or other Git software)

2. Install all Python dependecies

    `pip install -r requirements.txt`

3. Clone this repository

    `git clone git@github.com:EverOddish/DrFujiBot.git`

4. Make sure the Westwood submodule is updated

    `git submodule update --recursive --remote`

5. Copy the Westwood Django app into the DrFujiBot_Django directory

    `cp -r Westwood/django-westwood/westwood DrFujiBot_Django/`

6. Move into the DrFujiBot_Django directory and initialize Django (the Westwood data import will take some time)

~~~~
    cd DrFujiBot_Django
    python3 manage.py migrate
    python3 manage.py migrate --database=westwood
    python3 manage.py import_westwood_data
    python3 manage.py createsuperuser
~~~~

7. Start the Django development server

    `python3 manage.py runserver 0.0.0.0:41945`

8. You should now be able to make changes to the Python files and the server will automatically restart itself. The dashboard should be available by browsing to [http://localhost:41945/admin](http://localhost:41945/admin)

9. You may use the DrFujiBot Web Console link on the dashboard to test interaction with the bot.

## Setup for the installer component

1. Open a command prompt and navigate to the DrFujitBot_Installer directory

    `cd DrFujiBot_Installer`

2. Ensure that the Westwood database has been created as described in the Django setup instructions

3. Run the build script (this takes some time)

    `build_installer.bat`

4. The resulting installer will be found under DrFujiBot_Installer\build\nsis\DrFujiBot_2.0.0.exe

## Other questions

If you have any other questions, contact [EverOddish](https://twitter.com/EverOddish) on Twitter or join the [PokemonChallenges Discord](http://discord.gg/pchal) and ask to be added to the #drfuji-workshop channel.

# Disclaimers

All Pokemon data is owned by The Pokemon Company International. This project should not be used for commercial purposes.

This bot logs chat messages, usernames, and time stamps from the Twitch chat channel to which it is connected. Logs are stored on the local hard drive of the host machine in a database. Anyone that uses this bot must inform their viewers that this data is recorded, and must comply with all local and international privacy laws that are applicable. The authors of this DrFujiBot software are not responsible for any privacy violations that may arise from use of the bot.
