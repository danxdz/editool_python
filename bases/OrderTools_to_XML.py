import pandas as pd
import xml.etree.ElementTree as ET
from unidecode import unidecode
import re

# Classe Tool para representar cada ferramenta
class Tool:
    def __init__(self, data):
        self.data = data

# Carrega o arquivo Excel
df = pd.read_excel('./1.xlsx', skiprows=[0])

# Remove acentos dos cabeçalhos e substitui caracteres especiais por "_"
df.columns = [re.sub(r'[^a-zA-Z0-9_]', '_', unidecode(str(column))) for column in df.columns]

# Lista para armazenar as ferramentas
tools = []

# Itera sobre as linhas do DataFrame
for index, row in df.iterrows():
    # Remove as colunas não utilizadas (colunas com nome 'Unnamed:')
    data = {k: v for k, v in row.items() if not str(k).startswith('Unnamed')}
    
    # Converte valores float e inteiros para string
    for key, value in data.items():
        if isinstance(value, (float, int)):
            data[key] = str(value)
    
    # Cria um objeto Tool com os dados da linha
    tool = Tool(data)
    
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
tree.write('1.xml', encoding='utf-8', xml_declaration=True)
