import wx
import math
import threading
import os
import time 
import logging

import win32api
import win32con

import pygetwindow as gw  

from pynput import mouse
from pynput.keyboard import Key, Controller

from topsolid_api import TopSolidAPI 


class ConfigFile:
    def __init__(self):
        self.config = {}
        self.read_config()
        

    def create_config(self):
        with open('wx_gui\\config.txt', 'w') as file:
            file.write(
                'mouse_button;Button.x1;Mouse button to open the radial menu\n'
                'menu_1;test_connection;Test connection to TopSolid\n'
                'menu_2;get_current_project;Get Current Project\n'
                'menu_3;get_constituents;Get Constituents of Current Project\n'
                'menu_4;start_modification;Start Modification\n'
                'menu_5;end_modification;End Modification\n'
                'menu_6;open_file;Open File\n'
                'menu_7;check_in_all_files;Check In All Files\n'
                'menu_8;export_all_pdfs;Export all to pdfs\n'
            )
    
    def read_config(self):
        with open('wx_gui\\config.txt', 'r') as file:
            for line in file:
                key, value, toolTip = line.strip().split(';')
                self.config[key] = [value, toolTip]
    
    def get_config(self, key):
        return self.config.get(key)

    def write_config(self):
        with open('wx_gui\\config.txt', 'w') as file:
            for key, (value, tooltip) in self.config.items():
                file.write(f'{key};{value};{tooltip}\n')

# ShortcutTextCtrl class to capture key combinations
class ShortcutTextCtrl(wx.TextCtrl):
    def __init__(self, parent, value=''):
        super().__init__(parent, value=value, style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_CHAR, self.on_char)
        self.shortcut = value

    def on_key_down(self, event):
        keycode = event.GetKeyCode()
        modifiers = []
        if event.ControlDown():
            modifiers.append('CTRL')
        if event.AltDown():
            modifiers.append('ALT')
        if event.ShiftDown():
            modifiers.append('SHIFT')
        key = self.get_key_name(keycode)
        if key:
            shortcut = '+'.join(modifiers + [key]) if modifiers else key
            self.SetValue(shortcut)
            self.shortcut = shortcut
        else:
            event.Skip()

    def get_key_name(self, keycode):
        # Handle ASCII characters
        if 32 <= keycode <= 126:
            return chr(keycode)
        # Handle function keys
        elif wx.WXK_F1 <= keycode <= wx.WXK_F24:
            return f'F{keycode - wx.WXK_F1 + 1}'
        # Handle numpad digits
        elif wx.WXK_NUMPAD0 <= keycode <= wx.WXK_NUMPAD9:
            return f'NUMPAD{keycode - wx.WXK_NUMPAD0}'
        # Handle special keys
        key_dict = {
            wx.WXK_BACK: 'BACK',
            wx.WXK_TAB: 'TAB',
            wx.WXK_RETURN: 'RETURN',
            wx.WXK_ESCAPE: 'ESCAPE',
            wx.WXK_SPACE: 'SPACE',
            wx.WXK_DELETE: 'DELETE',
            wx.WXK_LEFT: 'LEFT',
            wx.WXK_RIGHT: 'RIGHT',
            wx.WXK_UP: 'UP',
            wx.WXK_DOWN: 'DOWN',
            wx.WXK_HOME: 'HOME',
            wx.WXK_END: 'END',
            wx.WXK_PAGEUP: 'PAGEUP',
            wx.WXK_PAGEDOWN: 'PAGEDOWN',
            wx.WXK_INSERT: 'INSERT',
            wx.WXK_PRINT: 'PRINT',
            wx.WXK_PAUSE: 'PAUSE',
            wx.WXK_NUMLOCK: 'NUMLOCK',
            wx.WXK_SCROLL: 'SCROLLLOCK',
            wx.WXK_CAPITAL: 'CAPSLOCK',
        }
        return key_dict.get(keycode, None)

    def on_char(self, event):
        pass  # Prevent character input

# ConfigFrame class for the configuration window
class ConfigFrame(wx.Frame):
    def __init__(self, parent, config):
        super().__init__(parent, title='Setup', size=(450, 450))
        self.config = config
        self.parent = parent
        
        self.init_ui()
        self.Centre()
        self.Show()

    def init_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.controls = {}

        for key, (value, tooltip) in self.config.config.items():
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(panel, label=key)
            if 'mouse_button' in key:
                ctrl = wx.TextCtrl(panel, value=value)
            elif 'menu_' in key:
                ctrl = ShortcutTextCtrl(panel, value=value)
            else:
                ctrl = wx.TextCtrl(panel, value=value)
            tooltip = wx.TextCtrl(panel, value=tooltip)    
            self.controls[key] = ctrl, tooltip
            hbox.Add(label, flag=wx.RIGHT, border=8)
            hbox.Add(ctrl, proportion=1, flag=wx.EXPAND)
            hbox.Add(tooltip, proportion=1, flag=wx.EXPAND)
            sizer.Add(hbox, flag=wx.EXPAND|wx.ALL, border=5)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        save_btn = wx.Button(panel, label='Save')
        save_btn.Fit()

        cancel_btn = wx.Button(panel, label='Close')
        cancel_btn.Fit()

        btn_sizer.Add(save_btn, proportion=0, flag=wx.ALL, border=10)
        btn_sizer.Add(cancel_btn, proportion=0, flag=wx.ALL, border=10)

        sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        panel.SetSizerAndFit(sizer)
        panel.Layout()


        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)

    def on_save(self, event):
        for key, ctrl in self.controls.items():
            value = ctrl[0].GetValue()
            tt = ctrl[1].GetValue()
            tooltip = tt
            self.config.config[key] = [value, tooltip]
        self.config.write_config()
        self.parent.reload_config()
        self.Close()

    def on_cancel(self, event):
        self.Close()
    
    ''' example of config file
    mouse_button;Button.x1;Mouse button to open the radial menu
    menu_1;test_connection;Test connection to TopSolid
    menu_2;get_current_project;Get Current Project
    menu_3;get_constituents;Get Constituents of Current Project
    menu_4;start_modification;Start Modification
    menu_5;end_modification;End Modification
    menu_6;open_file;Open File
    menu_7;check_in_all_files;Check In All Files
    menu_8;export_all_pdfs;Export all to pdfs
    '''

class TransparentRadialMenu(wx.Frame):
    def __init__(self, parent, title):
        style = wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR | wx.NO_BORDER
        super().__init__(parent, title=title, size=(300, 300), style=style)

        self.ts = TopSolidAPI()

        self.icon_positions = []  # Stores the positions of the icons for hit testing
        
        self.localpath = os.path.dirname(os.path.abspath(__file__))


        # Load configuration from file
        self.config = ConfigFile()
        self.build_menu_items()

        # Load the TopSolid API
        #self.ts = TopSolidAPI()

        self.is_menu_visible = False  
        self.menu_center = (150, 150)  
        self.selected_icon = None  

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)        
        #self.Bind(wx.EVT_LEFT_UP, self.on_release)

        # Hide the window initially
        self.Hide()
        
    def build_menu_items(self):
        path = self.localpath      
        self.menu_items = [
            {"icon": path + "\\icons\\icon1.png", "action": self.config.get_config('menu_1')},
            {"icon": path + "\\icons\\icon2.png", "action": self.config.get_config('menu_2')},
            {"icon": path + "\\icons\\icon3.png", "action": self.config.get_config('menu_3')},
            {"icon": path + "\\icons\\icon4.png", "action": self.config.get_config('menu_4')},
            {"icon": path + "\\icons\\icon5.png", "action": self.config.get_config('menu_5')},
            {"icon": path + "\\icons\\icon6.png", "action": self.config.get_config('menu_6')},
            {"icon": path + "\\icons\\icon7.png", "action": self.config.get_config('menu_7')},
            {"icon": path + "\\icons\\icon8.png", "action": self.config.get_config('menu_8')},
        ]

    def on_quit(self, event):
        '''close the app'''
        self.ts.end_modif()
        self.ts.disconnect_topsolid()
        self.Close(True)

    def toggle_menu_visibility(self):
        if self.is_menu_visible:
            self.Hide()
            self.is_menu_visible = False
        else:
            self.Show()
            self.is_menu_visible = True
            self.Refresh()  # Redraw to display the menu

    def show_menu(self, position):
        self.menu_center = (150, 150)  # Center of the menu within the window
        if not self.is_menu_visible:
            self.is_menu_visible = True
            # Position the window at the cursor position
            window_x = position[0] - self.menu_center[0]
            window_y = position[1] - self.menu_center[1]
            self.SetPosition((window_x, window_y))
            self.Show()
            self.Refresh()

    def on_mouse_move(self, event):
        if not self.is_menu_visible:
            return

        x, y = event.GetPosition()
        self.selected_icon = None

        for icon_data in self.icon_positions:
            if icon_data["rect"].Contains(wx.Point(x, y)):
                self.selected_icon = icon_data
                tooltip_text = icon_data["tooltip"]
                if self.GetToolTipText() != tooltip_text:
                    self.SetToolTip(tooltip_text)
                break

        if not self.selected_icon:
            self.SetToolTip("")  # Remove the tooltip if not over any icon

    def on_paint(self, event):
        if not self.is_menu_visible:
            return
        dc = wx.PaintDC(self)
        dc.SetBrush(wx.Brush(wx.Colour(255, 255, 255, 0)))

        center_x, center_y = self.menu_center
        
        num_items = len(self.menu_items)
        self.icon_positions = [] 

        for i, item in enumerate(self.menu_items):
            angle = (2 * math.pi / num_items) * i

            try:
                icon = wx.Bitmap(item["icon"], wx.BITMAP_TYPE_PNG)
            except Exception as e:
                icon = wx.ArtProvider.GetBitmap(wx.ART_MISSING_IMAGE, wx.ART_OTHER, (32, 32))
                logging.error(f"Erro ao carregar ícone {item['icon']}: {e}")

            icon_width, icon_height = icon.GetWidth(), icon.GetHeight()

            # get size of the icon to calculate the radius
            icon_size = max(icon_width, icon_height)
            radius = icon_size*2

            # set the position of the icon
            x = int(center_x + radius * math.cos(angle))
            y = int(center_y + radius * math.sin(angle))

            x -= icon_width // 2
            y -= icon_height // 2

            dc.DrawBitmap(icon, x, y, True)

            # set the position of the icon and its tooltip
            icon_rect = wx.Rect(x, y, icon_width, icon_height)
            tooltip = item["action"][1]
            action = item["action"][0]
            self.icon_positions.append({
                "rect": icon_rect,
                "tooltip": tooltip,
                "action": action,
            })

            # optional: draw a hitbox
            #dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 1))
            #dc.DrawRectangle(icon_rect)

    def _on_release(self, event):
        if self.selected_icon:
            action = self.selected_icon["action"]
            #print("Debugging :: Ação:", action)

            if self.ts.connected:
                if hasattr(self, action):
                    getattr(self, action)()  # Call the associated method
                else:
                    # Assume action is a keyboard shortcut
                    self.simulate_key_combination(action)
            else:
                wx.MessageBox(
                    "Não conectado ao TopSolid", "Erro", wx.OK | wx.ICON_ERROR
                )

        self.toggle_menu_visibility()


    def on_click(self, event):
        if not self.is_menu_visible:
            return
        
        x, y = event.GetPosition()

        for icon_data in self.icon_positions:
            if icon_data["rect"].Contains(wx.Point(x, y)):
                action = icon_data["action"]
                ### print("Debugging :: ", action)
                
                self.toggle_menu_visibility()

                if self.ts.connected:
                    if hasattr(self, action):
                        getattr(self, action)()  # Call the associated method
                    else:
                        # Assume action is a keyboard shortcut
                        self.simulate_key_combination(action)
                else:
                    wx.MessageBox("Not connected to TopSolid", "Error", wx.OK | wx.ICON_ERROR)
                return

        self.toggle_menu_visibility()

    def simulate_key_combination(self, combination):
        self.set_active_window_title()
        keyboard = Controller()
        keys = combination.upper().split('+')
        key_map = {
            'CTRL': Key.ctrl,
            'ALT': Key.alt,
            'SHIFT': Key.shift,
            'ENTER': Key.enter,
            'BACKSPACE': Key.backspace,
            'TAB': Key.tab,
            'ESC': Key.esc,
            'UP': Key.up,
            'DOWN': Key.down,
            'LEFT': Key.left,
            'RIGHT': Key.right,
            # Add more mappings if needed
        }

        # Parse the keys
        modifiers = []
        normal_keys = []

        for k in keys:
            k = k.strip()
            if k in key_map:
                modifiers.append(key_map[k])
            elif len(k) == 1:
                normal_keys.append(k.lower())
            else:
                # Handle function keys
                if k.startswith('F') and k[1:].isdigit():
                    fn_number = int(k[1:])
                    if 1 <= fn_number <= 24:
                        normal_keys.append(getattr(Key, f'f{fn_number}'))
                else:
                    print(f"Unsupported key: {k}")
                    wx.MessageBox(f"Unsupported key: {k}", "Error", wx.OK | wx.ICON_ERROR)
                    return

        # Press modifiers
        for m in modifiers:
            keyboard.press(m)

        # Press normal keys
        for nk in normal_keys:
            keyboard.press(nk)
            keyboard.release(nk)

        # Release modifiers
        for m in reversed(modifiers):
            keyboard.release(m)

    # TopSolid API methods associated with the radial menu items

    def check_in_all_files(self):
        #get open files
        files = self.ts.get_open_files()

        lib_const = self.ts.get_constituents(None, True)
        self.ts.check_in_all(lib_const[1])
        wx.MessageBox(
            "Todos os arquivos registrados", "Sucesso", wx.OK | wx.ICON_INFORMATION
        )

    def export_all_pdfs(self):
        lib, name = self.ts.get_current_project()
        dlg = wx.DirDialog(
            self,
            "Escolha uma pasta para salvar os PDFs",
            style=wx.DD_DEFAULT_STYLE,
        )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if not os.path.exists(path):
                os.makedirs(path)
            self.ts.export_all_pdfs(path)
            wx.MessageBox(
                f"PDFs exportados para {path}",
                "Sucesso",
                wx.OK | wx.ICON_INFORMATION,
            )
        dlg.Destroy()

    def new_assembly(self):
        if self.ts.connected:
            print(self.ts.get_current_project())

    def import_files(self):
        self.ts.end_modif(True, False)
        # Adicione aqui a lógica para importar um arquivo
        dlg = wx.FileDialog(self, "Choose a file to import", wildcard="All files (*.*)|*.*", style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            file_path = dlg.GetPath()
            dlg.Destroy()

     
            # Lógica para obter o nome do novo documento
            # Neste exemplo, estou usando o nome do arquivo como o nome do documento.
            document_name = os.path.basename(file_path)


            #lib, name = self.topSolid.get_current_project()
            self.ts.get_current_project()

        try:
            # Chama o método import_documents
            imported_documents, log, bad_document_ids = self.ts.Import_file_w_conv(10, file_path, self.ts.current_project)
            
            # Examine os resultados conforme necessário
            if imported_documents:
                print(f"Documents imported successfully. Document IDs: {len(imported_documents)}", "Success", wx.OK | wx.ICON_INFORMATION)
                for doc in imported_documents:
                    print(len(doc), doc)
                    for d in doc:
                        print(d)
                        self.ts.check_in(d)
            else:
                wx.MessageBox(f"Error importing documents. Log: {log}. Bad Document IDs: {bad_document_ids}", "Error", wx.OK | wx.ICON_ERROR)

        except Exception as e:
            wx.MessageBox(f"Error importing documents: {e}", "Error", wx.OK | wx.ICON_ERROR)


    def close_active_file(self):
        file = self.ts.get_open_files()
        if file:
            for f in file:
                self.ts.close_file(f)
        else:
            wx.MessageBox(
                "Não conectado ao TopSolid", "Erro", wx.OK | wx.ICON_ERROR
            )

    def ask_plan(self):
        #get current open files
        files = self.ts.get_open_files()
        #get the first file
        file = files[0]
        #start modification
        self.ts.start_modif("plan", True)
        self.ts.isDirty(file)
        #ask for plan
        self.ts.ask_plan(file)
        #end modification
        self.ts.end_modif(False, False)


    
    def set_active_window_title(self):
        try:
            window = gw.getWindowsWithTitle('TopSolid' )[0]
            window.activate()
        except IndexError:
            wx.MessageBox("TopSolid window not found", "Error", wx.OK | wx.ICON_ERROR)

        

    def open_config_frame(self):
        ConfigFrame(self, self.config)

    def reload_config(self):
        self.config.read_config()
        self.build_menu_items()
        self.Refresh()

def get_active_window_title():
    """Fetches the title of the currently active window."""
    active_window = gw.getActiveWindow()
    if (active_window):
        return active_window.title
    return None


def start_pynput_listener(frame):
    config = ConfigFile()
    mouse_button = config.get_config('mouse_button')
    app = config.get_config('app')
      
    press_time = [0]


    def on_click(x, y, button, pressed):
                    
        title = get_active_window_title() 
        #print('title:', title)
        if  app[0] in title: 
                #print(f'button :: {button} mouse_button :: {mouse_button}')
                if str(button) == str(mouse_button[0]):
                    if pressed:
                        press_time[0] = time.time()
                    else:
                        duration = time.time() - press_time[0]
                        if duration >= 1:
                            wx.CallAfter(frame.open_config_frame)
                        else:
                            wx.CallAfter(frame.show_menu, (x, y))
                            

    listener = mouse.Listener(on_click=on_click)
    listener.start()


if __name__ == "__main__":
    app = wx.App()
    #create full screen frame
    frame = TransparentRadialMenu(None, title='Radial Menu')
    
    # Start the pynput listener in a separate thread
    threading.Thread(target=start_pynput_listener, args=(frame,), daemon=True).start()
    app.MainLoop()