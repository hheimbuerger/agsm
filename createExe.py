# A very simple setup script to create 2 executables.
#
# hello.py is a simple "hello, world" type program, which alse allows
# to explore the environment in which the script runs.
#
# test_wx.py is a simple wxPython program, it will be converted into a
# console-less program.
#
# If you don't have wxPython installed, you should comment out the
#   windows = ["test_wx.py"]
# line below.
#
#
# // Run the build process by entering 'setup.py py2exe' or
# // 'python setup.py py2exe' in a console prompt.
# No longer necessary, the scripts adds this to the command line itself. -- Cort
# (There's probably a better way than tinkering with sys.argv, but I don't know it.)
#
# If everything works well, you should find a subdirectory named 'dist'
# containing some files, among them hello.exe and test_wx.exe.


from distutils.core import setup
import settings
import py2exe
import os
import shutil
import sys



# these are the files we want to package with the executable
additionalFiles = (
                    settings.icon,
                    "Logo.png",
                    "ScrollbarPointerDown.png",
                    "ScrollbarPointerUp.png",
                    "StatsScreenBottomBorder.png",
                    "StatsScreenLeftBorder.png",
                    "StatsScreenRightBorder.png",
                    "StatsScreenTopBorder.png",
                  )

# delete old dist directory (just to be sure)
if(settings.distDir in os.listdir(".")):
    shutil.rmtree(settings.distDir)
    print "dir %s has been deleted" % (settings.distDir)
else:
    print "dir %s doesn't exist, don't have to delete" % (settings.distDir)

# create the icon
#response = os.popen("icon\png2ico %s icon/16x16.png icon/32x32.png icon/48x48.png" % (settings.icon))
#if(response.close()):
#    print "Generating the icon failed!"
#    sys.exit(1)
#else:
#    print "Icon created successfully."

# add "py2exe" to the command line of this script
originalArguments = sys.argv[1:]
sys.argv = [sys.argv[0], "py2exe"]
sys.argv.extend(originalArguments)

# now create the actual exe and do all the packaging
print "Starting to generate the executable."
origStdout = sys.stdout
py2exeLog = open("py2exe.log", "w")
sys.stdout = py2exeLog
setup(
    name = settings.name,
    version = settings.versionNumber,
    description = settings.description,

    # targets to build
    windows = [{
                'script': "AllegGameStatsMerger.py",
                'icon_resources': [(0, settings.icon)],
                'dest_base': settings.exeFilename
               }],
    options = {'py2exe':
                   {
                        'dist_dir': settings.distDir
                   }
              },
    zipfile = "application.lib",
    )
sys.stdout = origStdout
py2exeLog.close()
print "Executable generated, log in py2exe.log."

# add some additional files to the distribution
for file in additionalFiles:
    shutil.copy2(file, settings.distDir)
print "Additional files copied into the distribution directory."