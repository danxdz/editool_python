import os
import wx
from topsolid_api import TopSolidAPI

api = TopSolidAPI()

# Inicializa a aplicação wx
app = wx.App(False)

# Cria um diálogo para selecionar diretórios
dialog = wx.DirDialog(None, "Selecione a Pasta Contendo os Arquivos .TopPkg", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

path = ""
if dialog.ShowModal() == wx.ID_OK:
    path = dialog.GetPath()
dialog.Destroy()

# Verifica se um caminho foi selecionado
if path:
    # Lista todos os arquivos no diretório com a extensão .TopPkg
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.TopPkg')]

    for f in files:
        print(f)
        api.ts.Pdm.ImportPackageAsDistinctCopy (f,True,True)
else:
    print("Nenhuma pasta foi selecionada.")