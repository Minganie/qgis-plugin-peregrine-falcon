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

    def __init__(self):

        # Initialisation du driver OGR
        self.ogr_driver = ogr.GetDriverByName('ESRI Shapefile')






    def validate_input(self, inputs):

        for i, input in enumerate(inputs):
            print i
            print input

            # Vérifier si le fichier existe.
            if (os.path.exists(str(input))):
                pass

            else:

                return [False, input, "[ERREUR] Le fichier '%s' n'existe pas! % input"]

        return True











    # Retourne une liste [Geogcs, code EPSG, unités]
    def get_spatial_ref_sys(self, type, input):

        # Si l'input est un raster
        if (input != None):
            if (type == "dem"):
                # Ouverture de l'input avec GDAL
                input_ds = gdal.Open(input)
                # Obtenir la projetion du raster
                wktprj = input_ds.GetProjection()

            # Si l'input est un shapefile
            if (type == "shp"):
                # Ouverture de l'input avec OGR
                input_ds = self.ogr_driver.Open(input)
                # Obtenir la projection
                input_prj = input_ds.GetLayer().GetSpatialRef()
                # Convertir en WKT
                wktprj = osr.SpatialReference.ExportToWkt(input_prj)

            srs = osr.SpatialReference(wktprj)

            # Obtenir le code EPSG de la projection
            if (srs.IsProjected()):
                return [srs.GetAttrValue('PROJCS'), srs.GetAttrValue('AUTHORITY', 1), srs.GetAttrValue('UNIT')]
            else:
                return [srs.GetAttrValue('GEOGCS'), srs.GetAttrValue('AUTHORITY', 1), srs.GetAttrValue('UNIT')]








    def validate_input_spatial_ref_sys(self, inputs):
        if (inputs[0][1] == inputs[1][1] == inputs[2][1]):
            return True
        else:
            return False







    def set_input_spatial_ref_sys(self, input):
        self.input_ds = gdal.Open(input)
        if self.input_dem_srs is None:
            self.input_dem_srs = self.input_ds.GetProjection()

        if self.input_water_srs is None:
            self.input_water_srs = self.input_ds.GetProjection()

        if self.input_wetland_srs is None:
            self.input_wetland_srs = self.input_ds.GetProjection()

