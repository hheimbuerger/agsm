description = "merges stats screenshots"
longName = "AllegGameStatsMerger"
name = "AGSM"
icon = "AllegGameStatsMerger.ico"
exeFilename = "AllegGameStatsMerger"
versionNumber = "1.1"
allegPathRegistryKey = "SOFTWARE\\Microsoft\\Microsoft Games\\Allegiance\\1.0"
allegPathRegistryValue = "EXE Path"
distDir = "dist"



# these are the files we want to package with the executable
requiredExternalFiles = (
                    icon,
                    "Logo.png",
                    "ScrollbarPointerDown.png",
                    "ScrollbarPointerUp.png",
                    "StatsScreenBottomBorder.png",
                    "StatsScreenLeftBorder.png",
                    "StatsScreenRightBorder.png",
                    "StatsScreenTopBorder.png",
                    "StatsScreenDetectionTemplate.png",
                  )
