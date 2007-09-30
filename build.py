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


from src import settings
import os
import shutil
import os.path
import sys



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
#originalArguments = sys.argv[1:]
#sys.argv = [sys.argv[0], "py2exe"]
#sys.argv.extend(originalArguments)

# now create the executable
os.system("src\\build.py py2exe")

# wrap the Release Notes
response = os.popen("tools\TextfileWrapper.py \"# Release\ReleaseNotes_unwrapped.txt\" \"# Release\ReleaseNotes.txt\"")
result = response.readlines()
if(response.close()):
    print "ReleaseNotes wrapping failed!"
    sys.exit(1)
else:
    print "ReleaseNotes wrapped successfully:"
    print "  " + result[0].strip()

# add some additional files to the distribution
for file in settings.requiredExternalFiles:
    shutil.copy2(os.path.join("media/", file), settings.distDir + "/")
shutil.copy2("# Release\ReleaseNotes.txt", settings.distDir + "/")
print "Additional files copied into the distribution directory."

# generate the installer
if("/noinstaller" not in sys.argv):
    response = os.popen("iscc Installer.iss")
    result = response.readlines()
    issLog = open("iss.log", "w")
    issLog.writelines(result)
    issLog.close()
    if(response.close()):
        print "Generating the installer failed! (Is iscc.exe in your path?) Please check the log in iss.log"
        sys.exit(1)
    else:
        print "  Installer generated, log in iss.log"
