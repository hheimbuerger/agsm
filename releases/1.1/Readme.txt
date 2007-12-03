The following libs and tools have been used:
  • PIL (http://www.pythonware.com/products/pil/)
  • wxPython (http://www.wxpython.org/)
  • py2exe (http://www.py2exe.org/) to generate the executable
  • Inno Setup (http://www.jrsoftware.org/isinfo.php) to generate the installer
  • TextfileWrapper.py (included) to wrap the release notes
  
The buildfile (build.py) will prepare a release almost completely if all of the above
tools are available. PIL, wxPython and py2exe need to be installed. Inno Setup has to
be in the path.

When running the application locally without creating an executable, remember that the
working directory *has* to be set to /media.
