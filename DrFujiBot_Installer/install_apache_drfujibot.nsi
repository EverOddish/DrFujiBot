Function DumpLog
  Exch $5
  Push $0
  Push $1
  Push $2
  Push $3
  Push $4
  Push $6
 
  FindWindow $0 "#32770" "" $HWNDPARENT
  GetDlgItem $0 $0 1016
  StrCmp $0 0 exit
  FileOpen $5 $5 "w"
  StrCmp $5 "" exit
    SendMessage $0 ${LVM_GETITEMCOUNT} 0 0 $6
    System::Call '*(&t${NSIS_MAX_STRLEN})p.r3'
    StrCpy $2 0
    System::Call "*(i, i, i, i, i, p, i, i, i) i  (0, 0, 0, 0, 0, r3, ${NSIS_MAX_STRLEN}) .r1"
    loop: StrCmp $2 $6 done
      System::Call "User32::SendMessage(i, i, i, i) i ($0, ${LVM_GETITEMTEXT}, $2, r1)"
      System::Call "*$3(&t${NSIS_MAX_STRLEN} .r4)"
      FileWrite $5 "$4$\r$\n" ; Unicode will be translated to ANSI!
      IntOp $2 $2 + 1
      Goto loop
    done:
      FileClose $5
      System::Free $1
      System::Free $3
  exit:
    Pop $6
    Pop $4
    Pop $3
    Pop $2
    Pop $1
    Pop $0
    Exch $5
FunctionEnd

; Apache Section
!include x64.nsh
Section "Apache HTTP Server 2.4"
    SetOutPath "$INSTDIR"
    File "..\..\prebuilt\httpd-2.4.41-win32-VC15.zip"
    nsisunz::Unzip "$INSTDIR/httpd-2.4.41-win32-VC15.zip" "$INSTDIR"

    ; Set Apache's root directory to the bundled installation
    textreplace::_ReplaceInFile /NOUNLOAD "$INSTDIR/Apache24/conf/httpd.conf" "$INSTDIR/Apache24/conf/httpd.conf" "Define SRVROOT $\"c:/Apache24$\"" "Define SRVROOT $\"$INSTDIR\Apache24$\"" "/S=1"

    ; Set Apache to listen on localhost only with a random high port
    textreplace::_ReplaceInFile /NOUNLOAD "$INSTDIR/Apache24/conf/httpd.conf" "$INSTDIR/Apache24/conf/httpd.conf" "Listen 80" "Listen 127.0.0.1:41945" "/S=1"

    ; Set existing root directory to an unused value
    textreplace::_ReplaceInFile /NOUNLOAD "$INSTDIR/Apache24/conf/httpd.conf" "$INSTDIR/Apache24/conf/httpd.conf" "<Directory />" "<Directory /unused>" "/S=1"

    ; Append mod_wsgi settings for Django
    ClearErrors
    FileOpen $4 "$INSTDIR\Apache24\conf\httpd.conf" a
    FileSeek $4 0 END
    FileWrite $4 "$\r$\n"
    FileWrite $4 "LoadFile $\"$INSTDIR/Python/python37.dll$\""
    FileWrite $4 "$\r$\n"
    FileWrite $4 "LoadModule wsgi_module $\"$INSTDIR/pkgs/mod_wsgi/server/mod_wsgi.cp37-win32.pyd$\""
    FileWrite $4 "$\r$\n"
    FileWrite $4 "WSGIPythonHome $\"$INSTDIR/Python$\""
    FileWrite $4 "$\r$\n"
    FileWrite $4 "WSGIScriptAlias / $\"$INSTDIR/DrFujiBot_Django/DrFujiBot_Django/wsgi.py$\""
    FileWrite $4 "$\r$\n"
    FileWrite $4 "WSGIPythonPath $\"$INSTDIR/DrFujiBot_Django$\""
    FileWrite $4 "$\r$\n"
    FileWrite $4 "<Directory />"
    FileWrite $4 "$\r$\n"
    FileWrite $4 "<Files wsgi.py>"
    FileWrite $4 "$\r$\n"
    FileWrite $4 "Require all granted"
    FileWrite $4 "$\r$\n"
    FileWrite $4 "</Files>"
    FileWrite $4 "$\r$\n"
    FileWrite $4 "</Directory>"
    FileWrite $4 "$\r$\n"
    FileWrite $4 "$\r$\n"
    FileWrite $4 "Alias /static $\"$INSTDIR/pkgs/django/contrib/admin/static$\""
    FileWrite $4 "$\r$\n"
    FileWrite $4 "<Directory /static>"
    FileWrite $4 "$\r$\n"
    FileWrite $4 "Require all granted"
    FileWrite $4 "$\r$\n"
    FileWrite $4 "</Directory>"
    FileWrite $4 "$\r$\n"
    FileWrite $4 "$\r$\n"
    ; Use persistent connections for better performance
    FileWrite $4 "KeepAlive On"
    FileWrite $4 "$\r$\n"
    FileWrite $4 "MaxKeepAliveRequests 0"
    FileWrite $4 "$\r$\n"
    FileWrite $4 "KeepAliveTimeout 300"
    FileWrite $4 "$\r$\n"
    FileClose $4

    ; Install Visual Studio 2015 Runtime if needed
    ${If} ${RunningX64}
        # 64 bit code
        ReadRegDword $R1 HKLM "SOFTWARE\Wow6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x86" "Installed"
    ${Else}
        # 32 bit code
        ReadRegDword $R1 HKLM "SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x86" "Installed"
    ${EndIf}       
    ${If} $R1 != "1"
        SetOutPath "$INSTDIR" 
        File "..\..\prebuilt\vc_redist.x86.exe" 	
        nsExec::ExecToLog '"$INSTDIR\vc_redist.x86.exe" /passive /norestart'
    ${EndIf}

    ; Install Apache as a Windows service
    nsExec::ExecToLog '"$INSTDIR\Apache24\bin\httpd" -k install -n $\"DrFujiBot Apache$\"'

    ; Start Apache
    nsExec::ExecToLog '"$INSTDIR\Apache24\bin\httpd" -k start -n $\"DrFujiBot Apache$\"'
SectionEnd

; Django Section
Section "DrFujiBot Django"
    File /r /x db.sqlite3 /x *.pyc /x *.swp "..\..\..\DrFujiBot_Django"
    CreateDirectory "$INSTDIR\..\DrFujiBot_Backup"

    IfFileExists "$INSTDIR\..\DrFujiBot_Backup\db_backup_before_uninstall.sqlite3" RestoreBackup Init
    RestoreBackup:
    CopyFiles "$INSTDIR\..\DrFujiBot_Backup\db_backup_before_uninstall.sqlite3" "$INSTDIR\DrFujiBot_Django\db.sqlite3"

    # Run any new migrations on the old database to bring it up to date
    nsExec::ExecToLog '"$INSTDIR\Python\python.exe" "$INSTDIR\DrFujiBot_Django\manage.py" migrate'
    Goto Check

    Init:
    ; Initialize Django
    nsExec::ExecToLog '"$INSTDIR\Python\python.exe" "$INSTDIR\DrFujiBot_Django\manage.py" migrate'
    File "..\..\..\DrFujiBot_Installer\create_super_user.bat"
    nsExec::ExecToLog '"$INSTDIR\create_super_user.bat"'

    Check:
    nsExec::ExecToLog '"$INSTDIR\Python\python.exe" "$INSTDIR\DrFujiBot_Django\manage.py" check'
    Pop $0
    IfErrors 0 done
        MessageBox MB_OK "Error installing Django"
    done:
SectionEnd

; IRC Section
Section "DrFujiBot IRC"
    File /r /x config.json /x *.swp "..\..\..\DrFujiBot_IRC"
    ${If} ${RunningX64}
        CopyFiles "$INSTDIR\pkgs\pywin32_system32\*.dll" "$WINDIR\SysWOW64"
    ${EndIf}

    ; Create config.json
    ClearErrors
    FileOpen $4 "$INSTDIR\DrFujiBot_IRC\config.json" w
    FileSeek $4 0 END
    FileWrite $4 "{$\"twitch_channel$\": $\"$\", $\"twitch_oauth_token$\": $\"$\"}"
    FileClose $4

    nsExec::ExecToLog 'sc.exe create "DrFujiBot IRC" start= auto binPath= "\$\"$INSTDIR\Python\python.exe\$\" \$\"$INSTDIR\DrFujiBot_IRC\drfujibot_irc.py\$\"'
    nsExec::ExecToLog 'sc.exe description "DrFujiBot IRC" "Connects to Twitch chat to relay commands to the local DrFujiBot Django instance"'

    File ..\..\disclaimers.txt

    StrCpy $0 "$INSTDIR\install.log"
    Push $0
    Call DumpLog
SectionEnd

; Uninstall sections

Section "Uninstall"
    ; Apache HTTP Server 2.4
    nsExec::ExecToLog '"$INSTDIR\Apache24\bin\httpd" -k stop -n $\"DrFujiBot Apache$\"'
    nsExec::ExecToLog '"$INSTDIR\Apache24\bin\httpd" -k uninstall -n $\"DrFujiBot Apache$\"'
    RMDir /r "$INSTDIR\Apache24"
    Delete "$INSTDIR\-- Win32 VC15  --"
    Delete "$INSTDIR\ReadMe.txt"
    Delete "$INSTDIR\httpd-2.4.41-win32-VC15.zip"

    ; DrFujiBot Django
    RMDir /r "$INSTDIR\DrFujiBot_Django"

    ; DrFujiBot IRC
    nsExec::ExecToLog 'net.exe stop "DrFujiBot IRC"'
    nsExec::ExecToLog 'sc.exe delete "DrFujiBot IRC"'
    RMDir /r "$INSTDIR\DrFujiBot_IRC"

    ; Remove leftovers that couldn't be deleted because Apache was still running
    RMDir /r "$INSTDIR"
SectionEnd
