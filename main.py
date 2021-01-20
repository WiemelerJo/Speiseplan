from Kochbuch import *

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QLineEdit, QDoubleSpinBox, QPushButton, QMessageBox, QHeaderView
from PyQt5.QtCore import QThread, pyqtSignal, QSignalBlocker
from PyQt5.QtCore import Qt

from sqlitedict import SqliteDict

import sys

class MyForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.button_load_data.clicked.connect(self.load)
        self.ui.edit_database_path.editingFinished.connect(self.load_from_lineEdit)
        self.ui.button_save.clicked.connect(self.save)
        self.ui.button_add.clicked.connect(self.add_entry)

    def closeEvent(self,event):
        close = QMessageBox()
        close.setText("Speichern ?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()
        if close == QMessageBox.Yes:
            self.save()
            event.accept()
        else:
            event.accept()

    def load(self):
        # Load SQLdict
        #try:
            self.fname = QFileDialog.getOpenFileName(self, 'Open file') # gt file path
            self.ui.edit_database_path.setText('Loaded database: ' + self.fname[0]) # set path to LineEdit
            self.Kochbuch = SqliteDict(self.fname[0], autocommit=True)  # Lade Haupt dictionary/ Gerichte
            self.create_content_table()
        #except:
            #print('Cannot load specified file!\nError in main.load()')
            #pass

    def load_from_lineEdit(self):
        # Load from LineEdit
        try:
            self.fname[0] = self.ui.edit_database_path.text()[17:] # get text without prefix
            self.Kochbuch = SqliteDict(self.fname[0], autocommit=True)  # Lade Haupt dictionary/ Gerichte
            self.create_content_table()
        except:
            print('Cannot load specified file!\nError in main.load_from_lineEdit()')
            pass

    def save(self):
        # get items from content_table, update Kochbuch and commit it to database
        self.Kochbuch.clear()
        table = self.ui.content_table
        header_items = [table.model().headerData(i, Qt.Horizontal) for i in range(table.model().columnCount())]

        for row_index in range(self.ui.content_table.rowCount()): # Every row is one dish/gericht
            temp_dict = dict()
            for col_index, item in enumerate(header_items):
                temp_dict[item] = table.cellWidget(row_index,col_index).text()
            self.add_gericht(temp_dict)

    def add_entry(self):
        # Add empty entry to table
        row_cnt = self.ui.content_table.rowCount()
        col_cnt = self.ui.content_table.columnCount()
        self.ui.content_table.insertRow(row_cnt)

        for col_index in range(col_cnt):
            self.ui.content_table.setCellWidget(row_cnt, col_index, QLineEdit())
            if col_index == col_cnt - 1:  # Delete Option
                self.ui.content_table.setCellWidget(row_cnt, col_index, QPushButton('Delete'))
                self.ui.content_table.cellWidget(row_cnt, col_index).clicked.connect(self.remove_entry)

    def remove_entry(self):
        table = self.ui.content_table
        # --------------Remove Row------------
        column = table.currentColumn()
        row = table.currentRow()
        table.removeRow(row)
        # -------------Remove dict entry--------
        #name = table.cellWidget(row,0).text()
        #self.del_gericht(name)

    def create_content_table(self):
        # Creates the Widgets inside the Table
        table = self.ui.content_table
        table.setRowCount(len(self.Kochbuch))
        header_items = [table.model().headerData(i, Qt.Horizontal) for i in range(table.model().columnCount())]
        row_label = []
        col_cnt = table.model().columnCount()

        for row_index, val in enumerate(self.Kochbuch.items()):
            #row_label.append(str(row_index + 1) + ' ' + str(val[0]))
            for col_index in range(col_cnt):
                table.setCellWidget(row_index,col_index,QLineEdit())
                if col_index == col_cnt - 1: # Add Delete Button
                    table.setCellWidget(row_index, col_index, QPushButton('Delete'))
                    table.cellWidget(row_index,col_index).clicked.connect(self.remove_entry)
        #self.ui.content_table.setVerticalHeaderLabels(row_label)
        self.set_text_to_table(header_items)

    def set_text_to_table(self,header_items):
        table = self.ui.content_table
        for row_index, val in enumerate(self.Kochbuch.items()):
            table.cellWidget(row_index, 0).setText(val[0]) # Name column/ set Name
            #print(val[1].values())
            for col_index, item in enumerate(header_items[1:]):
                try:
                    table.cellWidget(row_index, col_index + 1).setText(val[1][item])
                except KeyError:
                    if item == None: # Used, that the delete button text will not be overwritten
                        pass
                    else:
                        # Set unfilled category empty
                        table.cellWidget(row_index, col_index + 1).setText('')

    def add_gericht(self, entries:dict):
        # Olf func args: name: str, Fisch: bool, Nudeln: bool, Vortag: bool, SE: bool, WE: bool, WE_Wichtung: float, Wichtung: float
        # Gerichte werden gespeichert in dict()
        # Jedes Gericht wird dabei Kategorisiert in:
        #       - Fisch: Bool
        #       - Nudeln: Bool
        #       - Vortag: Bool (Wenn Sonntags viel Bestellt wird das Essen vom Vortag machen)
        #       - SE: Bool (Sonntagsessen)
        #       - WE: Bool (Wochenendessen, wie z.B Holen/Bestellen)
        #       - WE_Wichtung: Float (Jedes Gericht soll die chance haben am WE dran zu kommen, Holen/Bestellen oder z.B. Rolladen sollen bevorzugt werden)
        #       - Wichtung: Float (Warkeit des Gerichtes ausgewählt zu werden, um doppelte zu vermeiden) 1.0 = Kommt dran; 0 = wird nicht dran kommen
        # -------------------------------------------------------------------------------
        # Tortillas = dict() # Ein Gericht dict()
        # Tortillas['Fisch'] = False
        # Tortillas['Nudeln'] = False
        # Tortillas['Vortag'] = False
        # Tortillas['SE'] = False
        # Tortillas['WE'] = False
        # Tortillas['WE_Wichtung'] = 0.1
        # Tortillas['Wichtung'] = 1.0

        # Gerichte['Tortillas'] = Tortillas
        # -------------------------------------------------------------------------------
        '''name_dict = dict()
        name_dict['Fisch'] = Fisch
        name_dict['Nudeln'] = Nudeln
        name_dict['Vortag'] = Vortag
        name_dict['SE'] = SE
        name_dict['WE'] = WE
        name_dict['WE_Wichtung'] = WE_Wichtung
        name_dict['Wichtung'] = Wichtung'''
        name = entries['Name']
        self.Kochbuch[name] = entries

    def del_gericht(self,name):
        self.Kochbuch.pop(name)

    def update_kochbuch(self, Kochbuch: dict, name: str, kategorie: str, value: any):
        # Da hier mit dict im dict gearbeitet wird und dasa äußerste dict ein SQLdict ist,
        # müssen hier die Einträge ein bisschen umständlich verändert werden, um vom RAM in die SQL datei zu schreiben
        update = Kochbuch[name]
        update[kategorie] = value
        Kochbuch[name] = update

if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MyForm()
    w.show()
    sys.exit(app.exec_())