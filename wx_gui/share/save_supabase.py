
import os
from supabase import create_client, Client

from env import SUPABASE_URL 
from env import SUPABASE_KEY


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def readTools():
    print("readTools")
    response = supabase.table('tools').select("*").execute()
    print("response :: ", response)
    return response

readTools()
