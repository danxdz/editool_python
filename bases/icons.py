import tkinter as tk
from tkinter import ttk
import win32gui
import win32con
import win32api


def find_topsolid_window():
    """Procura uma janela cujo título contenha 'TopSolid'."""
    found_window = None

    def callback(hwnd, _):
        nonlocal found_window
        if "TopSolid 7" in win32gui.GetWindowText(hwnd):
            found_window = hwnd
            return False  # Para de procurar após encontrar
        return True

    win32gui.EnumWindows(callback, None)
    return found_window


def enum_controls(hwnd):
    """Enumera os controles (filhos) de uma janela."""
    controls = []

    def callback(child_hwnd, _):
        class_name = win32gui.GetClassName(child_hwnd)
        window_text = win32gui.GetWindowText(child_hwnd)
        controls.append((child_hwnd, class_name, window_text))
        return True

    win32gui.EnumChildWindows(hwnd, callback, None)
    return controls


def update_controls():
    """Atualiza a lista de controles da aplicação TopSolid."""
    hwnd = find_topsolid_window()
    if hwnd:
        window_title = win32gui.GetWindowText(hwnd)
        controls = enum_controls(hwnd)

        # Atualiza a lista na combobox
        control_list.clear()
        for ctrl in controls:
            handle, class_name, text = ctrl
            description = f"{class_name} - {text} (HWND: {handle})"
            control_list.append((description, handle))
        dropdown['values'] = [desc for desc, _ in control_list]

        # Atualiza o label com o título da janela ativa
        active_window_label.config(text=f"Janela encontrada: {window_title}")
        if controls:
            dropdown.current(0)  # Seleciona o primeiro item
        else:
            dropdown.set("Nenhum controle encontrado.")
    else:
        active_window_label.config(text="Nenhuma janela 'TopSolid' encontrada.")
        dropdown.set("")


def click_handle(hwnd):
    """Simula um clique no controle identificado pelo hwnd."""
    try:
        # Obtém a posição do controle
        rect = win32gui.GetWindowRect(hwnd)
        x = (rect[0] + rect[2]) // 2  # Centro no eixo X
        y = (rect[1] + rect[3]) // 2  # Centro no eixo Y

        # Move o cursor para o controle e simula o clique
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    except Exception as e:
        result_label.config(text=f"Erro ao clicar no controle: {e}")


def execute_control():
    """Executa o controle selecionado."""
    if not control_list:
        result_label.config(text="Nenhum controle disponível para executar.")
        return

    selection = dropdown.current()
    if selection == -1:
        result_label.config(text="Selecione um controle para executar.")
        return

    _, handle = control_list[selection]

    # Simula um clique no controle selecionado
    try:
        # Primeiro tenta com BM_CLICK
        result_label.config(text=f"Tentando clicar no controle HWND: {handle}")
        win32gui.SendMessage(handle, win32con.BM_CLICK, 0, 0)
        result_label.config(text=f"Controle executado com sucesso: HWND {handle}")
    except Exception as e:
        # Caso BM_CLICK falhe, tenta usar a função de clique
        result_label.config(text=f"BM_CLICK falhou, tentando com click_handle: {e}")
        click_handle(handle)


# Inicializa a aplicação tkinter
app = tk.Tk()
app.title("Controles")
app.geometry("500x300")

# Lista de controles e elementos da UI
control_list = []
active_window_label = tk.Label(app, text="Janela ativa: Nenhuma", anchor="w")
active_window_label.pack(fill="x", pady=5)

# Combobox para listar os controles
dropdown_label = tk.Label(app, text="Controles:")
dropdown_label.pack(anchor="w", padx=10)

dropdown = ttk.Combobox(app, state="readonly", width=80)
dropdown.pack(fill="x", padx=10, pady=5)

# Botão para atualizar os controles
update_button = tk.Button(app, text="Atualizar", command=update_controls)
update_button.pack(side="left", padx=10, pady=10)

# Botão para executar o controle selecionado
execute_button = tk.Button(app, text="Executar", command=execute_control)
execute_button.pack(side="left", padx=10, pady=10)

# Label para mostrar resultados
result_label = tk.Label(app, text="", anchor="w", fg="blue")
result_label.pack(fill="x", padx=10, pady=10)

# Inicia o loop principal
app.mainloop()
