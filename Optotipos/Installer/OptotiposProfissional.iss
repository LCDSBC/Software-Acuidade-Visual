#define MyAppName "Optotipos Profissional"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Optotipos Profissional"
#define MyAppExeName "Optotipos.exe"

[Setup]
AppId={{8D7E0F71-2CB0-47C0-9C40-64213DFCF3D9}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Optotipos Profissional
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=Optotipos_Profissional_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\Optotipos.exe

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Area de Trabalho"; GroupDescription: "Atalhos:"; Flags: checkedonce

[Files]
Source: "..\dist\Optotipos_Portatil\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Optotipos Profissional"; Filename: "{app}\Optotipos.exe"; WorkingDir: "{app}"
Name: "{group}\Configurador"; Filename: "{app}\Configurador.exe"; WorkingDir: "{app}"
Name: "{group}\Manual de Uso"; Filename: "{app}\Manual\MANUAL_DE_USO.md"; WorkingDir: "{app}\Manual"
Name: "{autodesktop}\Optotipos Profissional"; Filename: "{app}\Optotipos.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\Optotipos.exe"; Description: "Abrir Optotipos Profissional"; Flags: nowait postinstall skipifsilent
