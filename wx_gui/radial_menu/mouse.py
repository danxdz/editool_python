import uiautomation as auto

from uiautomation import InvokePattern

import win32gui
import win32con

def find_topsolid_window():
    """Trouve la fenêtre TopSolid."""
    all_windows = auto.GetRootControl().GetChildren()
    for win in all_windows:
        if "TopSolid" in win.Name:
            return win
    return None


def click_toolstrip_button():
    """Clique sur le second bouton dans le contrôle 'toolStripRibbonControl'."""
    window = find_topsolid_window()
    if window:
        print(f"Fenêtre trouvée : {window.Name}")
        
        # Recherche du contrôle principal "toolStripContainer"
        tool_strip_container = window.Control(searchDepth=20, AutomationId="toolStripContainer")
        if tool_strip_container.Exists():
            print(f"Contrôle trouvé : {tool_strip_container.AutomationId}")
            
            # Recherche du contrôle "toolStripRibbonControl"
            tool_strip_ribbon = tool_strip_container.Control(searchDepth=1, AutomationId="toolStripRibbonControl")
            if tool_strip_ribbon.Exists():
                print(f"Contrôle trouvé : {tool_strip_ribbon.AutomationId}")
                
                # Récupérer tous les boutons enfants
                buttons = [child for child in tool_strip_ribbon.GetChildren() if child.ControlTypeName == "ButtonControl"]
                print(f"Nombre de boutons trouvés : {len(buttons)}")
                debug_buttons(buttons)

                # Vérifier et cliquer sur le deuxième bouton
                if len(buttons) >= 2:  # Vérifie qu'il y a au moins 2 boutons

                    second_button = buttons[1]  # Index 1 = deuxième bouton
                    debug_control_patterns(second_button)
                    print(f"Clique sur le bouton : {second_button.Name}")
                    click_button_with_win32(second_button)
                    #second_button.Click()  # Actionne directement le bouton
                else:
                    print("Moins de deux boutons trouvés dans 'toolStripRibbonControl'.")
            else:
                print("Contrôle 'toolStripRibbonControl' non trouvé.")
        else:
            print("Contrôle 'toolStripContainer' non trouvé.")
    else:
        print("Fenêtre TopSolid non trouvée.")



def click_button_with_win32(button):
    """Simule un clic sur le bouton avec Win32 API."""
    hwnd = button.NativeWindowHandle
    if hwnd:
        win32gui.SendMessage(hwnd, win32con.BM_CLICK, 0, 0)  # Envoie un message de clic
        print(f"Bouton '{button.Name}' cliqué avec Win32 API.")
    else:
        print(f"Impossible de récupérer le HWND pour le bouton '{button.Name}'.")



def debug_buttons(buttons):
    """Affiche les informations sur les boutons trouvés."""
    for i, button in enumerate(buttons):
        print(f"Index {i}: Name: {button.Name}, AutomationId: {button.AutomationId}")

def debug_control_patterns(control):
    """Affiche les patterns supportés par un contrôle."""
    print(f"Name: {control.Name}, AutomationId: {control.AutomationId}")
    print(f"ControlTypeName: {control.ControlTypeName}")
    print(f"Patterns disponibles : {control.GetTogglePattern()}")

if __name__ == "__main__":
    click_toolstrip_button()
