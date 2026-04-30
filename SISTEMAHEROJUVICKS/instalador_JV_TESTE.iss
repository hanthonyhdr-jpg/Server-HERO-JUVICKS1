[Setup]
AppId={{7B174844-2B5A-46C8-BF2D-C86C5B35E05E}}
AppName=JV TESTE
AppVersion=1.0.0
AppPublisher=Minha Empresa
DefaultDirName={autopf}\JVTESTE
DefaultGroupName=JV TESTE
OutputDir=H:\JUVIX SERVER OPERACIONAL VERSAO FINAL - Copia\SISTEMA LIMPO - ESTAVEL\Output
OutputBaseFilename=Instalador_JV_TESTE
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin



[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "H:\JUVIX SERVER OPERACIONAL VERSAO FINAL - Copia\SISTEMA LIMPO - ESTAVEL\dist\JV_TESTE\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\JV TESTE"; Filename: "{app}\JV_TESTE.exe"
Name: "{autodesktop}\JV TESTE"; Filename: "{app}\JV_TESTE.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\JV_TESTE.exe"; Description: "{cm:LaunchProgram,JV TESTE}"; Flags: nowait postinstall skipifsilent
