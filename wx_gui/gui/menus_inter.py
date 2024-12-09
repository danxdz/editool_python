# class thar contains the menus for the gui and its internalization
# we create a csv with all the text and its translations
# the csv is loaded into a dictionary and the text is retrieved from the dictionary
# like first line of the csv: define the language then the text

#en;fr;pt
#open:Open;Ouvrir;Abrir  >> "open" is the key and "Open;Ouvrir;Abrir" is the value
#del:Delete;Supprimer;Borrar

import csv
import os

#read the csv file and load it into a dictionary the needed language
#the csv file must be in the same directory as the script

class MenusInter:
    def __init__(self, lang):
        #self.set_lang(lang)
        self.lang = lang
        self.menus = {}
        self.load_menu()

    def GetCustomLanguage(ts_lang=None):
        '''Get the custom language from the config file'''
        #read the config file to get the language
        data = []
        lang = -1

        if os.path.isfile('config.txt'):            
            with open('config.txt', 'r', encoding='utf-8') as file:
                data = file.readlines()
                if data:
                    for line in data:
                        if line.startswith('lang'):
                            lang = int(line.split(';')[1].strip())
                            break
            
                

            # close the file
            file.close()
      
        # if no config file, do not set the language at this point

        return lang
    
    def get_lang_code(lang):
        lang = 0 if lang == 'en' else 1 if lang == 'fr' else 2 if lang == 'pt' else -1
        return lang

    def set_lang(self, lang=0):
        '''Set the language of the menus'''
        data = []
        #if lang not int:
        if isinstance(lang, str):
            lang = lang.split('-')[0]
            lang = MenusInter.get_lang_code(lang)

        config_exists = os.path.isfile('config.txt')
        if config_exists:
            #open the file and read the data
            with open('config.txt', 'r', encoding='utf-8') as file:
                data = file.readlines()
                #check if the language is already set
                for line in data:
                    if line.startswith('lang'): #if the line starts with lang
                        data.remove(line) #remove the line
                        break
                #and else add the language to the file
                data.append(f"lang;{lang}" + '\n')
                #write the data
                file = open('config.txt', 'w', encoding='utf-8')
                file.writelines(data)
            #close the file
            file.close()
        else:
            with open('config.txt', 'w', encoding='utf-8') as file:
                file.write(f"lang;{lang}" + '\n')
        
        return lang


    def get_language_by_id(self, lang_index):
        if lang_index == 0:
            return "en"
        elif lang_index == 1:
            return "fr"
        elif lang_index == 2:
            return "pt"
        else:
            return "en"
        

    def load_menu(self):
        #print("load_menu :: ", self.lang)
        #print("load_menu :: ", os.path.dirname(os.path.abspath(__file__)))

        with open('menus.csv',  encoding='UTF-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in reader:
                #print(row)
                self.menus[row[0]] = row[1:]
                

    def get_menu(self, menu):
        #print("get_menu :: ", menu)
        #print("get_menu :: ", self.menus[menu][self.lang])        
        return self.menus[menu][self.lang]