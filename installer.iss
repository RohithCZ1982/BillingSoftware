; Inno Setup Script — School Uniform Billing System
; Download Inno Setup: https://jrsoftware.org/isdl.php

#define AppName      "School Uniform Billing"
#define AppVersion   "1.0.0"
#define AppPublisher "Your Shop Name"
#define AppExeName   "UniformBilling.exe"
#define BuildDir     "dist\UniformBilling"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisherURL=
AppSupportURL=
AppUpdatesURL=
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
LicenseFile=
OutputDir=installer_output
OutputBaseFilename=UniformBilling_Setup_v{#AppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";    Description: "{cm:CreateDesktopIcon}";    GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main application bundle (everything PyInstaller produced)
Source: "{#BuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Create the writable data folders inside AppData so they survive updates
; (bills, backups, database are stored in the install dir for simplicity)

[Dirs]
Name: "{app}\bills";   Permissions: users-modify
Name: "{app}\backups"; Permissions: users-modify

[Icons]
Name: "{group}\{#AppName}";        Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";  Filename: "{app}\{#AppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: quicklaunchicon

[Run]
; Offer to launch immediately after install
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Remove the database and generated files on uninstall only if user chooses
; (comment these out if you want to preserve user data on uninstall)
; Type: filesandordirs; Name: "{app}\billing.db"
; Type: filesandordirs; Name: "{app}\bills"
; Type: filesandordirs; Name: "{app}\backups"
