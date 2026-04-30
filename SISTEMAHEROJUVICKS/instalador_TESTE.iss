[Setup]
AppId={{97E99C67-C019-42D3-9032-69BDE1A66E03}}
AppName=TESTE
AppVersion=1.0.0
AppPublisher=Minha Empresa
DefaultDirName={autopf}\TESTE
DefaultGroupName=TESTE
OutputDir=H:\JUVIX SERVER OPERACIONAL VERSAO FINAL - Copia\SISTEMA LIMPO - ESTAVEL\Output
OutputBaseFilename=Instalador_TESTE
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
SetupIconFile=ICONE\ICONE.ico
UninstallDisplayIcon={app}\TESTE.exe

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "H:\JUVIX SERVER OPERACIONAL VERSAO FINAL - Copia\SISTEMA LIMPO - ESTAVEL\dist\TESTE\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\TESTE"; Filename: "{app}\TESTE.exe"
Name: "{autodesktop}\TESTE"; Filename: "{app}\TESTE.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\TESTE.exe"; Description: "{cm:LaunchProgram,TESTE}"; Flags: nowait postinstall skipifsilent
