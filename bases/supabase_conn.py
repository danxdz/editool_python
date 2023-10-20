import os
from supabase import create_client, Client
from flask import Flask, request
from realtime.connection import Socket
import asyncio
import websockets

app = Flask(__name__)

# Configurar as credenciais do Supabase
supabase_url = 'https://tcwvtjvpgupoxkxqdmnf.supabase.co'
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRjd3Z0anZwZ3Vwb3hreHFkbW5mIiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODcwOTM5MDcsImV4cCI6MjAwMjY2OTkwN30.-MeqccCaIW3QwIrczk68pmP9KzJExTRd8sllRWtKyro"
supabase: Client = create_client(supabase_url, supabase_key)

print(supabase_url)


@app.route('/new_tool', methods=['POST'])
def receive_webhook():
    data = request.json  # Acessa os dados do webhook como JSON
    print(data)
    # Aqui você pode processar os dados recebidos do webhook conforme necessário
    # Por exemplo, você pode adicionar a nova ferramenta ao banco de dados ou fazer qualquer outra ação desejada
    
    #read tools from database
    #tools = supabase.table('tools').select('*').execute()
    #print(tools)

        
    # Definir os dados a serem inseridos
    tool_data = {
        
        "column": "null",
        "Type": "FRTO",
        "GroupeMat": "iѕo M",
        "D1": 21,
        "L1": 34,
        "L2": 34,
        "L3": 90,
        "D3": 16,
        "NoTT": 4,
        "RayonBout": 1,
        "Chanfrein": "null",
        "CoupeCentre": "Non",
        "ArrCentre": "Non",
        "TypeTar": "null",
        "PasTar": "null",
        "Manuf": "Seco",
        "ManufRef": "554160R100Z4.0-SIRON-A",
        "ManufRefSec": "SIRON-A",
        "Code": "Web",
        "CodeBar": 797
    
    }
    
    result = supabase.table('tools').insert({"tool": [tool_data]}).execute()

    print(result)

    #return result
    return "ok"


if __name__ == '__main__':
    app.run(port=8001)

