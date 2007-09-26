import wx
import MainWindow
        


if(__name__ == "__main__"):
    app = wx.App(0)
    try:
        window = MainWindow.MainWindow()
        app.MainLoop()
    except Exception, exc:
        wx.MessageDialog(self,
              message="A general exception occured. Please report the error together with a description of what you did. More information:\n\n%s" % (exc.strerror),
              caption="Exception",
              style=wx.OK | wx.ICON_ERROR).ShowModal()
