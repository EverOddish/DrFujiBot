RMDIR /S /Q DrFujiBot_Django\westwood
MKDIR DrFujiBot_Django\westwood
XCOPY Westwood\django-westwood\westwood DrFujiBot_Django\westwood /E
DEL DrFujiBot_Django\db.sqlite3 2>nul
DEL DrFujiBot_Django\westwood.sqlite3 2>nul

RMDIR /S /Q R:\DrFujiBot
MKDIR R:\DrFujiBot
XCOPY ..\DrFujiBot R:\DrFujiBot /E

CD /D R:\DrFujiBot\DrFujiBot_Django
python manage.py migrate
python manage.py migrate --database=westwood
python manage.py import_westwood_data

CD R:\DrFujiBot\DrFujiBot_Installer
build_installer.bat
