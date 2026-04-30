[Setup]
AppId={{DD69BC84-52F1-431C-87DD-05F3F7F2A4CC}}
AppName=HERO JUVICKS SERVER 0.7
AppVersion=1.0.0
AppPublisher=Minha Empresa
DefaultDirName={autopf}\HEROJUVICKSSERVER0.7
DefaultGroupName=HERO JUVICKS SERVER 0.7
OutputDir=Output
OutputBaseFilename=Instalador_HERO_JUVICKS_SERVER_0.7
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
SetupIconFile=..\..\JUVIX SERVER OPERACIONAL VERSAO FINAL - bkp\SISTEMA LIMPO - ESTAVEL\ICONE\ICONE.ico
UninstallDisplayIcon={app}\HERO_JUVICKS_SERVER_0.7.exe

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\HERO_JUVICKS_SERVER_0.7\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\HERO JUVICKS SERVER 0.7"; Filename: "{app}\HERO_JUVICKS_SERVER_0.7.exe"
Name: "{autodesktop}\HERO JUVICKS SERVER 0.7"; Filename: "{app}\HERO_JUVICKS_SERVER_0.7.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\HERO_JUVICKS_SERVER_0.7.exe"; Description: "{cm:LaunchProgram,HERO JUVICKS SERVER 0.7}"; Flags: nowait postinstall skipifsilent
