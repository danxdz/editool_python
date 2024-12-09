import uiautomation as auto

def find_topsolid_window():
    """Trouve la fenêtre TopSolid, peu importe le titre exact."""
    all_windows = auto.GetRootControl().GetChildren()
    for win in all_windows:
        if "TopSolid" in win.Name:
            return win
    return None


def click_toolstrip():
    """Essaye de cliquer sur le contrôle 'toolStripRibbonControl'."""
    window = find_topsolid_window()
    if window:
        print(f"Fenêtre trouvée : {window.Name}")
        
        # Parcourt les enfants pour rechercher le contrôle
        for child in window.GetChildren():
            print(f"Contrôle trouvé : Name={child.Name}, ControlType={child.ControlTypeName}")
            
            # Remplacez ici par un critère adapté (Name ou autre)
            if "toolStripRibbonControl" in child.Name:
                child.Click()
                print("Clic simulé sur le contrôle.")
                return
        
        print("Contrôle 'toolStripRibbonControl' non trouvé.")
    else:
        print("Fenêtre TopSolid non trouvée.")


def list_all_children(control, depth=0):
    """Affiche tous les enfants récursivement."""
    indent = "  " * depth
    for child in control.GetChildren():
        print(f"{indent}Name: {child.Name}, Type: {child.ControlTypeName}, AutomationId: {child.AutomationId}")
        list_all_children(child, depth + 1)

def debug_toolstrip():
    """Affiche tous les enfants de la fenêtre TopSolid pour déboguer."""
    window = find_topsolid_window()
    if window:
        print(f"Fenêtre trouvée : {window.Name}")
        list_all_children(window)
    else:
        print("Fenêtre TopSolid non trouvée.")


if __name__ == "__main__":
    debug_toolstrip()
