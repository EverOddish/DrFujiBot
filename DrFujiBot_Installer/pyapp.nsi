!define PRODUCT_NAME "[[ib.appname]]"
!define PRODUCT_VERSION "[[ib.version]]"
!define PY_VERSION "[[ib.py_version]]"
!define PY_MAJOR_VERSION "[[ib.py_major_version]]"
!define BITNESS "[[ib.py_bitness]]"
!define ARCH_TAG "[[arch_tag]]"
!define INSTALLER_NAME "[[ib.installer_name]]"
!define PRODUCT_ICON "[[icon]]"

; Marker file to tell the uninstaller that it's a user installation
!define USER_INSTALL_MARKER _user_install_marker
 
Unicode false
SetCompressor lzma

!define MULTIUSER_EXECUTIONLEVEL Highest
!define MULTIUSER_INSTALLMODE_DEFAULT_CURRENTUSER
!define MULTIUSER_MUI
!define MULTIUSER_INSTALLMODE_COMMANDLINE
!define MULTIUSER_INSTALLMODE_INSTDIR "[[ib.appname]]"
[% if ib.py_bitness == 64 %]
!define MULTIUSER_INSTALLMODE_FUNCTION correct_prog_files
[% endif %]
!include MultiUser.nsh

[% block modernui %]
; Modern UI installer stuff 
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "[[icon]]"
!define MUI_UNICON "[[icon]]"

; UI pages
[% block ui_pages %]
!insertmacro MUI_PAGE_WELCOME
[% if license_file %]
!insertmacro MUI_PAGE_LICENSE [[license_file]]
[% endif %]
!insertmacro MULTIUSER_PAGE_INSTALLMODE
#!insertmacro MUI_PAGE_DIRECTORY



; Start DrFujiBot add-in:
!include nsDialogs.nsh
!include LogicLib.nsh
!include ZipDLL.nsh

;; USAGE:
!define MIN_FRA_MAJOR "4"
!define MIN_FRA_MINOR "6"
!define MIN_FRA_BUILD "1"
;
;; NB Use an asterisk to match anything.
; Call AbortIfBadFramework
;; No pops. It just aborts inside the function, or returns if all is well.
;; Change this if you like.
Function AbortIfBadFramework
 
  ; Save the variables in case something else is using them
  Push $0
  Push $1
  Push $2
  Push $3
  Push $4
  Push $R1
  Push $R2
  Push $R3
  Push $R4
  Push $R5
  Push $R6
  Push $R7
  Push $R8
 
  ; Major
  StrCpy $R5 "0"
 
  ; Minor
  StrCpy $R6 "0"
 
  ; Build
  StrCpy $R7 "0"
 
  ; No Framework
  StrCpy $R8 "0.0.0"
 
  StrCpy $0 0
 
  loop:
 
  ; Get each sub key under "SOFTWARE\Microsoft\NET Framework Setup\NDP"
  EnumRegKey $1 HKLM "SOFTWARE\Microsoft\NET Framework Setup\NDP" $0
  StrCmp $1 "" done ;jump to end if no more registry keys
  IntOp $0 $0 + 1
  StrCpy $2 $1 1 ;Cut off the first character
  StrCpy $3 $1 "" 1 ;Remainder of string
 
  ; Loop if first character is not a 'v'
  StrCmpS $2 "v" start_parse loop
 
  ; Parse the string
  start_parse:
  StrCpy $R1 ""
  StrCpy $R2 ""
  StrCpy $R3 ""
  StrCpy $R4 $3
 
  StrCpy $4 1
 
  parse:
  StrCmp $3 "" parse_done ; If string is empty, we are finished
  StrCpy $2 $3 1 ; Cut off the first character
  StrCpy $3 $3 "" 1 ; Remainder of string
  StrCmp $2 "." is_dot not_dot ; Move to next part if it's a dot
 
  is_dot:
  IntOp $4 $4 + 1 ; Move to the next section
  goto parse ; Carry on parsing
 
  not_dot:
  IntCmp $4 1 major_ver
  IntCmp $4 2 minor_ver
  IntCmp $4 3 build_ver
  IntCmp $4 4 parse_done
 
  major_ver:
  StrCpy $R1 $R1$2
  goto parse ; Carry on parsing
 
  minor_ver:
  StrCpy $R2 $R2$2
  goto parse ; Carry on parsing
 
  build_ver:
  StrCpy $R3 $R3$2
  goto parse ; Carry on parsing
 
  parse_done:
 
  IntCmp $R1 $R5 this_major_same loop this_major_more
  this_major_more:
  StrCpy $R5 $R1
  StrCpy $R6 $R2
  StrCpy $R7 $R3
  StrCpy $R8 $R4
 
  goto loop
 
  this_major_same:
  IntCmp $R2 $R6 this_minor_same loop this_minor_more
  this_minor_more:
  StrCpy $R6 $R2
  StrCpy $R7 $R3
  StrCpy $R8 $R4
  goto loop
 
  this_minor_same:
  IntCmp R3 $R7 loop loop this_build_more
  this_build_more:
  StrCpy $R7 $R3
  StrCpy $R8 $R4
  goto loop
 
  done:
 
  ; Have we got the framework we need?
  IntCmp $R5 ${MIN_FRA_MAJOR} max_major_same fail end
  max_major_same:
 
  ; Versions > 4.5 have different logic.
  IntCmp ${MIN_FRA_MAJOR} 4 0 before45 end
  IntCmp ${MIN_FRA_MINOR} 5 max_major_greaterthan45 before45 max_major_greaterthan45
 
  before45:
  IntCmp $R6 ${MIN_FRA_MINOR} max_minor_same fail end
 
  max_minor_same:
  IntCmp $R7 ${MIN_FRA_BUILD} end fail end
 
  max_major_greaterthan45:
 
  !if ${MIN_FRA_MINOR} == "5"
 
   !if ${MIN_FRA_BUILD} == "0"
    !define MIN_FRA_RELEASE "378389"
   !else if ${MIN_FRA_BUILD} == "1"
    !define MIN_FRA_RELEASE "378675"
   !else if ${MIN_FRA_BUILD} == "2"
    !define MIN_FRA_RELEASE "379893"
   !else
    !error "AbortIfBadFramework was passed a bad framework version ${MIN_FRA_MAJOR}.${MIN_FRA_MINOR}.${MIN_FRA_BUILD}."
   !endif
 
  !else if ${MIN_FRA_MINOR} == "6"
 
   !if ${MIN_FRA_BUILD} == "0"
    !define MIN_FRA_RELEASE "393295"
   !else if ${MIN_FRA_BUILD} == "1"
    !define MIN_FRA_RELEASE "394254"
   !else if ${MIN_FRA_BUILD} == "2"
    !define MIN_FRA_RELEASE "394802"
   !else
    !error "AbortIfBadFramework was passed a bad framework version ${MIN_FRA_MAJOR}.${MIN_FRA_MINOR}.${MIN_FRA_BUILD}."
   !endif
 
  !else if ${MIN_FRA_MINOR} == "7"
 
   !if ${MIN_FRA_BUILD} == "0"
    !define MIN_FRA_RELEASE "460798"
   !else if ${MIN_FRA_BUILD} == "1"
    !define MIN_FRA_RELEASE "461308"
   !else if ${MIN_FRA_BUILD} == "2"
    !define MIN_FRA_RELEASE "461808"
   !else
    !error "AbortIfBadFramework was passed a bad framework version ${MIN_FRA_MAJOR}.${MIN_FRA_MINOR}.${MIN_FRA_BUILD}."
   !endif
  !else
   !error "AbortIfBadFramework is not sure how to check .NET framework versions > V4.7."
  !endif
 
  ReadRegDWORD $R9 HKLM "SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full" Release
  IntCmp $R9 ${MIN_FRA_RELEASE} end wrong_framework end
 
  fail:
  StrCmp $R8 "0.0.0" no_framework
  goto wrong_framework
 
  no_framework:
  MessageBox MB_OK|MB_ICONSTOP "Installation failed.$\n$\n\
         This software requires Windows Framework version \
         ${MIN_FRA_MAJOR}.${MIN_FRA_MINOR}.${MIN_FRA_BUILD} or higher.$\n$\n\
         No version of Windows Framework is installed.$\n$\n\
         Please update your computer at http://windowsupdate.microsoft.com/."
  abort
 
  wrong_framework:
  MessageBox MB_OK|MB_ICONSTOP "Installation failed!$\n$\n\
         This software requires Windows Framework version \
         ${MIN_FRA_MAJOR}.${MIN_FRA_MINOR}.${MIN_FRA_BUILD} or higher.$\n$\n\
         The highest version on this computer is $R8.$\n$\n\
         Please update your computer at http://windowsupdate.microsoft.com/."
  abort
 
  end:
 
  ; Pop the variables we pushed earlier
  Pop $R8
  Pop $R7
  Pop $R6
  Pop $R5
  Pop $R4
  Pop $R3
  Pop $R2
  Pop $R1
  Pop $4
  Pop $3
  Pop $2
  Pop $1
  Pop $0
 
FunctionEnd

Function TrimQuotes
Exch $R0
Push $R1
 
  StrCpy $R1 $R0 1
  StrCmp $R1 `"` 0 +2
    StrCpy $R0 $R0 `` 1
  StrCpy $R1 $R0 1 -1
  StrCmp $R1 `"` 0 +2
    StrCpy $R0 $R0 -1
 
Pop $R1
Exch $R0
FunctionEnd
!macro _TrimQuotes Input Output
  Push `${Input}`
  Call TrimQuotes
  Pop ${Output}
!macroend
!define TrimQuotes `!insertmacro _TrimQuotes`

Section "Check .NET Framework Version"
Call AbortIfBadFramework
SectionEnd

Section "Backup and remove old version"
    ; Check for uninstaller.
    ReadRegStr $0 HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "UninstallString"
    ReadRegStr $1 HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "InstallLocation"
    ${TrimQuotes} $0 $0
    IfFileExists $0 0 Done
    MessageBox MB_OK "Uninstalling old version. Your database will be automatically backed up and restored to the new version."
    DetailPrint "Removing previous installation."    

    CreateDirectory "$1\..\DrFujiBot_Backup"
    CopyFiles "$1\DrFujiBot_Django\db.sqlite3" "$1\..\DrFujiBot_Backup\db_backup_before_uninstall.sqlite3"

    ${If} ${Errors}
        DetailPrint "Failed to back up existing database"    
        Abort "Failed to back up existing database"
        Goto Done
    ${EndIf}

    ; Run the uninstaller silently.
    ExecWait '"$0" /S _?=$INSTDIR'
    RMDir /r "$INSTDIR"

    Done:
SectionEnd
; End DrFujiBot add-in



!insertmacro MUI_PAGE_INSTFILES


; Start DrFujiBot add-in:
Function LaunchDrFujiBot
    ExecShell "open" "http://localhost:41945/admin/"
FunctionEnd
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "Launch DrFujiBot administration"
!define MUI_FINISHPAGE_RUN_FUNCTION "LaunchDrFujiBot"
; End DrFujiBot add-in


!insertmacro MUI_PAGE_FINISH
[% endblock ui_pages %]
!insertmacro MUI_LANGUAGE "English"
[% endblock modernui %]

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "${INSTALLER_NAME}"
ShowInstDetails show

Section -SETTINGS
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
SectionEnd

[% block sections %]

Section "!${PRODUCT_NAME}" sec_app
  SetRegView [[ib.py_bitness]]
  SectionIn RO
  File ${PRODUCT_ICON}
  SetOutPath "$INSTDIR\pkgs"
  File /r "pkgs\*.*"
  SetOutPath "$INSTDIR"

  ; Marker file for per-user install
  StrCmp $MultiUser.InstallMode CurrentUser 0 +3
    FileOpen $0 "$INSTDIR\${USER_INSTALL_MARKER}" w
    FileClose $0
    SetFileAttributes "$INSTDIR\${USER_INSTALL_MARKER}" HIDDEN

  [% block install_files %]
  ; Install files
  [% for destination, group in grouped_files %]
    SetOutPath "[[destination]]"
    [% for file in group %]
      File "[[ file ]]"
    [% endfor %]
  [% endfor %]
  
  ; Install directories
  [% for dir, destination in ib.install_dirs %]
    SetOutPath "[[ pjoin(destination, dir) ]]"
    File /r "[[dir]]\*.*"
  [% endfor %]
  [% endblock install_files %]
  
  [% block install_shortcuts %]
  ; Install shortcuts
  ; The output path becomes the working directory for shortcuts
  SetOutPath "%HOMEDRIVE%\%HOMEPATH%"
  [% if single_shortcut %]
    [% for scname, sc in ib.shortcuts.items() %]
    CreateShortCut "$SMPROGRAMS\[[scname]].lnk" "[[sc['target'] ]]" \
      '[[ sc['parameters'] ]]' "$INSTDIR\[[ sc['icon'] ]]"
    [% endfor %]
  [% else %]
    [# Multiple shortcuts: create a directory for them #]
    CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
    [% for scname, sc in ib.shortcuts.items() %]
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\[[scname]].lnk" "[[sc['target'] ]]" \
      '[[ sc['parameters'] ]]' "$INSTDIR\[[ sc['icon'] ]]"
    [% endfor %]
  [% endif %]
  SetOutPath "$INSTDIR"
  [% endblock install_shortcuts %]

  [% block install_commands %]
  [% if has_commands %]
    DetailPrint "Setting up command-line launchers..."
    nsExec::ExecToLog '[[ python ]] -Es "$INSTDIR\_assemble_launchers.py" [[ python ]] "$INSTDIR\bin"'

    StrCmp $MultiUser.InstallMode CurrentUser 0 AddSysPathSystem
      ; Add to PATH for current user
      nsExec::ExecToLog '[[ python ]] -Es "$INSTDIR\_system_path.py" add_user "$INSTDIR\bin"'
      GoTo AddedSysPath
    AddSysPathSystem:
      ; Add to PATH for all users
      nsExec::ExecToLog '[[ python ]] -Es "$INSTDIR\_system_path.py" add "$INSTDIR\bin"'
    AddedSysPath:
  [% endif %]
  [% endblock install_commands %]
  
  ; Byte-compile Python files.
  DetailPrint "Byte-compiling Python modules..."
  nsExec::ExecToLog '[[ python ]] -m compileall -q "$INSTDIR\pkgs"'
  WriteUninstaller $INSTDIR\uninstall.exe
  ; Add ourselves to Add/remove programs
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "InstallLocation" "$INSTDIR"
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "DisplayIcon" "$INSTDIR\${PRODUCT_ICON}"
  [% if ib.publisher is not none %]
    WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                     "Publisher" "[[ib.publisher]]"
  [% endif %]
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegDWORD SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "NoModify" 1
  WriteRegDWORD SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "NoRepair" 1

  ; Check if we need to reboot
  IfRebootFlag 0 noreboot
    MessageBox MB_YESNO "A reboot is required to finish the installation. Do you wish to reboot now?" \
                /SD IDNO IDNO noreboot
      Reboot
  noreboot:
SectionEnd

Section "Uninstall"
  SetRegView [[ib.py_bitness]]
  SetShellVarContext all
  IfFileExists "$INSTDIR\${USER_INSTALL_MARKER}" 0 +3
    SetShellVarContext current
    Delete "$INSTDIR\${USER_INSTALL_MARKER}"

  Delete $INSTDIR\uninstall.exe
  Delete "$INSTDIR\${PRODUCT_ICON}"
  RMDir /r "$INSTDIR\pkgs"

  ; Remove ourselves from %PATH%
  [% block uninstall_commands %]
  [% if has_commands %]
    nsExec::ExecToLog '[[ python ]] -Es "$INSTDIR\_system_path.py" remove "$INSTDIR\bin"'
  [% endif %]
  [% endblock uninstall_commands %]

  [% block uninstall_files %]
  ; Uninstall files
  [% for file, destination in ib.install_files %]
    Delete "[[pjoin(destination, file)]]"
  [% endfor %]
  ; Uninstall directories
  [% for dir, destination in ib.install_dirs %]
    RMDir /r "[[pjoin(destination, dir)]]"
  [% endfor %]
  [% endblock uninstall_files %]

  [% block uninstall_shortcuts %]
  ; Uninstall shortcuts
  [% if single_shortcut %]
    [% for scname in ib.shortcuts %]
      Delete "$SMPROGRAMS\[[scname]].lnk"
    [% endfor %]
  [% else %]
    RMDir /r "$SMPROGRAMS\${PRODUCT_NAME}"
  [% endif %]
  [% endblock uninstall_shortcuts %]
  RMDir $INSTDIR
  DeleteRegKey SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
SectionEnd

[% endblock sections %]

; Functions

Function .onMouseOverSection
    ; Find which section the mouse is over, and set the corresponding description.
    FindWindow $R0 "#32770" "" $HWNDPARENT
    GetDlgItem $R0 $R0 1043 ; description item (must be added to the UI)

    [% block mouseover_messages %]
    StrCmp $0 ${sec_app} "" +2
      SendMessage $R0 ${WM_SETTEXT} 0 "STR:${PRODUCT_NAME}"
    
    [% endblock mouseover_messages %]
FunctionEnd

Function .onInit
  !insertmacro MULTIUSER_INIT
FunctionEnd

Function un.onInit
  !insertmacro MULTIUSER_UNINIT
FunctionEnd

[% if ib.py_bitness == 64 %]
Function correct_prog_files
  ; The multiuser machinery doesn't know about the different Program files
  ; folder for 64-bit applications. Override the install dir it set.
  StrCmp $MultiUser.InstallMode AllUsers 0 +2
    StrCpy $INSTDIR "$PROGRAMFILES64\${MULTIUSER_INSTALLMODE_INSTDIR}"
FunctionEnd
[% endif %]
