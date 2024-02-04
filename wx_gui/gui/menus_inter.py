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
        self.lang = lang
        self.menus = {}
        self.load_menu()

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
