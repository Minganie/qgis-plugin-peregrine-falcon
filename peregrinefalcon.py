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
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QProgressBar, QFrame
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from peregrinefalcon_dialog import PeregrineFalconDialog
from communications import communications

import time
import os.path

from faucon import peregrineFalcon
from faucon_validation import validation


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

        #########################################################
        #########################################################


        # Initialisation des variables
        self.input_wetland = ""
        self.input_water = ""
        self.input_dem = ""


        # Initialiser la progress bar
        self.progressMessageBar = self.iface.messageBar().createMessage("Plugin PeregrinFalcon: Traitements en cours...")
        self.progress = QProgressBar()
        self.progress.setMaximum(15)
        self.progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.progressMessageBar.layout().addWidget(self.progress)


        #######

        self.dlg.demPushButton.clicked.connect(self.select_dem_file)
        self.dlg.waterPushButton.clicked.connect(self.select_water_file)
        self.dlg.wetLandPushButton.clicked.connect(self.select_wetland_file)
        self.dlg.outPushButton.clicked.connect(self.select_output_folder)


        self.dlg.demLineEdit.editingFinished.connect(self.write_dem_srs)
        self.dlg.waterLineEdit.editingFinished.connect(self.write_water_srs)
        self.dlg.wetLandLineEdit.editingFinished.connect(self.write_wetland_srs)


        self.dlg.slopeAreaSlider.setMinimum(2)
        self.dlg.slopeAreaSlider.setMaximum(1000)

        self.dlg.slopeDegSlider.setMinimum(20)
        self.dlg.slopeDegSlider.setMaximum(90)

        self.dlg.waterAreaSlider.setMinimum(2)
        self.dlg.waterAreaSlider.setMaximum(1000)

        self.dlg.wetLandAreaSlider.setMinimum(2)
        self.dlg.wetLandAreaSlider.setMaximum(1000)


        # Listen to events
        self.dlg.slopeAreaSlider.valueChanged.connect(self.show_slope_area_value)
        self.dlg.waterAreaSlider.valueChanged.connect(self.show_water_area_value)
        self.dlg.slopeDegSlider.valueChanged.connect(self.show_slope_deg_value)
        self.dlg.wetLandAreaSlider.valueChanged.connect(self.show_wet_land_value)



        # Initialiser des valeurs par défaut pour les paramètres
        self.dlg.slopeAreaSlider.setValue(5)
        self.dlg.waterAreaSlider.setValue(5)
        self.dlg.wetLandAreaSlider.setValue(5)
        self.dlg.slopeDegSlider.setValue(40)
        self.dlg.pixelRadioButton.setChecked(True)


        # Initialisation des classes de communication et de validation
        self.communications = communications(self.iface, self.progress, self.progressMessageBar)
        self.validate = validation(self.iface, self.communications)



        ####### VALEURS TEMPORAIRES POUR DEBUG ################
        self.dlg.demLineEdit.setText(r"/home/prototron/.qgis2/python/plugins/qgis-plugin-peregrine-falcon/in_data/proj/larouche_slopeq_m.tif")
        self.dlg.waterLineEdit.setText(r"/home/prototron/.qgis2/python/plugins/qgis-plugin-peregrine-falcon/in_data/proj/waterbody_3.shp")
        self.dlg.outLineEdit.setText(r'/home/prototron/.qgis2/python/plugins/qgis-plugin-peregrine-falcon/out_data/')
        self.dlg.wetLandLineEdit.setText(r'/home/prototron/.qgis2/python/plugins/qgis-plugin-peregrine-falcon/in_data/proj/saturated_soil_2.shp')

        ###################################



        #########################################################
        #########################################################


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
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.

            # Initialisation de la barre de progrès
            self.iface.messageBar().pushWidget(self.progressMessageBar, self.iface.messageBar().INFO)

            # Régler les variables avec les fichiesr
            self.input_dem = self.dlg.demLineEdit.text()
            self.input_water = self.dlg.waterLineEdit.text()
            self.input_wetland = self.dlg.wetLandLineEdit.text()


            # Validation des fichiers en entrée
            validate_input = self.validate.validate_input([self.input_dem, self.input_water, self.input_wetland])
            if (validate_input[0] == False):
                print validate_input[2]
                return


            # Obtenir les système de référence spatial des fichiers en entrée
            try:
                self.write_dem_srs()
                self.write_water_srs()
                self.write_wetland_srs()
            except:
                print "Erreur lors de l'obtention du SRS d'un fichier en input"
                return


            # Validation du système de référence spatial des fichiers en entrée
            print len(self.dem_srs), len(self.water_srs), len(self.wetland_srs)
            if (self.validate.validate_input_spatial_ref_sys([self.dem_srs[3], self.water_srs[3], self.wetland_srs[3]]) == False):
                print "Les fichiers en entrée n'ont pas tous le même système de référence spatial."
                return


            # Validation du chemin en sortie
            validate_output = self.validate.validate_output(self.dlg.outLineEdit.text())
            if (validate_output[0] == False):
                print validate_output[2]
                return





            # Début des traitements
            print "------- Début ------------"
            self.progress.setValue(1)
            faucon = peregrineFalcon(self.iface, self.communications, self.progress, self.dlg.demLineEdit.text(), self.dlg.waterLineEdit.text(), self.dlg.wetLandLineEdit.text(), self.dlg.outLineEdit.text(), self.dlg.slopeLineEdit.text(), self.dlg.waterParamLineEdit.text(), self.dlg.wetLandParamLineEdit.text(), "", self.dlg.slopeDegLineEdit.text())
            faucon.set_gdal_driver()
            self.progress.setValue(2)
            faucon.open_input_raster()
            self.progress.setValue(3)
            faucon.get_raster_spatial_ref()
            self.progress.setValue(4)
            faucon.get_input_data()
            self.progress.setValue(5)
            faucon.identify_cliffs()
            self.progress.setValue(6)
            #faucon.get_coordinate_from_xy(400, 460)
            #faucon.calculate_slope_avg()
            self.progress.setValue(7)
            #faucon.rasterize_water()
            self.progress.setValue(8)
            #faucon.rasterize_wetland()
            self.progress.setValue(9)
            #faucon.calculate_water_area()
            self.progress.setValue(10)
            #faucon.calculate_wetland_area()
            self.progress.setValue(11)
            #faucon.calculate_slope_area()
            self.progress.setValue(12)

            #faucon.manage_threshold_values()
            self.progress.setValue(13)
            #faucon.create_proximity_raster("wetland")
            self.progress.setValue(14)
            #self.communications.show_message("info", u"Traitements terminés!")
            #faucon.create_proximity_raster("water")
            self.progress.setValue(15)

            # Pour une raison quelconque, on doit lancer cet instruction 2 fois pour que le message s'affiche (à cause du time.sleep)
            self.communications.show_message("info", u"Traitements terminés!")
            self.communications.show_message("info", u"Traitements terminés!")

            # Attendre 3 secondes avant d'effacer le contenu de la Status Bar et d'enlever la Message Bar
            time.sleep(3)
            self.iface.messageBar().clearWidgets()
            self.iface.mainWindow().statusBar().clearMessage()



    def write_dem_srs(self):
        validate_input = self.validate.validate_input([self.dlg.demLineEdit.text(), "", ""])[0]
        if (validate_input):
            self.write_input_srs("dem", "dem", str(self.dlg.demLineEdit.text()))
        else:
            self.dlg.demSrsLabel.setText("")
            self.dlg.demUnitLabel.setText("")



    def write_water_srs(self):
        validate_input = self.validate.validate_input(["", self.dlg.waterLineEdit.text(), ""])[0]
        if (validate_input):
            self.write_input_srs("water", "shp", str(self.dlg.waterLineEdit.text()))
        else:
            self.dlg.waterSrsLabel.setText("")
            self.dlg.waterUnitLabel.setText("")



    def write_wetland_srs(self):
        validate_input = self.validate.validate_input(["", "", self.dlg.wetLandLineEdit.text()])[0]
        if (validate_input):
            self.write_input_srs("wetland", "shp", str(self.dlg.wetLandLineEdit.text()))
        else:
            self.dlg.wetlandSrsLabel.setText("")
            self.dlg.wetlandUnitLabel.setText("")



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



    def select_dem_file(self):
        # Choisir un fichier
        self.input_dem = QFileDialog.getOpenFileName(self.dlg, "Selectionnez un fichier TIF", r"", '*.tif')
        self.dlg.demLineEdit.setText(self.input_dem)
        print self.input_dem

        if self.input_dem != "":
            self.write_input_srs("dem", "dem", self.input_dem)



    def select_water_file(self):
        # Choisir un fichier
        self.input_water = QFileDialog.getOpenFileName(self.dlg, "Selectionnez un fichier SHP", r"", '*.shp')
        self.dlg.waterLineEdit.setText(self.input_water)

        if self.input_water != "":
            self.write_input_srs("water", "shp", self.input_water)



    def select_wetland_file(self):
        # Choisir un fichier
        self.input_wetland = QFileDialog.getOpenFileName(self.dlg, "Selectionnez un fichier SHP", r"", '*.shp')
        self.dlg.wetLandLineEdit.setText(self.input_wetland)

        if self.input_wetland != "":
            self.write_input_srs("wetland", "shp", self.input_wetland)



    def select_output_folder(self):
        output_file = QFileDialog.getSaveFileName(self.dlg, "Selectionnez un emplacement de sortie", r"", "*.tif")
        self.dlg.outLineEdit.setText(output_file)



    def show_slope_area_value(self):
        slope_value = self.dlg.slopeAreaSlider.value()
        self.dlg.slopeLineEdit.setText(str(slope_value))

    def show_water_area_value(self):
        water_value = self.dlg.waterAreaSlider.value()
        self.dlg.waterParamLineEdit.setText(str(water_value))

    def show_slope_deg_value(self):
        slope_deg_value = self.dlg.slopeDegSlider.value()
        self.dlg.slopeDegLineEdit.setText(str(slope_deg_value))

    def show_wet_land_value(self):
        wet_land_value = self.dlg.wetLandAreaSlider.value()
        self.dlg.wetLandParamLineEdit.setText(str(wet_land_value))







    def show_help(self):
        pass


    def validate_input_dem(self):
        pass


    def validate_input_water(self):
        pass


    def validate_input_wetland(self):
        pass

