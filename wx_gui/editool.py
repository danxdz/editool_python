import wx

#add lib to create log file
import logging


#import gui
from ToolManagerUi import ToolManagerUI


if __name__ == "__main__":
    #create log file and delete the previous one
    open('editool.log', 'w').close()
    
    logging.basicConfig(
        filename='editool.log', 
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)-2s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    
    logging.info('Starting ediTool')
    
    app = wx.App()
    frame = ToolManagerUI(None, wx.ID_ANY, title='ediTool')
    frame.Show()
    app.MainLoop()