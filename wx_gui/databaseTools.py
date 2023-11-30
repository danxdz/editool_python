import sqlite3
from debugOutput import debugOut as db
from tool import Tool


def sqlConn():
    # Connect to the SQLite database
    conn = sqlite3.connect('tool_manager.db')
    cursor = conn.cursor()
    return cursor


def load_tools_from_database(self):
        cursor = sqlConn()
        # Lê as ferramentas do banco de dados
        cursor.execute("SELECT * FROM tools")
        tools = cursor.fetchall()
        print("Ferramentas lidas do banco de dados: ", len(tools))
        # Adiciona as ferramentas ao Treeview
        tools_list = []
        for tool_data in tools:
            tool = Tool(*tool_data[1:])
            print("tool", tool.Name)
            tools_list.append(tool)
            #self.add_tool_to_treeview(tool)
        return tools_list

def deleteTool(id):
    #connect to the database
    conn = sqlite3.connect('tool_manager.db')
    #create a cursor
    cursor = conn.cursor()
    #delete a record
    print("delete :: "+str(id.Name))
    tmp = "DELETE from tools WHERE name='" + str(id.Name) + "'"
    cursor.execute(tmp)
    #commit changes
    conn.commit()
    #close connection
    conn.close()


def saveTool(tool):
        # Conecta ao banco de dados (ou cria um novo se não existir)
    conn = sqlite3.connect('tool_manager.db')

    # Cria um cursor para executar comandos SQL
    cursor = conn.cursor()

    # Cria a tabela 'tools' com os atributos desejados (caso ainda não exista)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            toolType TEXT,
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
        INSERT INTO tools (Name, toolType, GroupeMat, D1, L1, L2, L3, D3, NoTT, RayonBout, Chanfrein, CoupeCentre,
            ArrCentre, TypeTar, PasTar, Manuf, ManufRef, ManufRefSec, Code, CodeBar,Comment)
        VALUES (:Name, :toolType, :GroupeMat, :D1, :L1, :L2, :L3, :D3, :NoTT, :RayonBout, :Chanfrein, :CoupeCentre,
            :ArrCentre, :TypeTar, :PasTar, :Manuf, :ManufRef, :ManufRefSec, :Code, :CodeBar, :Comment)
    ''', tool.__dict__)

    # Confirma a transação
    conn.commit()

    print('Ferramenta adicionada ao banco de dados.',conn.total_changes)

    # Fecha a conexão
    conn.close()