from distutils.core import setup
import py2exe
import settings
import os.path
import sys



# now create the actual exe and do all the packaging
print "Starting to generate the executable."
#oldWorkingDirectory = os.getcwd()
os.chdir("src/")
origStdout = sys.stdout
py2exeLog = open("../py2exe.log", "w")
sys.stdout = py2exeLog
setup(
    name = settings.name,
    version = settings.versionNumber,
    description = settings.description,

    # targets to build
    windows = [{
                'script': "AllegGameStatsMerger.py",
                'icon_resources': [(0, os.path.join("../media/", settings.icon))],
                'dest_base': settings.exeFilename
               }],
    options = {'py2exe':
                   {
                        'dist_dir': os.path.join("../", settings.distDir),
                        'compressed': True,
                        #'optimize': 2,
                        'bundle_files': True,
                        #'build_dir': "../build"
                   }
              },
    zipfile = None, #"application.lib",
    )
sys.stdout = origStdout
py2exeLog.close()
print "  Executable generated, log in py2exe.log"
#os.chdir(oldWorkingDirectory)
