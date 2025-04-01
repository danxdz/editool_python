import pyodbc

# Configurações de conexão
server = r'.\SQLTOPSOLID'  # Nome do servidor e instância
database = '716718_'  # Nome da base de dados específica

#list all databases in the server

# Conectando ao servidor usando a autenticação windows

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};'
    'Trusted_Connection=yes;'
)


'''conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};'
    'UID=sa;'
    'PWD=TopSolid'
)'''

# Criando um cursor
cursor = conn.cursor()

cursor.execute("SELECT name FROM master.dbo.sysdatabases")
databases = cursor.fetchall()
print("\nDatabases:")
for db in databases:
    print(db.name)


    #show all tables in each database


cursor.execute("SELECT * FROM [719].[dbo].[Users]")
columns = cursor.fetchall()

# Imprimindo as colunas da tabela 'Document'
print("\nColunas da tabela 'Users':")    
for column in columns:
   print(column[7])
   print(column[10])

cursor.execute("SELECT * FROM [716].[dbo].[Users]")
# show dartabase content columns formated
users = cursor.fetchall()

for user in users:
    #strip the byte characters and /x
    user = [str(i).replace("b'", "").replace("\\x", "") for i in user]
    '''
    Users:
        ['-1', 'None', 'None', '-1', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'False', 'False', 'True', 'False', 'None']
        ['0', "ceD9187f295e1\\te0d5h8eefa1llg91af498dfc787034Na1d7ee}b2'", "212ul\\\\96bbKc681bb906Uc1fe'", '-1', 'b"fa\'\\\\R85O1b1ab9-1dY195e4c7"', "aab9f91a98020fe79e\\\\a9b0bee107c1-02My8ea497M;014-ke5f7e7Ke4Zc297@7fF)058498edbe9f3b899aG8ez99c7ad867f5c6qe2v'", 'b"fa\'\\\\R85O1b1ab9-1dY195e4c7"', "c0cbC8ccc9685c2&d3befbc187d9{8bja2cf1ebaffacfc*v1df7b1OKD@b61aHbejd5ccH89a4aaecfaeaaaee00s1815fc3zcd9cid9%bf4ldacb8cMyIe2a40bd0d11e8ba3'", 'b"fa\'\\\\R85O1b1ab9-1dY195e4c7"', 'b"fa\'\\\\R85O1b1ab9-1dY195e4c7"', '', 'False', 'False', 'True', 'False', '9999-12-31 23:59:59.997000']
        ['1', "ceD9187f295e1\\te0d5h8eefa1llg91af498dfc787034Na1d7ee}b2'", "212ul\\\\96bbKc681bb906Uc1fe'", '-1', 'b"fa\'\\\\R85O1b1ab9-1dY195e4c7"', "cca2e2hf6ec03>[8a9GYhNe7vPn7f 81a88n]1bV*b214\\ne7df90f8980e088efc4{a1]beacac5+y~8d8e03m\\nb3fciT2d600'", 'b"fa\'\\\\R85O1b1ab9-1dY195e4c7"', 'b"e90688dd9188dad6eb16ba5e61cff81d5e9f6fc|\\rbcf6e7e1a6b6Cdbf8{\'af94c2d7C98#c6df120fc584Gafd506c6ebed9c1f9b810fc9edeb3=3"', 'b"fa\'\\\\R85O1b1ab9-1dY195e4c7"', 'b"fa\'\\\\R85O1b1ab9-1dY195e4c7"', '', 'False', 'False', 'True', 'True', '9999-12-31 23:59:59.997000']
        ['2', "ceD9187f295e1\\te0d5h8eefa1llg91af498dfc787034Na1d7ee}b2'", "212ul\\\\96bbKc681bb906Uc1fe'", '-1', "Ab1caa0ab00b<88e2Qc5\\r~v1'", "f8of061903bOwna9}c4le0\\t'", "c1Wc91{d0d58cc594Cc2oceH*'", 'b"f1eaaafaB8019cc05cae6\';dd0689"', 'b"fa\'\\\\R85O1b1ab9-1dY195e4c7"', 'b"fa\'\\\\R85O1b1ab9-1dY195e4c7"', '$2a$11$4GY/tpQZbI/R0J74avlGKus1P7sTQx/ET1GFsuAO9pj54wRrpQx1y', 'False', 'False', 'True', 'True', '9999-12-31 23:59:59.997000']
    '''
    #break the users columns into rows
    print("\n")
    for i in range(len(user)):
        print(f"{columns[i]}: {user[i]}")
    print("\n")




'''
Users:
(-1, None, None, -1, None, None, None, None, None, None, None, False, False, True, False, None)
(0, b'\xceD\x91\x87\xf2\x95\xe1\t\xe0\xd5h\x8e\xef\xa1llg\x91\xaf4\x98\xdf\xc7\x87\x034N\xa1\xd7\xee}\xb2', b'2\x12ul\\\x96\xbbK\xc6\x81\xbb9\x06U\xc1\xfe', -1, b"\xfa'\\R\x85O\x1b\x1a\xb9-\x1dY\x195\xe4\xc7", b'\xaa\xb9\xf9\x1a\x98\x02\x0f\xe7\x9e\\\xa9\xb0\xbe\xe1\x07\xc1-\x02My\x8e\xa4\x97M;\x014-k\xe5\xf7\xe7K\xe4Z\xc2\x97@\x7fF)\x05\x84\x98\xed\xbe\x9f3b\x89\x9aG\x8ez\x99\xc7\xad\x86\x7f5\xc6q\xe2v', b"\xfa'\\R\x85O\x1b\x1a\xb9-\x1dY\x195\xe4\xc7", b'\xc0\xcbC\x8c\xcc\x96\x85\xc2&\xd3\xbe\xfb\xc1\x87\xd9{\x8bj\xa2\xcf\x1e\xba\xff\xac\xfc*v\x1d\xf7\xb1OKD@\xb6\x1aH\xbej\xd5\xccH89\xa4\xaa\xec\xfa\xea\xaa\xee\x00s\x18\x15f\xc3z\xcd\x9ci\xd9%\xbf4l\xda\xcb\x8cMyI\xe2\xa4\x0b\xd0\xd1\x1e\x8b\xa3', b"\xfa'\\R\x85O\x1b\x1a\xb9-\x1dY\x195\xe4\xc7", b"\xfa'\\R\x85O\x1b\x1a\xb9-\x1dY\x195\xe4\xc7", '', False, False, True, False, datetime.datetime(9999, 12, 31, 23, 59, 59, 997000))
(1, b'\xceD\x91\x87\xf2\x95\xe1\t\xe0\xd5h\x8e\xef\xa1llg\x91\xaf4\x98\xdf\xc7\x87\x034N\xa1\xd7\xee}\xb2', b'2\x12ul\\\x96\xbbK\xc6\x81\xbb9\x06U\xc1\xfe', -1, b"\xfa'\\R\x85O\x1b\x1a\xb9-\x1dY\x195\xe4\xc7", b'\xcc\xa2\xe2h\xf6\xec\x03>[8\xa9GYhN\xe7vPn\x7f 8\x1a\x88n]\x1bV*\xb2\x14\n\xe7\xdf\x90\xf8\x980\xe0\x88\xef\xc4{\xa1]\xbea\xca\xc5+y~\x8d\x8e\x03m\n\xb3\xfciT2\xd6\x00', b"\xfa'\\R\x85O\x1b\x1a\xb9-\x1dY\x195\xe4\xc7", b"\xe9\x06\x88\xdd\x91\x88\xda\xd6\xeb\x16b\xa5\xe6\x1c\xff\x81\xd5\xe9\xf6\xfc|\r\xbc\xf6\xe7\xe1\xa6\xb6C\xdb\xf8{'\xaf\x94\xc2\xd7C\x98#\xc6\xdf\x12\x0f\xc5\x84G\xaf\xd5\x06\xc6\xeb\xed\x9c\x1f9\xb8\x10\xfc\x9e\xde\xb3=3", b"\xfa'\\R\x85O\x1b\x1a\xb9-\x1dY\x195\xe4\xc7", b"\xfa'\\R\x85O\x1b\x1a\xb9-\x1dY\x195\xe4\xc7", '', False, False, True, True, datetime.datetime(9999, 12, 31, 23, 59, 59, 997000))
(2, b'\xceD\x91\x87\xf2\x95\xe1\t\xe0\xd5h\x8e\xef\xa1llg\x91\xaf4\x98\xdf\xc7\x87\x034N\xa1\xd7\xee}\xb2', b'2\x12ul\\\x96\xbbK\xc6\x81\xbb9\x06U\xc1\xfe', -1, b"\xfa'\\R\x85O\x1b\x1a\xb9-\x1dY\x195\xe4\xc7", b'\xf8o\xf06\x19\x03bOwn\xa9}\xc4l\xe0\t', b"\xfa'\\R\x85O\x1b\x1a\xb9-\x1dY\x195\xe4\xc7", b"\xf1\xea\xaa\xfaB\x80\x19\xcc\x05\xca\xe6';\xdd\x06\x89", b"\xfa'\\R\x85O\x1b\x1a\xb9-\x1dY\x195\xe4\xc7", b"\xfa'\\R\x85O\x1b\x1a\xb9-\x1dY\x195\xe4\xc7", '$2a$11$S4KoyLVmEt8YTHoTytyn6u/iduGgBpH0KeGHRpP8FdlIrX5e8.qoG', False, False, True, False, datetime.datetime(9999, 12, 31, 23, 59, 59, 997000))
'''


# Fechando a conexão
conn.close()
