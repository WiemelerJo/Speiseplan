from sqlitedict import SqliteDict

# Gerichte werden gespeichert in dict()
# Jedes Gericht wird dabei Kategorisiert in:
#       - Fisch: Bool
#       - Nudeln: Bool
#       - Vortag: Bool (Wenn Sonntags viel Bestellt wird das Essen vom Vortag machen)
#       - SE: Bool (Sonntagsessen)
#       - WE: Bool (Wochenendessen, wie z.B Holen/Bestellen)
#       - WE_Wichtung: Float (Jedes Gericht soll die chance haben am WE dran zu kommen, Holen/Bestellen oder z.B. Rolladen sollen bevorzugt werden)
#       - Wichtung: Float (Warkeit des Gerichtes ausgewählt zu werden, um doppelte zu vermeiden) 1.0 = Kommt dran; 0 = wird nicht dran kommen

def add_gericht(Kochbuch:dict, name:str, Fisch:bool, Nudeln:bool, Vortag:bool, SE:bool, WE:bool, WE_Wichtung:float, Wichtung:float):
    #-------------------------------------------------------------------------------
    #Tortillas = dict() # Ein Gericht dict()
    #Tortillas['Fisch'] = False
    #Tortillas['Nudeln'] = False
    #Tortillas['Vortag'] = False
    #Tortillas['SE'] = False
    #Tortillas['WE'] = False
    #Tortillas['WE_Wichtung'] = 0.1
    #Tortillas['Wichtung'] = 1.0

    #Gerichte['Tortillas'] = Tortillas
    #-------------------------------------------------------------------------------
    name_dict = dict()
    name_dict['Fisch'] = Fisch
    name_dict['Nudeln'] = Nudeln
    name_dict['Vortag'] = Vortag
    name_dict['SE'] = SE
    name_dict['WE'] = WE
    name_dict['WE_Wichtung'] = WE_Wichtung
    name_dict['Wichtung'] = Wichtung
    Kochbuch[name] = name_dict
    return Kochbuch

def remove(Kochbuch:dict, name:str):
    Kochbuch.pop(name)


def update_kochbuch(Kochbuch:dict, name:str, kategorie:str, value:any):
    # Da hier mit dict im dict gearbeitet wird und dasa äußerste dict ein SQLdict ist,
    # müssen hier die Einträge ein bisschen umständlich verändert werden, um vom RAM in die SQL datei zu schreiben
    update = Kochbuch[name]
    update[kategorie] = value
    Kochbuch[name] = update
    return Kochbuch

Kochbuch = SqliteDict('./test.sqlite', autocommit=True) #  Lade Haupt dictionary/ Gerichte

add_gericht(Kochbuch, 'Tortillas', False, False, False, False, False, 0.1, 1.0)
add_gericht(Kochbuch, 'Baum', False, False, False, False, False, 0.1, 1.0)
add_gericht(Kochbuch, 'Auto', False, False, False, False, False, 0.1, 1.0)

update_kochbuch(Kochbuch, 'Tortillas', 'Wichtung', 10.0)

#print(len(Kochbuch))
for i in Kochbuch.items():
    print(i[0])

remove(Kochbuch,'Auto')

for i in Kochbuch.items():
    print(i[0])


