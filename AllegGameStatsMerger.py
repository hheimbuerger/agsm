import wx
import MainWindow
import settings
import os.path
import sys



if(__name__ == "__main__"):
    app = wx.App(0)
#    try:

    for file in settings.requiredExternalFiles:
        if(not os.path.isfile(file)):
            wx.MessageDialog(None,
                 message="The file '%s' is required, but couldn't be found in the application's working directory. Application will now terminate." % (file),
                 caption="Missing file",
                 style=wx.OK | wx.ICON_ERROR).ShowModal()
            sys.exit(1)

    window = MainWindow.MainWindow()
    app.MainLoop()
#    except Exception, exc:
#        wx.MessageDialog(self,
#              message="A general exception occured. Please report the error together with a description of what you did. More information:\n\n%s" % (exc.strerror),
#              caption="Exception",
#              style=wx.OK | wx.ICON_ERROR).ShowModal()
