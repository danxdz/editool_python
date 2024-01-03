import wx

#import gui
from ToolManagerUi import ToolManagerUI


if __name__ == "__main__":

    print("Starting ediTool - tools manager")

    app = wx.App()
    frame = ToolManagerUI(None, wx.ID_ANY, title='ediTool - tools manager')
    frame.Show()
    app.MainLoop()