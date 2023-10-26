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
