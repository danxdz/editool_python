
import os
from supabase import create_client, Client

from share.env import SUPABASE_URL 
from share.env import SUPABASE_KEY


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def read_menu():
    #need to import to format UTF-8

    print("read_menu")
    try:
        response = supabase.table('menus').select("*").execute()
        print("response :: ", response)
        return response
    except:
        print("no internet connection")
        return None
    



def readTools():
    print("readTools")
    response = supabase.table('tools').select("*").execute()
    print("response :: ", response)
    return response

#readTools()
read_menu()
