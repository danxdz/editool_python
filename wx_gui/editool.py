import wx
import threading
import logging

from ToolManagerUi import ToolManagerUI
from radial_menu.round import TransparentRadialMenu, start_pynput_listener

if __name__ == "__main__":
    # Create or clear the log file
    open('editool.log', 'w').close()
    
    # Set up logging
    logging.basicConfig(
        filename='editool.log', 
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)-2s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logging.info('Starting ediTool')
    
    # Initialize the wxPython application
    app = wx.App()
    
    # Create the main application window
    main_frame = ToolManagerUI(None, title='ediTool')
    main_frame.Show()
    
    # Create the radial menu frame
    radial_menu_frame = TransparentRadialMenu(None, title='Radial Menu')
    
    # Start the pynput listener in a separate daemon thread
    threading.Thread(
        target=start_pynput_listener, 
        args=(radial_menu_frame,), 
        daemon=True
    ).start()
    
    # Start the application's main event loop
    app.MainLoop()


#make sure to close the log file and thread when the application is closed
logging.info('Closing ediTool')
logging.shutdown()
threading.Event().set()
threading.Event().clear()
threading.Event().wait()    