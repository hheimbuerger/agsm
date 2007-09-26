; -- Example2.iss --
; Same as Example1.iss, but creates its icon in the Programs folder of the
; Start Menu instead of in a subfolder, and also creates a desktop icon.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

[Setup]
AppName=AGSM
AppVerName=AllegGameStatsMerger v1.0
DefaultDirName={pf}\Microsoft Games\Allegiance\AGSM
DefaultGroupName=Allegiance
UninstallDisplayIcon={app}\AllegGameStatsMerger.exe
OutputDir=installer_dist
OutputBaseFilename=AGSM_v1.0
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\*"; DestDir: "{app}"

[Icons]
Name: "{commonprograms}\Allegiance\AGSM"; Filename: "{app}\AllegGameStatsMerger.exe"; WorkingDir: "{app}"
;Name: "{commondesktop}\My Program"; Filename: "{app}\MyProg.exe"

