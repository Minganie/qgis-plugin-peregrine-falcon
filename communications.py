# -*- coding: utf-8 -*-

import time
from PyQt4.QtGui import QProgressBar
from PyQt4.QtCore import Qt, QTimer
from qgis.core import QgsMessageLog



# Classe pour communiquer des messages à l'utilisateur et écrire les logs

class communications:

    def __init__(self, iface, progress, progressMessageBar, plugin_name):
        self.iface = iface
        self.progress = progress
        self.progressMessageBar = progressMessageBar
        self.plugin_name = plugin_name







    # Afficher un message à l'utilisateur
    def show_message(self, level, message):
        self.write_qgis_logs(level, message)

        # Si c'est level info, ne l'afficher que dans le status bar
        if (level == "info"):
            self.show_message_statusBar(message)
        # Si c'est level warning ou plus, afficher dans la Message bar
        if (level == "warning"):
            self.show_message_messageBar(level, "[WARNING] " + message)
        if (level == "critical"):
            self.show_message_messageBar(level, "[ERREUR] " + message)





    # Afficher un message dans la "Status Bar"
    def show_message_statusBar(self, message):
        self.iface.mainWindow().statusBar().showMessage(message)





    # Afficher un message dans le "Message Bar"
    def show_message_messageBar(self, level, message):
        if (level == "warning"):
            self.warning_message_bar(message)
            self.clear_message_bar_delay()
        if (level == "critical"):
            self.critical_message_bar(message)
            self.clear_message_bar_delay()




    # Si c'est un message "warning"
    def warning_message_bar(self, message):
        self.progressMessageBar = self.iface.messageBar().createMessage(message)
        self.progress = QProgressBar()
        self.progress.setMaximum(19)
        self.progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.progressMessageBar.layout().addWidget(self.progress)
        self.iface.messageBar().pushWidget(self.progressMessageBar, self.iface.messageBar().WARNING)




    # Si c'est un message "critique" !
    def critical_message_bar(self, message):
        self.progressMessageBar = self.iface.messageBar().createMessage(message)
        self.progress = QProgressBar()
        self.progress.setMaximum(19)
        self.progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.progressMessageBar.layout().addWidget(self.progress)
        self.iface.messageBar().pushWidget(self.progressMessageBar, self.iface.messageBar().CRITICAL)





    # Délais avant d'effacer la Message Bar
    def clear_message_bar_delay(self):
        # Attendre 8 secondes avant d'effacer le contenu de la Status Bar et d'enlever la Message Bar
        self.timer = QTimer()
        self.timer.setInterval(8000)   # 1000 ms = 1 secondes
        self.timer.setSingleShot(True)
        # Quand le timer fini, appeller la fonction pour effacer
        self.timer.timeout.connect(self.clear_message_bar)
        self.timer.start()





    # Suppression de la Message Bar et du Status Bar
    def clear_message_bar(self):
        self.iface.messageBar().clearWidgets()
        self.iface.mainWindow().statusBar().clearMessage()




    # Écriture des logs de QGIS
    def write_qgis_logs(self, level, message):

        if (level == "info"):
            QgsMessageLog.logMessage(message, self.plugin_name, level=QgsMessageLog.INFO)
        if (level == "warning"):
            QgsMessageLog.logMessage(message, self.plugin_name, level=QgsMessageLog.WARNING)
        if (level == "critical"):
            QgsMessageLog.logMessage(message, self.plugin_name, level=QgsMessageLog.CRITICAL)