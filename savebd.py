import sqlite3




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
        INSERT INTO tools (Name, Type, GroupeMat, D1, L1, L2, L3, D3, NoTT, RayonBout, Chanfrein, CoupeCentre,
            ArrCentre, TypeTar, PasTar, Manuf, ManufRef, ManufRefSec, Code, CodeBar,Comment)
        VALUES (:Name, :Type, :GroupeMat, :D1, :L1, :L2, :L3, :D3, :NoTT, :RayonBout, :Chanfrein, :CoupeCentre,
            :ArrCentre, :TypeTar, :PasTar, :Manuf, :ManufRef, :ManufRefSec, :Code, :CodeBar, :Comment)
    ''', tool.__dict__)

    # Confirma a transação
    conn.commit()

    print('Ferramenta adicionada ao banco de dados.',conn.total_changes)

    # Fecha a conexão
    conn.close()