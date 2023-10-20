import xml.etree.ElementTree as ET
import sqlite3
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Abre a janela de diálogo para selecionar o arquivo XML
Tk().withdraw()
xml_file_path = askopenfilename(title='Selecione um arquivo XML', filetypes=[('XML Files', '*.xml')])

if not xml_file_path:
    print('Nenhum arquivo selecionado.')
    exit()

# Faz o parsing do arquivo XML
tree = ET.parse(xml_file_path)
root = tree.getroot()

# Obtém os dados da ferramenta
tool = root.find('.//tool')
tool_data = {
    'Name': tool.attrib['name'],  # Adicione essa linha para obter o atributo 'name' do XML
    'Type': tool.attrib['type'],
    'GroupeMat': tool.find('param[@name="cuttingMaterial"]').attrib['value'],
    'D1': float(tool.find('param[@name="toolDiameter"]').attrib['value']),
    'D2': float(tool.find('param[@name="toolShaftDiameter"]').attrib['value'])-0.2,
    'D3': float(tool.find('param[@name="toolShaftDiameter"]').attrib['value']),
    'L1': float(tool.find('param[@name="cuttingLength"]').attrib['value']),
    'L2': float(tool.find('param[@name="taperHeight"]').attrib['value']),
    'L3': float(tool.find('param[@name="toolTotalLength"]').attrib['value']),
    'NoTT': int(tool.find('param[@name="cuttingEdges"]').attrib['value']),
    'RayonBout': float(tool.find('param[@name="cornerRadius"]').attrib['value']),
    'Chanfrein': tool.find('param[@name="toolShaftChamferAbsPos"]').attrib['value'],
    'CoupeCentre': "no", #tool.find('param[@name="cuttingDirection"]').attrib['value'],
    'ArrCentre': "no",#tool.find('param[@name="ArrCentre"]').attrib['value'],
    'TypeTar': "",#tool.find('param[@name="TypeTar"]').attrib['value'],
    'PasTar': "",#tool.find('param[@name="PasTar"]').attrib['value'],
    'Manuf': tool.find('param[@name="manufacturer"]').attrib['value'],
    'ManufRef': tool.find('param[@name="orderingCode"]').attrib['value'],
    'ManufRefSec': tool.find('param[@name="comment"]').attrib['value'],
    'Code': " ",
    'CodeBar': tool.find('param[@name="orderingCode"]').attrib['value'],
    'Comment': tool.find('param[@name="comment"]').attrib['value'],

}

# Conecta ao banco de dados (ou cria um novo se não existir)
conn = sqlite3.connect('tool_manager.db')

# Cria um cursor para executar comandos SQL
cursor = conn.cursor()

# Cria a tabela 'tools' com os atributos desejados (caso ainda não exista)
cursor.execute('''
   CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Type TEXT,
            GroupeMat INT,
            D1 REAL,
            D2 REAL,
            D3 REAL,
            L1 REAL,
            L2 REAL,
            L3 REAL,
            NoTT INTEGER,
            RayonBout REAL,
            Chanfrein REAL,
            CoupeCentre TEXT,
            ArrCentre TEXT,
            TypeTar TEXT,
            PasTar REAL,
            Manuf TEXT,
            ManufRef TEXT,
            ManufRefSec TEXT,
            Code TEXT,
            CodeBar TEXT,
            Comment TEXT
        )
''')

# Insere a ferramenta na tabela 'tools'
cursor.execute('''
    INSERT INTO tools (Name, Type, GroupeMat, D1, D2, D3, L1, L2, L3, NoTT, RayonBout, Chanfrein, CoupeCentre,
        ArrCentre, TypeTar, PasTar, Manuf, ManufRef, ManufRefSec, Code, CodeBar,Comment)
    VALUES (:Name, :Type, :GroupeMat, :D1, :D2, :D3, :L1, :L2, :L3, :NoTT, :RayonBout, :Chanfrein, :CoupeCentre,
        :ArrCentre, :TypeTar, :PasTar, :Manuf, :ManufRef, :ManufRefSec, :Code, :CodeBar, :Comment)
''', tool_data)

# Confirma a transação
conn.commit()

# Fecha a conexão
conn.close()

print('Ferramenta adicionada ao banco de dados.')
