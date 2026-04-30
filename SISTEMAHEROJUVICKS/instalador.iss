[Setup]
AppName=HERO_JUVICKS_SERVER_10
AppVersion=1.0.0
AppPublisher=Juviks Solutions
AppPublisherURL=https://juviks.com
DefaultDirName={commonpf}\HERO_JUVICKS_SERVER_10
DefaultGroupName=Juviks Server
DisableProgramGroupPage=yes
OutputBaseFilename=Instalador_HERO_JUVICKS_SERVER_10_OFICIAL
OutputDir=Output
PrivilegesRequired=admin
Compression=lzma
SolidCompression=yes
WizardStyle=modern dark
WizardStyleFile=builtin:polar
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=ICONE\ICONE.ico
UninstallDisplayIcon={app}\HERO_JUVICKS_SERVER_10.exe

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "Iniciar o sistema automaticamente com o Windows"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; O diretório principal gerado pelo PyInstaller (Modo OneDir/COLLECT)
Source: "dist\HERO_JUVICKS_SERVER_10\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "ngrok.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\HERO_JUVICKS_SERVER_10"; Filename: "{app}\HERO_JUVICKS_SERVER_10.exe"
Name: "{autodesktop}\HERO_JUVICKS_SERVER_10"; Filename: "{app}\HERO_JUVICKS_SERVER_10.exe"; Tasks: desktopicon

[Registry]
; Registra o sistema para iniciar com o Windows (HKCU para não exigir admin extra no boot)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "HERO_JUVICKS_SERVER_10"; ValueData: """{app}\HERO_JUVICKS_SERVER_10.exe"""; Flags: uninsdeletevalue; Tasks: startup

[InstallDelete]
; Apaga sessão salva da instalação anterior para forçar novo login com chave de acesso
Type: files; Name: "{localappdata}\JUVICKS_DATA\sessions\last_session.json"

[Run]
Filename: "{app}\HERO_JUVICKS_SERVER_10.exe"; Description: "{cm:LaunchProgram,Juviks Server}"; Flags: nowait postinstall skipifsilent
