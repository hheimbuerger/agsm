import sys
import os.path
import threading, thread

import wx
import Image

import settings
import MenuBarCreator
from StatsMerger import StatsMerger
from AboutWindow import AboutWindow



class MainWindow(wx.Frame):
    PREVIEW_WIDTH = 600+4
    FILES_TO_PARSE_WARNING_THRESHOLD = 100
    
    def __init__(self):
        self.currentPreviewImage = None
        #self.workerThread = None
        #self.processingFinishedEvent = None
        self.isProcessing = False
        self.statsMerger = None
        
        wx.Frame.__init__(self,
                          parent=None,
                          #pos=wx.Point(int(xmlElement.getAttribute("xpos")), int(xmlElement.getAttribute("ypos"))),
                          #size=(60+MainWindow.PREVIEW_WIDTH, 600),
                          style=wx.DEFAULT_FRAME_STYLE,
                          title="%s v%s" % (settings.name, settings.versionNumber)
                         )

        # set window icon
        wx.InitAllImageHandlers()
        iconBundle = wx.IconBundle()
        # DEBUG: method to retrieve icon from executable temporarily removed, because that doesn't seem to work with IconBundle and SetIcons()
        #if hasattr(sys,"frozen") and sys.frozen == "windows_exe":
        #    exeName = sys.executable #"main.exe" #win32api.GetModuleFileName(win32api.GetModuleHandle(None))
        #    iconBundle.AddIconFromFile(exeName, wx.BITMAP_TYPE_ICO)
        #else:
        #    iconBundle.AddIconFromFile(settings.icon, wx.BITMAP_TYPE_ANY)
        iconBundle.AddIconFromFile(settings.icon, wx.BITMAP_TYPE_ANY)
        self.SetIcons(iconBundle)

        # base structure (panel as the base control, two static boxes inside it)
        basePanel = wx.Panel(self)
        upperBox = wx.StaticBox(basePanel, -1, "Screenshot processing")
        lowerBox = wx.StaticBox(basePanel, -1, "Results")
        
        # add a status bar
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        # add the menu
        menuBarStructure = [
                (
                    "File",
                    "",
                    (
                         #("&Generate", "Parse all screenshots, try to find clusters and merge them if possible", self.???),
                         #None,
                         ("E&xit", "Close the application", self.doExit),
                         #[
                         #     ("Submenu",
                         #      "",
                         #      (
                         #           ("Test", "Test item", None),
                         #      ),
                         #     )
                         #]
                    ),
                ),
                (
                    "Help",
                    "",
                    (
                         ("&About / Quickstart", "Show the about screen", self.doShowCredits),
                    ),
                ),
            ]
        self.SetMenuBar(MenuBarCreator.createMenuBar(self, menuBarStructure))
        
        # create the controls in the upper box
        labelSourceDir = wx.StaticText(parent=basePanel, label="Source directory")
        labelTimeframe = wx.StaticText(parent=basePanel, label="Screenshot timeframe (s)")
        self.pickerctrlSourceDir = wx.DirPickerCtrl(parent=basePanel, style=wx.DIRP_USE_TEXTCTRL | wx.DIRP_DIR_MUST_EXIST, message="Please select the directory Allegiance stores your screenshots in.") #wx.TextCtrl(parent=basePanel, value="e:\\Alleg")
        self.spinTimeframe = wx.SpinCtrl(parent=basePanel, min=1, max=60*60, initial=60)
        self.buttonProcess = wx.Button(parent=basePanel, label="Process")
        self.gaugeProgress = wx.Gauge(parent=basePanel, size=(-1, 10), style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)
        
        # create the controls for the lower box
        labelClusters = wx.StaticText(parent=basePanel, label="Detected clusters (latest first):")
        self.listClusters = wx.ListBox(parent=basePanel, style=wx.LB_SINGLE | wx.LB_ALWAYS_SB)
        labelPreview = wx.StaticText(parent=basePanel, label="Preview of merged image:")
        #self.imagePreview = wx.StaticBitmap(parent=basePanel, size=(MainWindow.PREVIEW_WIDTH, -1), style=wx.SUNKEN_BORDER)        #, bitmap=wxIm
        self.imagePreview = wx.Panel(parent=basePanel, size=(MainWindow.PREVIEW_WIDTH, -1), style=wx.SUNKEN_BORDER)        #, bitmap=wxIm
        self.imagePreview.SetMaxSize((MainWindow.PREVIEW_WIDTH, -1))
        self.imagePreview.SetMinSize((MainWindow.PREVIEW_WIDTH, -1))
        self.scrollPreview = wx.ScrollBar(basePanel, style=wx.SB_VERTICAL)
        labelLog = wx.StaticText(parent=basePanel, label="Log:")
        self.textboxLog = wx.TextCtrl(parent=basePanel, style=wx.TE_READONLY | wx.TE_MULTILINE)
        labelSave = wx.StaticText(parent=basePanel, label="Save merged image:")
        self.pickerctrlTargetFile = wx.FilePickerCtrl(parent=basePanel, style=wx.FLP_USE_TEXTCTRL | wx.FLP_SAVE | wx.FLP_OVERWRITE_PROMPT, message="Please select the path and filename you want to write the merged image to.", wildcard="Portable Network Graphics (PNG) files (*.png)|*.png")
        self.buttonSave = wx.Button(parent=basePanel, label="Save")
        
        # set up all the sizers for the upper box
        upperSizer = wx.StaticBoxSizer(upperBox, wx.HORIZONTAL)
        generationSizer = wx.GridBagSizer(5, 20)
        generationSizer.AddGrowableCol(1)
        generationSizer.Add(labelSourceDir, pos=(0, 0), flag=wx.ALIGN_LEFT | wx.TOP, border=3)
        generationSizer.Add(self.pickerctrlSourceDir, pos=(0, 1), flag=wx.EXPAND)
        generationSizer.Add(labelTimeframe, pos=(1, 0), flag=wx.ALIGN_LEFT | wx.TOP, border=3)
        generationSizer.Add(self.spinTimeframe, pos=(1, 1), flag=wx.ALIGN_LEFT)
        generationSizer.Add(self.buttonProcess, pos=(2, 0), flag=wx.EXPAND)
        generationSizer.Add(self.gaugeProgress, pos=(2, 1), flag=wx.EXPAND)
        upperSizer.Add(generationSizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        
        # set up all the sizers for the lower box
        lowerSizer = wx.StaticBoxSizer(lowerBox, wx.VERTICAL)
        lowerSizer.Add(labelClusters, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        lowerSizer.Add(self.listClusters, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
        lowerSizer.Add(labelPreview, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        previewSizer = wx.BoxSizer(wx.HORIZONTAL)
        previewSizer.Add(self.imagePreview, proportion=0, flag=wx.EXPAND)
        previewSizer.Add(self.scrollPreview, proportion=0, flag=wx.EXPAND | wx.LEFT, border=10)
        lowerSizer.Add(previewSizer, proportion=5, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
        lowerSizer.Add(labelLog, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        lowerSizer.Add(self.textboxLog, proportion=2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
        lowerSizer.Add(labelSave, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        saveLineSizer = wx.BoxSizer(wx.HORIZONTAL)
        saveLineSizer.Add(self.pickerctrlTargetFile, proportion=1, flag=wx.EXPAND)
        saveLineSizer.Add(self.buttonSave, proportion=0, flag=wx.EXPAND | wx.LEFT, border=10)
        lowerSizer.Add(saveLineSizer, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)

        # set up the main sizer (separating the two static boxes)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(upperSizer, proportion=0, flag=wx.EXPAND)
        sizer.Add((1, 10), proportion=0, flag=wx.EXPAND)
        sizer.Add(lowerSizer, proportion=1, flag=wx.EXPAND)
        
        # set up the border size and initialise the sizers
        border = wx.BoxSizer()
        border.Add(sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=10) 
        basePanel.SetSizer(border)
        basePanel.SetAutoLayout(1)
        border.Fit(self)
        
        # set initial configuration
        self.onClusterSelect(None)
        self.SetStatusText("Ready.")

        # bind events
        self.listClusters.Bind(wx.EVT_LISTBOX, self.onClusterSelect)
        self.buttonProcess.Bind(wx.EVT_BUTTON, self.onButtonProcessAbortClick)
        self.imagePreview.Bind(wx.EVT_SIZE, self.updatePreviewDetail)
        self.imagePreview.Bind(wx.EVT_PAINT, self.onImageRedraw)
        self.scrollPreview.Bind(wx.EVT_SCROLL, self.updatePreviewDetail)
        self.buttonSave.Bind(wx.EVT_BUTTON, self.saveMergedImage)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # show the window
        self.Centre()
        self.Show(True)                  # show the window
        
        # read the Alleg path from the registry and fill the file/dir pickers with it
        allegPath = self.getAllegArtPathFromRegistry()
        if(allegPath):
            self.pickerctrlSourceDir.SetPath(allegPath)
            self.pickerctrlTargetFile.SetPath(allegPath + "\\result.png")
        else:
            wx.MessageDialog(self,
                          message="Couldn't determine the path to Alleg's \"artwork\" directory from the registry! Please set it manually.",
                          caption="Warning",
                          style=wx.OK | wx.ICON_WARNING).ShowModal()
    
    
    
    def doProcess(self):
        sourcePath = self.pickerctrlSourceDir.GetPath()
        
        # make sure a valid directory has been selected
        if(not os.path.isdir(sourcePath)):
            wx.MessageDialog(self,
                          message="The given source path is not a directory!",
                          caption="Error",
                          style=wx.OK | wx.ICON_ERROR).ShowModal()
            return
        
        # show a warning if there are a lot of bitmap files
        numFiles = len(filter(lambda x: x[-4:]==".bmp", os.listdir(sourcePath)))
        if(numFiles > MainWindow.FILES_TO_PARSE_WARNING_THRESHOLD):
            if(wx.MessageDialog(self,
                          message="There are %i bitmap files in the directory you selected, parsing all those might take a while and consume quite some memory. Are you sure you want to proceed?" % (numFiles),
                          caption="Warning",
                          style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION).ShowModal() != wx.ID_YES):
                return
            
        # clear the cluster list and trigger all other UI items to be reset
        self.isProcessing = True
        self.listClusters.Clear()
        self.onClusterSelect(None)
        self.setGUIState()
        self.SetStatusText("Screenshots are now being processed. Please wait...")
        
        # start the actual processing in a background thread
        #self.processingFinishedEvent = threading.Event()
        self.statsMerger = StatsMerger(self.pickerctrlSourceDir.GetPath(),
                         self.spinTimeframe.GetValue(),
                         lambda x: self.gaugeProgress.SetRange(x),
                         lambda x: self.gaugeProgress.SetValue(x))

        thread.start_new_thread(self.processAndUpdateGui, ())


    
    def processAndUpdateGui(self):
        self.statsMerger.process()
        self.isProcessing = False
        self.results = self.statsMerger.getResults()
        self.results.reverse()
        for cluster in self.results:
            self.listClusters.Append(cluster.getTitle())
        self.setGUIState()
        if(self.statsMerger.abortProcessing):
            self.SetStatusText("Screenshot processing aborted, listing only those clusters already processed successfully.")
        else:
            self.SetStatusText("Screenshot processing complete.")


    
    def doAbortProcessing(self):
        self.statsMerger.triggerAbort()
        #self.gaugeProgress.Pulse()



    def doExit(self, event):
        self.Close()


        
    def doShowCredits(self, event):
        AboutWindow(self).Show(True)
    
    
    
    def setGUIState(self):
        #self.buttonProcess.Enable(not isProcessing)
        if(self.isProcessing):
            self.buttonProcess.SetLabel("Abort processing")
        else:
            self.buttonProcess.SetLabel("Process")
        self.listClusters.Enable(not self.isProcessing)
        self.textboxLog.Enable(not self.isProcessing)
        self.buttonSave.Enable(not self.isProcessing)
        
        
    
    def onButtonProcessAbortClick(self, event):
        if(self.isProcessing):
            self.doAbortProcessing()
        else:
            self.doProcess()


        
    def setNewPreviewImage(self, image):
        self.currentPreviewImage = image
        if(image):
            thumbSize = self.scrollPreview.GetSizeTuple()[1]
            self.scrollPreview.SetScrollbar(0, thumbSize, image.size[1], thumbSize);
            self.scrollPreview.Enable(True)
        else:
            self.scrollPreview.Enable(False)
        self.updatePreviewDetail(None)



    def redrawPreviewImage(self, dc):
        if(self.currentPreviewImage):
            pos = self.scrollPreview.GetThumbPosition()
            thumbSize = self.scrollPreview.GetSizeTuple()[1]
            box = (0, pos, self.currentPreviewImage.size[0], pos + thumbSize)
            croppedImage = self.currentPreviewImage.crop(box)
            
            wxIm = self.pilToImage(croppedImage)
            dc.DrawBitmap(wxIm, 0, 0, False)
            #self.imagePreview.SetBitmap(wxIm)
        else:
            imagePreviewSize = self.imagePreview.GetSizeTuple()
            backColor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU)    # SYS_COLOUR_WINDOW seems to give the wrong colour, at least not the one I was expecting
            emptyImage = wx.EmptyImage(imagePreviewSize[0], imagePreviewSize[1])
            emptyImage.SetRGBRect((0, 0, imagePreviewSize[0], imagePreviewSize[1]), backColor[0], backColor[1], backColor[2])
            emptyBitmap = emptyImage.ConvertToBitmap()
            dc.DrawBitmap(emptyBitmap, 0, 0, False)
            #self.imagePreview.SetBitmap(emptyBitmap)
            #self.imagePreview.SetBitmap(wx.EmptyBitmap(imagePreviewSize[0], imagePreviewSize[1]))
            #self.imagePreview.SetBitmap(wx.NullBitmap)



    def updatePreviewDetail(self, event):
        clientDC = wx.ClientDC(self.imagePreview)
        self.redrawPreviewImage(clientDC)



    def onImageRedraw(self, event):
        paintDC = wx.PaintDC(self.imagePreview)
        self.redrawPreviewImage(paintDC)
        

    
    def onClusterSelect(self, event):
        self.textboxLog.SetValue("")

        selections = self.listClusters.GetSelections()
        if(len(selections) > 0):
            selection = selections[0]
            cluster = self.results[selection]
            self.textboxLog.SetValue("\n".join(cluster.messages))
            if(cluster.mergedImage):
                self.setNewPreviewImage(cluster.mergedImage)
                self.pickerctrlTargetFile.SetPath(os.path.join(self.pickerctrlSourceDir.GetPath(), cluster.getFilenameSuggestion()))
                self.buttonSave.Enable(True)
                return

        # if we get here, there's no valid image to show
        self.setNewPreviewImage(None)
        self.pickerctrlTargetFile.SetPath("")
        self.buttonSave.Enable(False)
        
        
    
    def getAllegArtPathFromRegistry(self):
        try:
            import _winreg
            key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, settings.allegPathRegistryKey)
            (value, type) = _winreg.QueryValueEx(key, settings.allegPathRegistryValue)
            if(type == _winreg.REG_SZ):
                return(value)
            else:
                return(None)
        except:
            return(None)



    def saveMergedImage(self, event):
        selections = self.listClusters.GetSelections()
        if(len(selections) > 0):
            cluster = self.results[selections[0]]
            targetPath = self.pickerctrlTargetFile.GetPath()
            if(targetPath[-4:] != ".png"):
                wx.MessageDialog(self,
                              message="Couldn't save file. This application forces you to use png as the output format.",
                              caption="Invalid image format",
                              style=wx.OK | wx.ICON_ERROR).ShowModal()
            else:
                try:
                    cluster.mergedImage.save(targetPath)
                    self.SetStatusText("Merged image successfully saved to %s" % (targetPath))
                except IOError, exc:
                    wx.MessageDialog(self,
                                  message="Couldn't save file. The reported problem was: '%s'" % (exc.strerror),
                                  caption="Error",
                                  style=wx.OK | wx.ICON_ERROR).ShowModal()

                    
                    
    def onClose(self, event):
        if(self.isProcessing and event.CanVeto()):
            event.Veto()
            wx.MessageDialog(self,
                          message="Screenshots are currently being processed. Please wait for the processing to complete or abort it before closing the application.",
                          caption="Application can't be closed",
                          style=wx.OK | wx.ICON_HAND).ShowModal()
        else:
            self.Destroy()



    def pilToImage(self, pil):
        image = wx.BitmapFromBuffer(pil.size[0], pil.size[1], pil.convert('RGB').tostring())
        return image
