import xml.etree.ElementTree as ET
import sqlite3
from tkinter import Tk
from tkinter.filedialog import askopenfilename

class Tool:
    def __init__(self):
        self.Id = ""
        self.Name = ""
        self.Type = ""
        self.D1 = 0.0
        self.D2 = 0.0
        self.D3 = 0.0
        self.L1 = 0.0
        self.L2 = 0.0
        self.L3 = 0.0
        self.CorRadius = 0.0
        self.CorChamfer = 0.0
        self.AngleColl = 0.0
        self.AnglePoint = 0.0
        self.AngleDeg = 0.0
        self.NoTT = 0
        self.GroupeMat = ""
        self.ToolMaterial = ""
        self.CoupeCentre = ""
        self.ArrCentre = ""
        self.TypeTar = ""
        self.PasTar = ""
        self.Manuf = ""
        self.ManufRef = ""
        self.ManufRefSec = ""
        self.Code = ""
        self.CodeBar = ""
        self.Comment = ""

def CreateToolTable():
    conn = sqlite3.connect('tools.db')
    c = conn.cursor()

    # Cria a tabela "tools" se ainda não existir
    c.execute('''CREATE TABLE IF NOT EXISTS tools (
                    Id TEXT,
                    Type TEXT,
                    D1 REAL,
                    D2 REAL,
                    D3 REAL,
                    L1 REAL,
                    L2 REAL,
                    L3 REAL,
                    CorRadius REAL,
                    CorChamfer REAL,
                    AngleColl REAL,
                    AnglePoint REAL,
                    NoTT INTEGER,
                    GroupeMat TEXT,
                    ToolMaterial TEXT,
                    CoupeCentre TEXT,
                    ArrCentre TEXT,
                    TypeTar TEXT,
                    PasTar TEXT,
                    Manuf TEXT,
                    ManufRef TEXT,
                    ManufRefSec TEXT,
                    Code TEXT,
                    CodeBar TEXT,
                    Comment TEXT
                )''')

    conn.commit()
    conn.close()

def InsertToolData(tool):
    conn = sqlite3.connect('tools.db')
    c = conn.cursor()

    # Insere os dados da ferramenta na tabela
    c.execute('''INSERT INTO tools VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (tool.Id, tool.Type, tool.D1, tool.D2, tool.D3, tool.L1, tool.L2, tool.L3, tool.CorRadius,
               tool.CorChamfer, tool.AngleColl, tool.AnglePoint, tool.NoTT, tool.GroupeMat, tool.ToolMaterial,
               tool.CoupeCentre, tool.ArrCentre, tool.TypeTar, tool.PasTar, tool.Manuf, tool.ManufRef,
               tool.ManufRefSec, tool.Code, tool.CodeBar, tool.Comment))

    conn.commit()
    conn.close()

def ExtractXMLData(xmlfile):
    paramToPropDict = {}

    with open('DIN4000.txt') as file:
        for line in file:
            fields = line.strip().split(';')
            if len(fields) > 2:
                paramToPropDict[fields[0]] = fields[1]

    if xmlfile:
        documentoXml = ET.parse(xmlfile)
        xmlDoc = documentoXml.getroot()

        toolNode = xmlDoc.find('.//Tool')
        newTool = Tool()

        for categoryNode in toolNode.findall('.//Category-Data'):
            categoryName = categoryNode.find('PropertyName').text.strip()
            if categoryName == 'NSM':
                nsmValue = categoryNode.find('Value').text.strip()
                if nsmValue in paramToPropDict:
                    propName = paramToPropDict[nsmValue]
                    setattr(newTool, 'Type', propName)
                break

        for node in toolNode:
            for paramNode in node.findall('Property-Data'):
                paramName = paramNode.find('PropertyName').text.strip()
                paramValue = paramNode.find('Value').text.strip()

                if paramName in paramToPropDict:
                    propName = paramToPropDict[paramName]
                    prop = getattr(newTool, propName)
                    paramValue = paramValue.replace(',', '.')
                    if paramValue == 'FSA':
                        paramValue = 'FRAISA' #TODO check list to show right name

                    if paramValue.isdigit():
                        setattr(newTool, propName, int(paramValue))
                    else:
                        try:
                            setattr(newTool, propName, float(paramValue))
                        except ValueError:
                            setattr(newTool, propName, paramValue)

        print(newTool) # replace with appropriate action

        # Insere os dados da ferramenta na tabela
        InsertToolData(newTool)
    else:
        print('Tool not found')

# Cria a tabela de ferramentas
CreateToolTable()

# Abre a janela de diálogo para selecionar o arquivo XML
Tk().withdraw()
xml_file_path = askopenfilename(title='Selecione um arquivo XML', filetypes=[('XML Files', '*.xml')])

if not xml_file_path:
    print('Nenhum ficheiro XML selecionado.')
    exit()

# Faz o parsing do arquivo XML
tree = ET.parse(xml_file_path)
root = tree.getroot()

# Obtém os dados da ferramenta
ExtractXMLData(xml_file_path)
