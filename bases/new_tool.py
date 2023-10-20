import os
from supabase import create_client, Client

# Configurar as credenciais do Supabase
supabase_url = 'https://tcwvtjvpgupoxkxqdmnf.supabase.co'
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRjd3Z0anZwZ3Vwb3hreHFkbW5mIiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODcwOTM5MDcsImV4cCI6MjAwMjY2OTkwN30.-MeqccCaIW3QwIrczk68pmP9KzJExTRd8sllRWtKyro"

supabase: Client = create_client(supabase_url, supabase_key)

def add_tool():
    # Define os dados da nova ferramenta
    tool_data = {
        
        "column": "null",
        "Type": "FRTO",
        "GroupeMat": "iѕo M",
        "D1": 16,
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

    # Insere a nova ferramenta na tabela 'tools'
    result = supabase.table('tools').insert({"tool":[tool_data]}).execute()

    print(result)

# Exemplo de uso
add_tool()
