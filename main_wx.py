import wx

#import gui
from wx_gui.ToolManagerUi import ToolManagerUI



if __name__ == "__main__":
    print("Starting Tool Manager")
    app = wx.App()
    frame = ToolManagerUI()
    app.MainLoop()


