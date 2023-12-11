from tool import Tool

def interpret_tool_data(input_data):
    lines = input_data.strip().split('\n')
    print(lines)
    tool = Tool()

    with open("13999_paste.txt") as config_file:
        tool_params_dict = {}
        #For Each line As String In My.Resources._13399_paste.Split(Environment.NewLine)
        for line in config_file:
            #Dim fields = line.Split(";"c)
            fields = line.strip().split(";")
            print("fields: ", fields)
            #If fields(2).Contains("@") Then
            if  "@" in fields[2]:
                #toolParamsDict.Add(fields(1), fields(2).Replace("@", ""))
                tool_params_dict[fields[1]] = fields[2].replace("@", "")
        
        print(tool_params_dict)


    for i, line in enumerate(lines):
        # Se for o primeiro campo, atribuir ao atributo 'Name' da classe 'Tool'
        if i == 0:
            tool.Name = line.strip()
        elif not line.strip():
            continue  # Ignorar linhas vazias
        else:
            fields = line.strip().split("\t")
            if len(fields) < 2:
                fields = line.strip().split(" ")
                fields = line.strip().split(";")
            if len(fields) >= 2 and fields[0] in tool_params_dict:
                propName = tool_params_dict[fields[0]]
                value = fields[len(fields) - 1].strip().split(" ")
                if value[0] == "":
                    value = fields[len(fields) - 2].strip().split(" ")
                try:
                    setattr(tool, propName, value[0])
                except:
                    pass
    

    return {
        'Name': tool.Name,
        'Type': tool.Type,
        'GroupeMat': tool.GroupeMat,
        'D1': float(tool.D1),
        'D2': float(tool.D2),
        'D3': float(tool.D3),
        'L1': float(tool.L1),
        'L2': float(tool.L2),
        'L3': float(tool.L3),
        'NoTT': int(tool.NoTT),
        'RayonBout': float(tool.RayonBout),
        'Chanfrein': float(tool.Chanfrein),
        'CoupeCentre': float(tool.CoupeCentre),
        'ArrCentre': tool.ArrCentre,
        'TypeTar': int(tool.TypeTar),
        'PasTar': float(tool.PasTar),
        'Manuf': tool.Manuf,
        'ManufRef': tool.ManufRef,
        'ManufRefSec': tool.ManufRefSec,
        'Code': tool.Code,
        'CodeBar': tool.CodeBar,
        'Comment': tool.Comment,
    }

# Exemplo de utilização:
input_data = """
JHP794080E2R020.3Z4 TAN
Código GDG	B39 - JABRO HPM
Número do item	10072340

1
 

Quantidade mínima de vendas: 1
Fres. de rasgoFresamento lateralRampas, retasInterpolação helicoidal, Sólido
M
Informação solicitada  Imprimir
 Especificação Completa
 Dados De Corte
 Máquina Lateral  (33)
Nome	Descrição	Valor
APMXS	Profundidade de corte máxima em direção lateral ao avanço	19.0 mm
Código de barras	Código de barras do produto	72340100000102
CCC	capacidade de corte central	1
CGT	Tipo da geometria de corte	JHP794
Cmax	Diâmetro máximo da interpolação helicoidal	15.6 mm
Cmin	Diâmetro mínimo da interpolação helicoidal	10.4 mm
COBERTURA	Item de corte - Cobertura	TAN
DC	Diâmetro de corte	8.000 mm
DMM	diâmetro da haste	8.00 mm
DN	diâmetro do pescoço	7.50 mm
FCEDC	Contagem da face da aresta de corte	4
FHA	Ângulo de hélice da faca	40.0 deg
Classe	Classe	TAN
ICC	Canal de refrigeração interna	No
ItemNo.	Item No.	10072340
LN	Compr. do pescoço	24.5 mm
NA	Âng. do pescoço	0.0 deg
OAL	Peso total	63.0 mm
PCEDC	Perímetro da arresta de corte considerada	4
PSIR	âng de ataque	0.0 deg
RE	Raio de ponta	0.20 mm
tipodehaste	tipodehaste	Weldon
Peso	Peso liquido	0.039 kg
"""
result = interpret_tool_data(input_data)
print(result)