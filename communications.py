# -*- coding: utf-8 -*-

#from qgis import *



# Classe pour communiquer des messages à l'utilisateur et écrire les logs

class communications:

    def __init__(self, iface, progress, progressMessageBar):
        self.iface = iface
        self.progress = progress
        self.progressMessageBar = progressMessageBar



    def show_message(self, level, message):
        if (level == "info"):
            self.show_message_statusBar(message)
        if (level == "warning"):
            self.show_message_messageBar(level, message)
        if (level == "critical"):
            self.show_message_messageBar(level, message)


    def show_message_statusBar(self, message):
        self.iface.mainWindow().statusBar().showMessage(message)




    def show_message_messageBar(self, level, message):
        if (level == "warning"):
            self.progressMessageBar.setText("dans comm. warning")
        if (level == "critical"):
            self.progressMessageBar.setText("dans comm. critical")



    def write_qgis_logs(self, level, message):
        pass