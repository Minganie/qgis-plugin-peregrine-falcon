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





    # Retourne False si il y a un problème avec le fichier en entrée, avec le nom du fichier et le message d'erreur
    # Sous la form [Bool, "filename", "message"]
    def validate_input(self, inputs):

        for i, input in enumerate(inputs):

            if (input != ""):

                # Vérifier si le fichier existe.
                if not (os.path.exists(str(input))):
                    return [False, input, "[ERREUR] Le fichier '%s' n'existe pas!" % input]

                # Vérifier la validité du raster en entrée
                if (i == 0):
                    if not (self.validate_raster(input)):
                        return [False, input, "[ERREUR] Le fichier '%s' n'est pas un raster GTiff valide!" % input]

                # Vérifier la validité des shapefiles (polygones)
                if (i >= 1):
                    if (self.validate_polygons(input) == False):
                        return [False, input, "[ERREUR] Le fichier '%s' n'est pas un fichier de polygones!" % input]

        return [True, "", ""]




    def validate_raster(self, input):

        try:
            input_ds = gdal.Open(input)
            rasterband = input_ds.GetRasterBand(5)
        except:
            return False

        del input_ds, rasterband
        return True





    def validate_polygons(self, input):
        try:
            input_ds = self.ogr_driver.Open(input)
            input_lyr = input_ds.GetLayer()
        except:
            return False

        for feature in input_lyr:
            validate_feature = feature.GetGeometryRef()

            if (validate_feature.GetGeometryType() != 3):
                return False

        del validate_feature, input_ds, input_lyr
        return True




    def validate_output(self, output):
        if (output.strip() != "") and (output != None):
            if not (os.path.exists(output)):
                return [False, output, "[ERREUR] Le chemin %s n'existe pas!" % output]

            if not (os.access(output, os.W_OK)):
                return [False, output, "[ERREUR] Impossible d'écrire dans le chemin de sortie!"]





    # Retourne une liste [Geogcs, code EPSG, unités]
    def get_spatial_ref_sys(self, type, input):

        # Si l'input est un raster
        if (input != None) and (input != ""):
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

            # Écriture de l'information sur le SRS
            if (srs.IsProjected()):
                return_value = [srs.GetAttrValue('PROJCS'), srs.GetAttrValue('AUTHORITY', 1), srs.GetAttrValue('UNIT')]
            else:
                return_value = [srs.GetAttrValue('GEOGCS'), srs.GetAttrValue('AUTHORITY', 1), srs.GetAttrValue('UNIT')]

            del input_ds
            return return_value







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

