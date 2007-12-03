import wx

import settings



class AboutWindow(wx.Dialog):
    
    def __init__(self, parent):
        wx.Dialog.__init__(self,
                          parent=parent,
                          style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.FRAME_NO_TASKBAR | wx.FRAME_FLOAT_ON_PARENT,
                          size=(400, 300),
                          title="About %s v%s" % (settings.name, settings.versionNumber)
                         )

#===============================================================================
#        # set window icon
#        wx.InitAllImageHandlers()
#        iconBundle = wx.IconBundle()
#        # DEBUG: method to retrieve icon from executable temporarily removed, because that doesn't seem to work with IconBundle and SetIcons()
#        #if hasattr(sys,"frozen") and sys.frozen == "windows_exe":
#        #    exeName = sys.executable #"main.exe" #win32api.GetModuleFileName(win32api.GetModuleHandle(None))
#        #    iconBundle.AddIconFromFile(exeName, wx.BITMAP_TYPE_ICO)
#        #else:
#        #    iconBundle.AddIconFromFile(settings.icon, wx.BITMAP_TYPE_ANY)
#        iconBundle.AddIconFromFile(settings.icon, wx.BITMAP_TYPE_ANY)
#        self.SetIcons(iconBundle)
#===============================================================================

        # base structure (panel as the base control, two static boxes inside it)
        basePanel = wx.Panel(self)
        
        # create the items
        icon = wx.Icon(settings.icon, wx.BITMAP_TYPE_ANY) #iconBundle.AddIconFromFile(settings.icon, wx.BITMAP_TYPE_ANY)
        logo = wx.BitmapFromImage(wx.Image("Logo.png"))
        bitmapLogo = wx.StaticBitmap(parent=basePanel, style=wx.SUNKEN_BORDER, bitmap=logo)
        text = "%s (%s) v%s\n\n" \
               "Merges existing game stats screenshots from Allegiance to a complete image.\n\n" \
               "Please report any errors you find and include the version number, the screenshots you tried to process and the " \
               "log.\n\n" \
               "Quick instructions:\n" \
               "  1. Confirm your Allegiance directory has been detected correctly.\n" \
               "  2. Click on the 'Process' button.\n" \
               "  3. Look in the clusters list for the game whose stats you want to merge.\n" \
               "  4. Check the log to make sure merging was successful.\n" \
               "  5. Modify the file name at the bottom if needed and click on 'Save'.\n" \
               "\n" \
               "\n" \
               "Contact information:\n" \
               % (settings.name, settings.longName, settings.versionNumber)
        labelText = wx.StaticText(parent=basePanel, label=text)
        buttonOK = wx.Button(parent=basePanel, label="OK")
        hyperlinkEMail = wx.HyperlinkCtrl(parent=basePanel, id=wx.ID_ANY, style=wx.NO_BORDER | wx.HL_ALIGN_LEFT | wx.HL_CONTEXTMENU, label="e-mail to henrik@heimbuerger.de", url="mailto:henrik@heimbuerger.de")
        hyperlinkForum = wx.HyperlinkCtrl(parent=basePanel, id=wx.ID_ANY, style=wx.NO_BORDER | wx.HL_ALIGN_LEFT | wx.HL_CONTEXTMENU, label="PM 'Cortex' at the freeallegiance.org boards", url="http://www.freeallegiance.org/forums/index.php?showuser=4012")
        
        # create the sizers
        hsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer.Add(labelText, proportion=0)
        hsizer.Add(hyperlinkEMail, proportion=0, flag=wx.LEFT, border=20)
        hsizer.Add(hyperlinkForum, proportion=0, flag=wx.LEFT, border=20)
        logoTextSizer = wx.BoxSizer(wx.HORIZONTAL)
        logoTextSizer.Add(bitmapLogo, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER, border=30)
        logoTextSizer.Add(hsizer, proportion=1)        # , flag=wx.ALL, border=30
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(logoTextSizer, proportion=1, flag=wx.ALL, border=20)
        vsizer.Add(buttonOK, proportion=0, flag=wx.EXPAND | wx.ALL, border=20)
        basePanel.SetSizer(vsizer)
        basePanel.SetAutoLayout(True)
        vsizer.Fit(self)
        
        # bind event handlers
        buttonOK.Bind(wx.EVT_BUTTON, self.doClose)
        
#===============================================================================
#        upperBox = wx.StaticBox(basePanel, -1, "Screenshot processing")
#        lowerBox = wx.StaticBox(basePanel, -1, "Results")
#        
#        # add a status bar
#        self.CreateStatusBar() # A Statusbar in the bottom of the window
# 
#        # add the menu
#        menuBarStructure = [
#                (
#                    "File",
#                    "",
#                    (
#                         #("&Generate", "Parse all screenshots, try to find clusters and merge them if possible", self.???),
#                         #None,
#                         ("E&xit", "Close the application", self.doExit),
#                         #[
#                         #     ("Submenu",
#                         #      "",
#                         #      (
#                         #           ("Test", "Test item", None),
#                         #      ),
#                         #     )
#                         #]
#                    ),
#                ),
#                (
#                    "Help",
#                    "",
#                    (
#                         ("Help / &About", "Show the about screen", self.doShowCredits),
#                    ),
#                ),
#            ]
#        self.SetMenuBar(MenuBarCreator.createMenuBar(self, menuBarStructure))
#        
#        # create the controls in the upper box
#        labelSourceDir = wx.StaticText(parent=basePanel, label="Source directory")
#        labelTimeframe = wx.StaticText(parent=basePanel, label="Screenshot timeframe (s)")
#        self.pickerctrlSourceDir = wx.DirPickerCtrl(parent=basePanel, style=wx.DIRP_USE_TEXTCTRL | wx.DIRP_DIR_MUST_EXIST, message="Please select the directory Allegiance stores your screenshots in.") #wx.TextCtrl(parent=basePanel, value="e:\\Alleg")
#        self.spinTimeframe = wx.SpinCtrl(parent=basePanel, min=1, max=60*60, initial=60)
#        self.buttonProcess = wx.Button(parent=basePanel, label="Process")
#        self.gaugeProgress = wx.Gauge(parent=basePanel, size=(-1, 10), style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)
#        
#        # create the controls for the lower box
#        labelClusters = wx.StaticText(parent=basePanel, label="Detected clusters (latest first):")
#        self.listClusters = wx.ListBox(parent=basePanel, style=wx.LB_SINGLE | wx.LB_ALWAYS_SB)
#        labelPreview = wx.StaticText(parent=basePanel, label="Preview of merged image:")
#        self.imagePreview = wx.StaticBitmap(parent=basePanel, size=(MainWindow.PREVIEW_WIDTH, -1), style=wx.SUNKEN_BORDER)        #, bitmap=wxIm
#        self.imagePreview.SetMaxSize((MainWindow.PREVIEW_WIDTH, -1))
#        self.imagePreview.SetMinSize((MainWindow.PREVIEW_WIDTH, -1))
#        self.scrollPreview = wx.ScrollBar(basePanel, style=wx.SB_VERTICAL)
#        labelLog = wx.StaticText(parent=basePanel, label="Log:")
#        self.textboxLog = wx.TextCtrl(parent=basePanel, style=wx.TE_READONLY | wx.TE_MULTILINE)
#        labelSave = wx.StaticText(parent=basePanel, label="Save merged image:")
#        self.pickerctrlTargetFile = wx.FilePickerCtrl(parent=basePanel, style=wx.FLP_USE_TEXTCTRL | wx.FLP_SAVE | wx.FLP_OVERWRITE_PROMPT, message="Please select the path and filename you want to write the merged image to.", wildcard="Portable Network Graphics (PNG) files (*.png)|*.png")
#        self.buttonSave = wx.Button(parent=basePanel, label="Save")
#        
#        # set up all the sizers for the upper box
#        upperSizer = wx.StaticBoxSizer(upperBox, wx.HORIZONTAL)
#        generationSizer = wx.GridBagSizer(5, 20)
#        generationSizer.AddGrowableCol(1)
#        generationSizer.Add(labelSourceDir, pos=(0, 0), flag=wx.ALIGN_LEFT | wx.TOP, border=3)
#        generationSizer.Add(self.pickerctrlSourceDir, pos=(0, 1), flag=wx.EXPAND)
#        generationSizer.Add(labelTimeframe, pos=(1, 0), flag=wx.ALIGN_LEFT | wx.TOP, border=3)
#        generationSizer.Add(self.spinTimeframe, pos=(1, 1), flag=wx.ALIGN_LEFT)
#        generationSizer.Add(self.buttonProcess, pos=(2, 0), flag=wx.EXPAND)
#        generationSizer.Add(self.gaugeProgress, pos=(2, 1), flag=wx.EXPAND)
#        upperSizer.Add(generationSizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
#        
#        # set up all the sizers for the lower box
#        lowerSizer = wx.StaticBoxSizer(lowerBox, wx.VERTICAL)
#        lowerSizer.Add(labelClusters, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
#        lowerSizer.Add(self.listClusters, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
#        lowerSizer.Add(labelPreview, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
#        previewSizer = wx.BoxSizer(wx.HORIZONTAL)
#        previewSizer.Add(self.imagePreview, proportion=0, flag=wx.EXPAND)
#        previewSizer.Add(self.scrollPreview, proportion=0, flag=wx.EXPAND | wx.LEFT, border=10)
#        lowerSizer.Add(previewSizer, proportion=5, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
#        lowerSizer.Add(labelLog, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
#        lowerSizer.Add(self.textboxLog, proportion=2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
#        lowerSizer.Add(labelSave, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
#        saveLineSizer = wx.BoxSizer(wx.HORIZONTAL)
#        saveLineSizer.Add(self.pickerctrlTargetFile, proportion=1, flag=wx.EXPAND)
#        saveLineSizer.Add(self.buttonSave, proportion=0, flag=wx.EXPAND | wx.LEFT, border=10)
#        lowerSizer.Add(saveLineSizer, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
# 
#        # set up the main sizer (separating the two static boxes)
#        sizer = wx.BoxSizer(wx.VERTICAL)
#        sizer.Add(upperSizer, proportion=0, flag=wx.EXPAND)
#        sizer.Add((1, 10), proportion=0, flag=wx.EXPAND)
#        sizer.Add(lowerSizer, proportion=1, flag=wx.EXPAND)
#        
#        # set up the border size and initialise the sizers
#        border = wx.BoxSizer()
#        border.Add(sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=10) 
#        basePanel.SetSizer(border)
#        basePanel.SetAutoLayout(1)
#        border.Fit(self)
#        
#        # set initial configuration
#        self.onClusterSelect(None)
#        self.SetStatusText("Ready.")
# 
#        # bind events
#        self.listClusters.Bind(wx.EVT_LISTBOX, self.onClusterSelect)
#        self.buttonProcess.Bind(wx.EVT_BUTTON, self.onButtonProcessAbortClick)
#        self.imagePreview.Bind(wx.EVT_SIZE, self.updatePreviewDetail)
#        self.scrollPreview.Bind(wx.EVT_SCROLL, self.updatePreviewDetail)
#        self.buttonSave.Bind(wx.EVT_BUTTON, self.saveMergedImage)
#        self.Bind(wx.EVT_CLOSE, self.onClose)
#===============================================================================

        # show the window
        self.Centre()
        #self.Show(True)                  # show the window


    def doClose(self, event):
        self.Close()
