; Inno Setup script for the Arsis installer. Built by scripts\build-windows.ps1:
;   ISCC.exe /DAppVersion=0.1.0 packaging\arsis.iss
;
; Per-user install, no administrator rights. Updating = running a newer
; installer: it replaces the program files only. Data in %LOCALAPPDATA%\Arsis
; (database, backups, secret key, logs) is never touched by install, update or
; uninstall; Arsis migrates the database itself on the next start, after a backup.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
; Keep this AppId forever: it is how updates find the existing installation.
AppId={{7B1F4C2E-5A9D-4E3B-9C61-3F0A2D8E4B17}
AppName=Arsis
AppVersion={#AppVersion}
AppPublisher=Arsis
DefaultDirName={localappdata}\Programs\Arsis
DefaultGroupName=Arsis
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\build\installer
OutputBaseFilename=Arsis-Setup-{#AppVersion}
SetupIconFile=..\build\arsis.ico
UninstallDisplayIcon={app}\Arsis.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; The running app holds its files open: ask to close it before replacing them.
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Replace the whole program folder so files removed in a new version do not linger.
Source: "..\build\pyinstaller\dist\Arsis\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[InstallDelete]
Type: filesandordirs; Name: "{app}\_internal"

[Icons]
Name: "{group}\Arsis"; Filename: "{app}\Arsis.exe"
Name: "{group}\Disinstalla Arsis"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Arsis"; Filename: "{app}\Arsis.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Arsis.exe"; Description: "{cm:LaunchProgram,Arsis}"; Flags: nowait postinstall skipifsilent
