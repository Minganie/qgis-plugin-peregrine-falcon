# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PeregrineFalcon
                                 A QGIS plugin
 A tool to help identify potential habitats for the Peregrine Falcon in Northern American
                              -------------------
        begin                : 2016-04-12
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Myriam Luce, Patrice Pineault
        email                : Myriam.Luce@USherbrooke.ca, patrice.pineault@usherbrooke.ca
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QProgressBar, QMessageBox

# Initialize Qt resources from file resources.py
import resources


from peregrinefalcon_dialog import PeregrineFalconDialog
from communications import communications
from faucon import peregrineFalcon
from faucon_validation import validation

import os.path



class PeregrineFalcon:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PeregrineFalcon_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = PeregrineFalconDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Peregrine Falcon')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PeregrineFalcon')
        self.toolbar.setObjectName(u'PeregrineFalcon')

        ##################################################################################################################
        ##################################################################################################################


        # Initialisation des variables
        self.input_wetland = ""
        self.input_water = ""
        self.input_dem = ""
        self.plugin_name = "PeregrineFalcon"

        # Initialisation de la progress bar
        self.initialize_progress_bar()


        # Gérer les évènements des boutons
        self.dlg.demPushButton.clicked.connect(self.select_dem_file)
        self.dlg.waterPushButton.clicked.connect(self.select_water_file)
        self.dlg.wetLandPushButton.clicked.connect(self.select_wetland_file)
        self.dlg.outPushButton.clicked.connect(self.select_output_folder)
        self.dlg.helpPushButton.clicked.connect(self.show_help)

        # Gérer les évènements des LineEdits
        self.dlg.demLineEdit.editingFinished.connect(self.write_dem_srs)
        self.dlg.waterLineEdit.editingFinished.connect(self.write_water_srs)
        self.dlg.wetLandLineEdit.editingFinished.connect(self.write_wetland_srs)

        # Gérer les évènements des Sliders
        self.dlg.slopeAreaSlider.valueChanged.connect(self.show_slope_area_value)
        self.dlg.waterAreaSlider.valueChanged.connect(self.show_water_area_value)
        self.dlg.slopeDegSlider.valueChanged.connect(self.show_slope_deg_value)
        self.dlg.wetLandAreaSlider.valueChanged.connect(self.show_wet_land_value)

        # Régler les valeurs minimum et maximum des Sliders
        self.dlg.slopeAreaSlider.setMinimum(2)
        self.dlg.slopeAreaSlider.setMaximum(1000)

        self.dlg.slopeDegSlider.setMinimum(20)
        self.dlg.slopeDegSlider.setMaximum(90)

        self.dlg.waterAreaSlider.setMinimum(2)
        self.dlg.waterAreaSlider.setMaximum(1000)

        self.dlg.wetLandAreaSlider.setMinimum(2)
        self.dlg.wetLandAreaSlider.setMaximum(1000)

        # Initialiser des valeurs par défaut pour les paramètres
        self.dlg.slopeAreaSlider.setValue(5)
        self.dlg.waterAreaSlider.setValue(5)
        self.dlg.wetLandAreaSlider.setValue(5)
        self.dlg.slopeDegSlider.setValue(40)


        # Initialisation des classes de communication et de validation
        self.communications = communications(self.iface, self.progress, self.progressMessageBar, self.plugin_name)
        self.validate = validation(self.iface, self.communications, self.plugin_name)



        ################################# VALEURS TEMPORAIRES POUR DEBUG ##############################################
        # self.dlg.demLineEdit.setText(r"/home/prototron/.qgis2/python/plugins/qgis-plugin-peregrine-falcon/in_data/dem_highres_2.tif")
        # self.dlg.waterLineEdit.setText(r"/home/prototron/.qgis2/python/plugins/qgis-plugin-peregrine-falcon/in_data/waterbody_2.shp")
        # self.dlg.outLineEdit.setText(r'/home/prototron/.qgis2/python/plugins/qgis-plugin-peregrine-falcon/out_data/')
        # self.dlg.wetLandLineEdit.setText(r'/home/prototron/.qgis2/python/plugins/qgis-plugin-peregrine-falcon/in_data/saturated_soil_2.shp')

        # self.dlg.demLineEdit.setText(r"C:\Users\Myriam\Documents\S5 - H2016\GMQ580\qgis-plugin-peregrine-falcon\in_data\proj\dem_highres_proj.tif")
        # self.dlg.waterLineEdit.setText(r"C:\Users\Myriam\Documents\S5 - H2016\GMQ580\qgis-plugin-peregrine-falcon\in_data\proj\waterbody_3.shp")
        # self.dlg.outLineEdit.setText(r'C:\Users\Myriam\Documents\S5 - H2016\GMQ580\qgis-plugin-peregrine-falcon\out_data')
        # self.dlg.wetLandLineEdit.setText(r'C:\Users\Myriam\Documents\S5 - H2016\GMQ580\qgis-plugin-peregrine-falcon\in_data\proj\saturated_soil_2.shp')


        self.dlg.demLineEdit.setText(r"C:\OSGeo4W64\apps\qgis\python\plugins\qgis-plugin-peregrine-falcon\in_data\proj\dem_highres_proj.tif")
        self.dlg.waterLineEdit.setText(r"C:\OSGeo4W64\apps\qgis\python\plugins\qgis-plugin-peregrine-falcon\in_data\proj\waterbody_3.shp")
        self.dlg.outLineEdit.setText(r'C:\TEMP')
        self.dlg.wetLandLineEdit.setText(r'C:\OSGeo4W64\apps\qgis\python\plugins\qgis-plugin-peregrine-falcon\in_data\proj\saturated_soil_2.shp')
        ###############################################################################################################



        ##################################################################################################################
        ##################################################################################################################







    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PeregrineFalcon', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/PeregrineFalcon/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Peregrine Falcon'),
            callback=self.run,
            parent=self.iface.mainWindow())



    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Peregrine Falcon'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        # show the dialog
        self.dlg.show()



        # Initialiser la Progress Bar
        self.initialize_progress_bar()

        # Run the dialog event loop
        result = self.dlg.exec_()

        # See if OK was pressed
        if result:

            self.communications.write_qgis_logs("info", u"Bouton OK cliqué!")

            # Initialisation de la barre de progrès
            self.iface.messageBar().clearWidgets()
            self.iface.mainWindow().statusBar().clearMessage()

            self.iface.messageBar().pushWidget(self.progressMessageBar, self.iface.messageBar().INFO)




            # Régler les variables avec le chemin des fichiers en entrée
            self.input_dem = self.dlg.demLineEdit.text()
            self.input_water = self.dlg.waterLineEdit.text()
            self.input_wetland = self.dlg.wetLandLineEdit.text()


            # Validation des fichiers en entrée
            validate_input = self.validate.validate_input([self.input_dem, self.input_water, self.input_wetland])
            if (validate_input == False):
                return


            # Obtenir les système de référence spatial des fichiers en entrée
            try:
                self.write_dem_srs()
                self.write_water_srs()
                self.write_wetland_srs()
            except:
                self.communications.show_message("critical", u"[ERREUR] Erreur lors de l'obtention du SRS d'un fichier en entrée.")
                return


            # Validation du système de référence spatial des fichiers en entrée
            if (self.validate.validate_input_spatial_ref_sys([self.dem_srs[3], self.water_srs[3], self.wetland_srs[3]]) == False):
                return

            # Validation des unités de la projection
            if (self.validate.validate_projection_unit([self.dem_srs[2], self.water_srs[2], self.wetland_srs[2]]) == False):
                return

            # Validation du chemin en sortie
            validate_output = self.validate.validate_output(self.dlg.outLineEdit.text())
            if (validate_output == False):
                return


            # Début des traitements

            self.communications.write_qgis_logs("info", u"\nDébut des traitements\n")
            self.set_progress_bar_value(1)
            faucon = peregrineFalcon(self.iface, self.communications, self.progress, self.dlg.demLineEdit.text(), self.dlg.waterLineEdit.text(), self.dlg.wetLandLineEdit.text(), self.dlg.outLineEdit.text(), self.dlg.slopeLineEdit.text(), self.dlg.waterParamLineEdit.text(), self.dlg.wetLandParamLineEdit.text(), "", self.dlg.slopeDegLineEdit.text())
            faucon.set_gdal_driver()
            self.set_progress_bar_value(2)
            faucon.open_input_dem()
            self.set_progress_bar_value(3)
            faucon.get_dem_spatial_ref()
            self.set_progress_bar_value(4)
            faucon.dem_to_slopes()
            self.set_progress_bar_value(5)
            faucon.dem_to_aspect()
            self.set_progress_bar_value(6)
            faucon.aspect_reclass()
            self.set_progress_bar_value(7)
            faucon.get_input_data()
            self.set_progress_bar_value(8)
            faucon.identify_cliffs()
            self.set_progress_bar_value(9)
            faucon.rasterize_water()
            self.set_progress_bar_value(10)
            faucon.rasterize_wetland()
            self.set_progress_bar_value(11)
            faucon.calculate_water_area()
            self.set_progress_bar_value(12)
            faucon.calculate_wetland_area()
            self.set_progress_bar_value(13)
            faucon.calculate_slope_area()
            self.set_progress_bar_value(14)
            faucon.create_proximity_raster("wetland")
            self.set_progress_bar_value(15)
            faucon.create_proximity_raster("water")
            self.set_progress_bar_value(16)
            faucon.results_calculation()
            self.set_progress_bar_value(17)
            faucon.non_max_sup()
            self.set_progress_bar_value(18)
            faucon.fill_attribute_table()
            self.set_progress_bar_value(19)

            self.communications.show_message("info", u"Traitements terminés!")
            self.communications.clear_message_bar_delay()

            faucon.add_results_to_qgis()
            faucon.delete_temp_rasters()





    # Règle les valeurs de la barre de progrès
    def set_progress_bar_value(self, value):
        # Test si c'est possible d'ajouter une valeur à la barre
        try:
            self.progress.setValue(value)
        except:
            # Si c'est impossible, réinitialiser la barre de progrès, puis ajouter les valeur
            self.initialize_progress_bar()
            self.iface.messageBar().pushWidget(self.progressMessageBar, self.iface.messageBar().INFO)
            self.progress.setValue(value)





    # Initialise la barre de progrès
    def initialize_progress_bar(self):
        try:
            self.progressMessageBar = self.iface.messageBar().createMessage("Plugin Peregrine Falcon: Traitements en cours...")
            self.progress = QProgressBar()
            self.progress.setMaximum(19)
            self.progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            self.progressMessageBar.layout().addWidget(self.progress)
        except:
            pass





    # Fonction appellée par un évènnement (end editing) qui redirige vers la méthode pour écrire le SRS dans le dialog
    def write_dem_srs(self):
        # Valider si le chemin indiqué vers le fichier est valide
        validate_input = self.validate.validate_input([self.dlg.demLineEdit.text(), "", ""])
        if (validate_input):
            self.write_input_srs("dem", "dem", self.dlg.demLineEdit.text())
        else:
            self.dlg.demSrsLabel.setText("")
            self.dlg.demUnitLabel.setText("")




    # Fonction appellée par un évènnement (end editing) qui redirige vers la méthode pour écrire le SRS dans le dialog
    def write_water_srs(self):
        # Valider si le chemin indiqué vers le fichier est valide
        validate_input = self.validate.validate_input(["", self.dlg.waterLineEdit.text(), ""])
        if (validate_input):
            self.write_input_srs("water", "shp", self.dlg.waterLineEdit.text())
        else:
            self.dlg.waterSrsLabel.setText("")
            self.dlg.waterUnitLabel.setText("")




    # Fonction appellée par un évènnement (end editing) qui redirige vers la méthode pour écrire le SRS dans le dialog
    def write_wetland_srs(self):
        # Valider si le chemin indiqué vers le fichier est valide
        validate_input = self.validate.validate_input(["", "", self.dlg.wetLandLineEdit.text()])
        if (validate_input):
            self.write_input_srs("wetland", "shp", self.dlg.wetLandLineEdit.text())
        else:
            self.dlg.wetlandSrsLabel.setText("")
            self.dlg.wetlandUnitLabel.setText("")




    # Fonction pour obtenir et écrire les SRS dans les labels
    def write_input_srs(self, name, type, input):

        if (input != None) and (input != ""):
            if (name == "dem"):
                # Obtenir le SRS
                self.dem_srs = self.validate.get_spatial_ref_sys(name, input)

                # Écriture des labels
                self.dlg.demSrsLabel.setText(self.dem_srs[0])
                self.dlg.demUnitLabel.setText(self.dem_srs[2])

            if (name == "water"):
                # Obtenir le SRS
                self.water_srs = self.validate.get_spatial_ref_sys(name, input)

                # Écriture des labels
                self.dlg.waterSrsLabel.setText(self.water_srs[0] )
                self.dlg.waterUnitLabel.setText(self.water_srs[2])

            if (name == "wetland"):
                # Obtenir le SRS
                self.wetland_srs = self.validate.get_spatial_ref_sys(name, input)

                # Écriture des labels
                self.dlg.wetlandSrsLabel.setText(self.wetland_srs[0])
                self.dlg.wetlandUnitLabel.setText(self.wetland_srs[2])




    # Fonction appellée par un évènnement (button click) pour ajouter un fichier
    def select_dem_file(self):
        # Choisir un fichier
        self.input_dem = QFileDialog.getOpenFileName(self.dlg, "Selectionnez un fichier TIF", r"", '*.tif')
        self.dlg.demLineEdit.setText(self.input_dem)

        if self.input_dem != "":
            self.write_input_srs("dem", "dem", self.input_dem)




    # Fonction appellée par un évènnement (button click) pour ajouter un fichier
    def select_water_file(self):
        # Choisir un fichier
        self.input_water = QFileDialog.getOpenFileName(self.dlg, "Selectionnez un fichier SHP", r"", '*.shp')
        self.dlg.waterLineEdit.setText(self.input_water)

        if self.input_water != "":
            self.write_input_srs("water", "shp", self.input_water)




    # Fonction appellée par un évènnement (button click) pour ajouter un fichier
    def select_wetland_file(self):
        # Choisir un fichier
        self.input_wetland = QFileDialog.getOpenFileName(self.dlg, "Selectionnez un fichier SHP", r"", '*.shp')
        self.dlg.wetLandLineEdit.setText(self.input_wetland)

        if self.input_wetland != "":
            self.write_input_srs("wetland", "shp", self.input_wetland)




    # Fonction appellée par un évènnement (button click) pour ajouter le chemin de sortie
    def select_output_folder(self):
        output_file = QFileDialog.getExistingDirectory(self.dlg, "Selectionnez un emplacement de sortie", r"", QFileDialog.ShowDirsOnly)
        self.dlg.outLineEdit.setText(output_file)



    # Fonction appellée par un évènnement (value changed) dans un Slider pour afficher la nouvelle valeur
    def show_slope_area_value(self):
        slope_value = self.dlg.slopeAreaSlider.value()
        self.dlg.slopeLineEdit.setText(str(slope_value))



    # Fonction appellée par un évènnement (value changed) dans un Slider pour afficher la nouvelle valeur
    def show_water_area_value(self):
        water_value = self.dlg.waterAreaSlider.value()
        self.dlg.waterParamLineEdit.setText(str(water_value))



    # Fonction appellée par un évènnement (value changed) dans un Slider pour afficher la nouvelle valeur
    def show_slope_deg_value(self):
        slope_deg_value = self.dlg.slopeDegSlider.value()
        self.dlg.slopeDegLineEdit.setText(str(slope_deg_value))



    # Fonction appellée par un évènnement (value changed) dans un Slider pour afficher la nouvelle valeur
    def show_wet_land_value(self):
        wet_land_value = self.dlg.wetLandAreaSlider.value()
        self.dlg.wetLandParamLineEdit.setText(str(wet_land_value))




    # Fonction qui affiche la fenêtre d'aide
    def show_help(self):
        about = u"<p align='center'>Plugin Peregrine-Falcon<br><br>" \
                u"Créé par Myriam Luce (Myriam.Luce@USherbrooke.ca)<br>et<br>Patrice Pineault (patrice.pineault@usherbrooke.ca)<br><br>" \
                u"----------------------------------------<br><br>" \
                u"Les fichiers en entrée doivent obligatoirement avoir un système de coordonnées dont les unités sont en mètres!<br>" \
                u"<br>---------------------------------------<br>" \
                u"<br>DEM: Modèle d'élévation digital (DEM) en format GTiff" \
                u"<br><br>Étendues d'eau: Fichier shapefile (.shp) correspondant aux étendues d'eau du secteur à l'étude<br>" \
                u"<br>Milieux humides: Fichier shapefile (.shp) correspondant aux milieux humides du secteur à l'étude<br>" \
                u"<br>Emplacement de sortie: Choisir un dossier pour les fichiers en sortie<br>" \
                u"<br>Superficie de la pente: Garde seulement les amas de pixels contigus supérieur à la valeur déterminée<br>" \
                u"<br>Superficie des étendues d'eau: Garde seulement les amas de pixels contigus supérieur à la valeur déterminée<br>" \
                u"<br>Superficie des milieux humides: Garde seulement les amas de pixels contigus supérieur à la valeur déterminée<br>" \
                u"<br>Inclinaison de la pente (degrés): Garde seulement les valeurs d'inclinaison de la pente supérieurs à la valeur déterminée<br><br><br>" \
                u"</p>"
        self.help_dialog = QMessageBox.about(self.dlg, u"À propos", about)



