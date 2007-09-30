#===============================================================================
# Example menu structure:
# =======================
# 
# menuBarStructure = [
#        (
#            "File",
#            "",
#            (
#                 ("&Generate", "Parse all screenshots, try to find clusters and merge them if possible", self.doGenerate),
#                 None,
#                 ("E&xit", "Close the application", self.doExit),
#                 [
#                      ("Submenu",
#                       "",
#                       (
#                            ("Test", "Test item", None),
#                       ),
#                      )
#                 ]
#            ),
#        ),
#        (
#            "Help",
#            "",
#            (
#                 ("&About", "Show the credits", self.doShowCredits),
#            ),
#        ),
#    ]
#===============================================================================

import types
import wx



class MenuStructureInvalidError(Exception):
    pass



def createMenu(frame, rawMenu):
    menuList = []
    
    for rawItem in rawMenu:
        (menuHeading, menuHelp, menuEntries) = rawItem
        newMenu = wx.Menu()
    
        for menuEntry in menuEntries:
            if type(menuEntry) == types.NoneType:
                newMenu.AppendSeparator()
            elif type(menuEntry) == types.ListType:
                for submenu in createMenu(frame, menuEntry):
                    (submenuCaption, submenuHelp, submenu) = submenu
                    newMenu.AppendSubMenu(submenu, text=submenuCaption, help=submenuHelp)
            elif type(menuEntry) == types.TupleType:
                (caption, help, eventHandler) = menuEntry
                newMenuItem = wx.MenuItem(newMenu, id=wx.ID_ANY, text=caption, help=help)
                frame.Bind(wx.EVT_MENU, eventHandler, id=newMenuItem.GetId())
                newMenu.AppendItem(newMenuItem)
            else:
                raise MenuStructureInvalidError("Unexpected data type in menu structure")
                
        menuList.append((menuHeading, menuHelp, newMenu))
    
    return(menuList)



def createMenuBar(frame, rawMenuStructure):
    menuBar = wx.MenuBar()
    for submenu in createMenu(frame, rawMenuStructure):
        (menuCaption, menuHelp, menuEntries) = submenu
        menuBar.Append(menuEntries, menuCaption)
    return(menuBar)
