import pandas as pd
import xml.etree.ElementTree as ET
from unidecode import unidecode
import re
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Mapeamento dos nomes das colunas
column_mapping = {
    0: "column",
    1: "Type",
    2: "GroupeMat",
    3: "D1",
    4: "L1",
    5: "L2",
    6: "L3",
    7: "D3",
    8: "NoTT",
    9: "RayonBout",
    10: "Chanfrein",
    11: "CoupeCentre",
    12: "ArrCentre",
    13: "TypeTar",
    14: "PasTar",
    15: "Manuf",
    16: "ManufRef",
    17: "ManufRefSec",
    18: "Code",
    19: "CodeBar"
}

# Classe Tool para representar cada ferramenta
class Tool:
    def __init__(self, data):
        self.data = data

# Cria a janela principal
root = Tk()
root.withdraw()  # Esconde a janela principal

# Abre a caixa de diálogo para selecionar um arquivo
file_path = askopenfilename()

# Verifica se um arquivo foi selecionado
if file_path:
    print("Arquivo selecionado:", file_path)
    
    # Carrega o arquivo Excel
    df = pd.read_excel(file_path, skiprows=[0])

    # Remove acentos dos cabeçalhos e substitui caracteres especiais por "_"
    df.columns = [re.sub(r'[^a-zA-Z0-9_]', '_', unidecode(str(column))) for column in df.columns]

    # Lista para armazenar as ferramentas
    tools = []

    # Itera sobre as linhas do DataFrame
    for index, row in df.iterrows():
        # Cria um dicionário para armazenar os dados da ferramenta com os nomes de coluna desejados
        newTool = {}
        for x, value in enumerate(row):
            column_name = column_mapping.get(x)  # Obtém o nome da coluna mapeado
            
            if column_name:
                if column_name == "column":
                    newTool[column_name] = x
                elif pd.isnull(value):  # Verifica se o valor é NaN
                    newTool[column_name] = None
                elif isinstance(value, float):  # Converte valores float para inteiros
                    newTool[column_name] = int(value)
                else:
                    newTool[column_name] = value
        
        # Cria um objeto Tool com os dados da linha
        tool = Tool(newTool)
        
        # Adiciona a ferramenta à lista
        tools.append(tool)

    # Cria o elemento raiz do XML
    root = ET.Element('tools')

    # Itera sobre as ferramentas e cria os elementos XML correspondentes
    for tool in tools:
        tool_element = ET.SubElement(root, 'tool')
        
        # Adiciona os dados da ferramenta como subelementos
        for key, value in tool.data.items():
            # Codifica corretamente o valor para evitar erros de codificação
            encoded_value = str(value).encode('utf-8', 'xmlcharrefreplace').decode('utf-8')
            
            data_element = ET.SubElement(tool_element, key)
            data_element.text = encoded_value

    # Cria o objeto ElementTree com o elemento raiz
    tree = ET.ElementTree(root)

    # Salva o XML em um arquivo
    xml_file_path = file_path.replace('.xlsx', '.xml')  # Cria o caminho do arquivo XML
    tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
    
    print("Arquivo XML gerado:", xml_file_path)
else:
    print("Nenhum arquivo selecionado")
