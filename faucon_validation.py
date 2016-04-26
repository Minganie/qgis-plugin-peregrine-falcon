# -*- coding: utf-8 -*-

import gdal, ogr, osr
import os


class validation:

    input_dem = ""
    input_water = ""
    input_wetland = ""
    input_dem_srs = ""
    input_water_srs = ""
    input_wetland_srs = ""

    def __init__(self, iface, communications, plugin_name):

        self.iface = iface
        # Initialisation du driver OGR
        self.ogr_driver = ogr.GetDriverByName('ESRI Shapefile')
        self.communications = communications
        self.plugin_name = plugin_name




    # Validation des fichiers en entrée
    def validate_input(self, inputs):

        for i, input in enumerate(inputs):

            if (input != ""):

                # Vérifier si le fichier existe.
                if not (os.path.exists(input)):

                    self.communications.show_message("critical", u"Le fichier '%s' n'existe pas!" % input)
                    return False

                # Vérifier la validité du raster en entrée
                if (i == 0):
                    if not (self.validate_raster(input)):
                        self.communications.show_message("critical", u"Le fichier '%s' n'est pas un raster GTiff valide!" % input)
                        return False

                # Vérifier la validité des shapefiles (polygones)
                if (i >= 1):
                    if (self.validate_polygons(input) == False):
                        self.communications.show_message("critical", u"Le fichier '%s' n'est pas un polygone valide!" % input)
                        return False

        self.communications.write_qgis_logs("info", u"Fichiers en entrée: " + inputs[0] + "\n" + inputs[1] + "\n" + inputs[2])
        # Retourne vrai si les tests ont réussis!
        return True



    # Valider le raster en entrée
    def validate_raster(self, input):

        try:
            # Ouverture du raster
            input_ds = gdal.Open(input)
            # Obtenir la bande 1 du raster
            rasterband = input_ds.GetRasterBand(1)
        except:
            self.communications.show_message("critical", u"Impossible de lire la bande 1 du raster en entrée")
            return False

        del input_ds, rasterband
        return True




    # Validation des polygones en entrée
    def validate_polygons(self, input):
        try:
            # Ouverture du fichier
            input_ds = self.ogr_driver.Open(input)
            # Obtenir le layer du fichier
            input_lyr = input_ds.GetLayer()
        except:
            self.communications.show_message("critical", u"Impossible d'ouvrir le fichier %s!" % input)
            return False

        # Vérifier les feature (est-ce un polygone?)
        for feature in input_lyr:
            validate_feature = feature.GetGeometryRef()

            if (validate_feature.GetGeometryType() != 3):
                self.communications.show_message("critical", u"Le fichier %s ne contient pas de polygones!" % input)
                return False

        del validate_feature, input_ds, input_lyr
        # Retourne vrai si les tests ont réussis!
        return True



    # Valider le chemin de sortie
    def validate_output(self, output):

        # Est-ce que le champ est vide ou le dossier existe?
        if (output.strip() != "") and (output != None):
            if not (os.path.exists(output)):
                self.communications.show_message("critical", u"Le chemin %s n'existe pas!" % output)
                return False

            # Si non, est-ce qu'on peut écrire dans le dossier?
            if not (os.access(output, os.W_OK)):
                self.communications.show_message("critical", u"Impossible d'écrire dans le chemin de sortie!")
                return False

        self.communications.write_qgis_logs("info", u"Chemin en sortie: %s" % output)
        # Retourne vrai si les tests ont réussis!
        return True



    # Retourne une liste [Geogcs, code EPSG, unités]
    def get_spatial_ref_sys(self, name, input):

        # Si l'input est un raster
        if (input != None) and (input != ""):
            if (name == "dem"):
                # Ouverture de l'input avec GDAL
                input_ds = gdal.Open(input)
                # Obtenir la projetion du raster
                self.dem_wktprj = input_ds.GetProjection()
                wktprj = input_ds.GetProjection()

            # Si l'input est un shapefile
            if (name == "water"):
                # Ouverture de l'input avec OGR
                input_ds = self.ogr_driver.Open(input)
                # Obtenir la projection
                input_prj = input_ds.GetLayer().GetSpatialRef()
                # Convertir en WKT
                self.water_wktprj = osr.SpatialReference.ExportToWkt(input_prj)
                wktprj = osr.SpatialReference.ExportToWkt(input_prj)

            if (name == "wetland"):
                # Ouverture de l'input avec OGR
                input_ds = self.ogr_driver.Open(input)
                # Obtenir la projection
                input_prj = input_ds.GetLayer().GetSpatialRef()
                # Convertir en WKT
                self.wetland_wktprj = osr.SpatialReference.ExportToWkt(input_prj)
                wktprj = osr.SpatialReference.ExportToWkt(input_prj)

            srs = osr.SpatialReference(wktprj)

            # Écriture de l'information sur le SRS
            if (srs.IsProjected()):
                return_value = [srs.GetAttrValue('PROJCS'), srs.GetAttrValue('AUTHORITY', 1), srs.GetAttrValue('UNIT'), wktprj]
            else:
                return_value = [srs.GetAttrValue('GEOGCS'), srs.GetAttrValue('AUTHORITY', 1), srs.GetAttrValue('UNIT'), wktprj]

            del input_ds
            self.communications.write_qgis_logs("info", "Srs du fichier" + input + ": " + str(srs))
            return return_value




    def validate_projection_unit(self, inputs):
        for input in inputs:
            if (str(input).lower() != "metre") and (str(input).lower() != "meter") and (str(input).lower() != "metres") and (str(input).lower() != "meters") and (str(input).lower() != "m"):
                print input
                self.communications.show_message("critical", u"Un des fichiers en entrée n'a pas des unités en mètres!")
                return False

        return True



    # Vérifier si les fichiers en entrée ont le même SRS
    def validate_input_spatial_ref_sys(self, inputs):
        # Obtenir les SRS
        srs1 = osr.SpatialReference(inputs[0])
        srs2 = osr.SpatialReference(inputs[1])
        srs3 = osr.SpatialReference(inputs[2])

        if (srs1.IsSame(srs2) == srs1.IsSame(srs3) == srs2.IsSame(srs3)):
            # Retourne vrai si les tests ont réussis!

            return True
        else:
            self.communications.show_message("critical", u"Les fichiers en entrée n'ont pas tous le même système de référence spatial.")
            return False






    # Obtenir les SRS des fichiers en entrée
    def set_input_spatial_ref_sys(self, input):
        self.input_ds = gdal.Open(input)
        if self.input_dem_srs is None:
            self.input_dem_srs = self.input_ds.GetProjection()

        if self.input_water_srs is None:
            self.input_water_srs = self.input_ds.GetProjection()

        if self.input_wetland_srs is None:
            self.input_wetland_srs = self.input_ds.GetProjection()

