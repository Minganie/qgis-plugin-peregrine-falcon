# -*- coding: utf-8 -*-


# Spécification des chemins de l'interpreteur et des librairies sous windows
###### Vérifier si le OS est Windows


import gdal, ogr, osr
from gdalconst import *
import numpy
from scipy import ndimage
import scipy.stats
import os
from numpy import ndenumerate
import processing
from qgis.core import QgsRasterLayer, QgsRaster, QgsRasterDataProvider, QgsVectorLayer, QgsVectorDataProvider, QgsField, QgsPoint
from PyQt4.QtCore import QVariant

class peregrineFalcon:

    input_raster = ""
    input_water = ""
    input_wetland = ""
    output_path = ""
    slope_area = ""
    water_area = ""
    wetland_area = ""
    units = ""
    slope_deg = ""
    falaises_data = []
    input_data = ""






    def __init__(self, iface, communications, progress, input_dem, input_water, input_wetland, output_path, slope_area, water_area, wetland_area, units, slope_deg):
        self.input_dem = input_dem
        self.input_water = input_water
        self.input_wetland = input_wetland
        self.output_path = output_path
        self.slope_area = slope_area
        self.water_area = water_area
        self.wetland_area = wetland_area
        self.units = units
        self.slope_deg = slope_deg

        self.iface = iface
        self.progress = progress

        self.communications = communications




    # Utilisation du driver GTiff pour GDAL
    def set_gdal_driver(self):
        self.writeDriver = gdal.GetDriverByName('GTiff')
        self.communications.write_qgis_logs("info", u"GDAL Driver = GTiff")




    # Ouverture du Slope raster fait à partir de slope_to_dem()
    def open_input_dem(self):
        self.input_ds = gdal.Open(self.input_dem)
        self.communications.write_qgis_logs("info", u"Ouverture du raster %s" % self.input_dem)




    # Obtenir une matrice numpy avec le raster en entrée
    def get_input_data(self):
        self.communications.show_message("info", u"Obtenir une matrice du raster en entrée")
        input_raster_band1 = self.input_ds.GetRasterBand(1)
        self.input_data = input_raster_band1.ReadAsArray(0,0, self.cols, self.rows)




    # Obtenir la projection et le geotransform du raster en entrée ###
    def get_dem_spatial_ref(self):

        self.communications.show_message("info", u"Obtenir la projection et le geotransform du raster en entrée\n")
        if self.input_ds != None:
            # Obtenir la projection de l'image
            self.input_prj = self.input_ds.GetProjection()
            self.communications.write_qgis_logs("info", u"Projection de " + self.input_dem + ": " + str(self.input_prj))

            # Informations sur la position de l'image input et de la taille des pixels
            self.input_geot = self.input_ds.GetGeoTransform()
            self.communications.write_qgis_logs("info", u"Geotransform de " + self.input_dem + ": " + str(self.input_geot))

            # Nombre de colonnes et de rows de l'image en input
            self.cols = self.input_ds.RasterXSize
            self.rows = self.input_ds.RasterYSize

            self.communications.write_qgis_logs("info", u"Nombre de colonnes de " + self.input_dem + ": " + str(self.cols))
            self.communications.write_qgis_logs("info", u"Nombre de rangées de" + self.input_dem + ": " + str(self.rows))

            # Extent du dem en entrée
            minx = self.input_geot[0]
            maxy = self.input_geot[3]
            maxx = minx + self.input_geot[1]*self.cols
            miny = maxy + self.input_geot[5]*self.rows

            self.communications.show_message("info", u"Taille de l'image:" + str(self.cols) + " x " + str(self.rows))
            self.communications.write_qgis_logs("info", u"Extent du raster input: " + str(minx) + " " + str(maxy) + " " + str(maxx) + " " + str(miny))

        else:
            self.communications.show_message("critical", "Impossible d'ouvrir le fichier '%s'" % self.input_dem)






    # Obtenir un array numpy du raster en entrée
    def input_raster_data(self):
        self.communications.show_message("info", u"Obtenir un array numpy du raster en entrée\n")
        input_raster_band1 = self.input_ds.GetRasterBand(1)

        return input_raster_band1.ReadAsArray(0,0, self.cols, self.rows)






    # Convertir le DEM en entrée en raster de pentes
    def dem_to_slopes(self):
        self.communications.show_message("info", "Transformation du DEM en Slope")

        self.slope = self.output_path + os.sep + "slope.tif"

        # Utilisation de l'algorithme de QGIS
        processing.runalg("gdalogr:slope", self.input_dem, 1, False, False, False, 1, self.slope)
        self.get_slopes_data()



    # Obtenir la matrice des pentes
    def get_slopes_data(self):
        self.input_slopes = gdal.Open(self.slope)
        self.communications.write_qgis_logs("info", u"Ouverture du raster %s" % self.slope)
        slopes_band1 = self.input_slopes.GetRasterBand(1)

        self.slopes_data = slopes_band1.ReadAsArray(0,0, self.cols, self.rows)
        del self.input_slopes




    # Convertir le DEM en entrée en raster d'Aspect (orientation des pentes)
    def dem_to_aspect(self):
        self.communications.show_message("info", "Calcul de l'orientation des pentes")

        self.aspect = self.output_path + os.sep + "aspect.tif"

        # Utilisation de l'algorithme de QGIS
        processing.runalg("gdalogr:aspect", self.input_dem, 1, False, False, False, False, self.aspect)
        self.get_aspect_data()


    # Obtenir la matrice de l'orientation des pentes
    def get_aspect_data(self):
        self.input_aspect = gdal.Open(self.aspect)
        self.communications.write_qgis_logs("info", u"Ouverture du raster %s" % self.aspect)
        aspect_band1 = self.input_aspect.GetRasterBand(1)

        self.aspect_data = aspect_band1.ReadAsArray(0,0, self.cols, self.rows)



    # Reclassification de la matrice de l'orientation des pentes.
    def aspect_reclass(self):

        self.communications.show_message("info", u"Reclassification de la matrice 'Aspect'")

        self.aspect_data[numpy.where((self.aspect_data >= 0) & (self.aspect_data < 45)) ] = 1
        self.aspect_data[numpy.where((self.aspect_data >= 315) & (self.aspect_data <= 360))] = 1

        self.aspect_data[numpy.where((self.aspect_data >= 45) & (self.aspect_data < 90))] = 2
        self.aspect_data[numpy.where((self.aspect_data >= 270) & (self.aspect_data < 315))] = 2

        self.aspect_data[numpy.where((self.aspect_data >= 90) & (self.aspect_data < 135))] = 3
        self.aspect_data[numpy.where((self.aspect_data >= 225) & (self.aspect_data < 270))] = 3

        self.aspect_data[numpy.where((self.aspect_data >= 135) & (self.aspect_data < 225))] = 4

        self.aspect_data[numpy.where((self.aspect_data == -9999))] = 1
        self.aspect_data[numpy.isnan(self.aspect_data)] = 1

        # Écriture de l'image en output pour la fonction
        self.write_gtiff("aspect_reclass.tif", self.aspect_data)





    #Identifier les pentes dont l'inclinaison (dedgrés) est plus élevée que le paramètre spécifié
    def identify_cliffs(self):
        self.falaises_data = self.slopes_data

        # Enlever tout les pixels dont la valeur est inférieur à celle spécifié dans les paramètres
        self.communications.show_message("info", u"Élimination des pixels inférieurs à %s" % str(self.slope_deg))
        self.falaises_data[self.falaises_data < float(self.slope_deg)] = 0
        self.falaises_data[numpy.isnan(self.falaises_data)] = 0

        # Écriture de l'image en output pour la fonction
        self.write_gtiff("identify_cliffs.tif", self.falaises_data)







    # Rasterizer le shapefile des étendues d'eau en entrée
    def rasterize_water(self):

        self.communications.show_message("info", u"Convertir le shapefile d'étendu d'eau en raster\n")
        self.input_water_shp = ogr.Open(self.input_water)
        self.input_water_shp_lyr = self.input_water_shp.GetLayer()

        temp_write_path = self.output_path + os.sep + 'water_rasterized.tif'
        self.water_rast_img = self.writeDriver.Create(temp_write_path, self.cols, self.rows, 1, GDT_Int32)

        self.water_rast_img.SetGeoTransform((self.input_geot[0], self.input_geot[1], self.input_geot[2], self.input_geot[3], self.input_geot[4], self.input_geot[5]))
        self.water_rast_img_band1 = self.water_rast_img.GetRasterBand(1)
        self.water_rast_img_band1.SetNoDataValue(0)



        # Écriture du raster à partir du shapefile
        self.communications.show_message("info", u"Écriture du fichier 'water_rasterized.tif'")
        gdal.RasterizeLayer(self.water_rast_img, [1], self.input_water_shp_lyr, burn_values=[1])

        self.water_rast_img.SetGeoTransform((self.input_geot[0], self.input_geot[1], self.input_geot[2], self.input_geot[3], self.input_geot[4], self.input_geot[5]))
        self.water_rast_img.SetProjection(self.input_prj)

        #
        self.water_data = self.water_rast_img_band1.ReadAsArray(0,0, self.cols, self.rows)







    # Rasterizer le shapefile de milieux humides en entrée
    def rasterize_wetland(self):

        self.communications.show_message("info", u"Convertir le shapefile de milieu humide en raster...\n")
        self.input_wetland_shp = ogr.Open(self.input_wetland)
        self.input_wetland_shp_lyr = self.input_wetland_shp.GetLayer()


        temp_write_path = self.output_path + os.sep + 'wetland_rasterized.tif'
        self.wetland_rast_img = self.writeDriver.Create(temp_write_path, self.cols, self.rows, 1, GDT_Int32)

        self.wetland_rast_img.SetGeoTransform((self.input_geot[0], self.input_geot[1], self.input_geot[2], self.input_geot[3], self.input_geot[4], self.input_geot[5]))
        self.wetland_rast_img_band1 = self.wetland_rast_img.GetRasterBand(1)
        self.wetland_rast_img_band1.SetNoDataValue(0)



        # Écriture du raster à partir du shapefile
        self.communications.show_message("info", u"Écriture du fichier 'wetland_rasterized.tif'")
        gdal.RasterizeLayer(self.wetland_rast_img, [1], self.input_wetland_shp_lyr, burn_values=[1])

        self.water_rast_img.SetGeoTransform((self.input_geot[0], self.input_geot[1], self.input_geot[2], self.input_geot[3], self.input_geot[4], self.input_geot[5]))
        self.water_rast_img.SetProjection(self.input_prj)

        #
        self.wetland_data = self.wetland_rast_img_band1.ReadAsArray(0,0, self.cols, self.rows)











    # Éliminer les falaises dont la superficie est inférieure au nombre de pixels spécifié dans les paramètres
    def calculate_slope_area(self):

        # Structure pour l'identification des pixels contigus
        struct = [[1,1,1],
                  [1,1,1],
                  [1,1,1]]

        # Identifier les falaises et le nombre
        self.labeled_slope, self.num_slope = scipy.ndimage.measurements.label(self.falaises_data, structure=struct)

        self.nb_pixel_slope = [ 0 for i in range(self.num_slope) ]

        self.communications.show_message("info", u"Élimination des falaises dont la superficie est inférieure à %s pixels" % str(self.slope_area))

        # Remplir la matrice temporaire
        for i, value1 in enumerate(self.labeled_slope):
            for j, value2 in enumerate(value1):
                if value2 != 0:
                    # Ajouter un pixel a la liste du nombre de pixel par "label"
                    self.nb_pixel_slope[value2-1] = self.nb_pixel_slope[value2-1] + 1


        # Application du threshold
        for i, value in enumerate(self.labeled_slope):
            for j, value2 in enumerate(value):
                if value2 != 0:
                    if self.nb_pixel_slope[value2-1] >= int(self.slope_area): pass
                    else:
                        self.falaises_data[i][j] = 0


        self.write_gtiff("calculate_slope_area.tif", self.falaises_data)







    # Éliminer les étendues d'eau dont la superficie est inférieure au nombre de pixels spécifié dans les paramètres
    def calculate_water_area(self):

        # Structure pour l'identification des pixels contigus
        struct = [[1,1,1],
                  [1,1,1],
                  [1,1,1]]

        # Identifier les étendues d'eau et leur nombre
        self.labeled_water, self.num_water = scipy.ndimage.measurements.label(self.water_data, structure=struct)


        self.nb_pixel_water = [ 0 for i in range(self.num_water) ]

        self.communications.show_message("info", u"Élimination des étendues d'eau dont la superficie est inférieure à %s pixels" % str(self.water_area))
        # Remplir la matrice temporaire
        for i, value1 in enumerate(self.labeled_water):
            for j, value2 in enumerate(value1):
                if value2 != 0:
                    # Ajouter un pixel a la liste du nombre de pixel par "label"
                    self.nb_pixel_water[value2-1] = self.nb_pixel_water[value2-1] + 1



        self.water_data_rc = self.water_data

        # Application du threshold
        for i, value in enumerate(self.labeled_water):
            for j, value2 in enumerate(value):
                if value2 != 0:
                    if self.nb_pixel_water[value2-1] >= int(self.water_area): pass
                    else:
                        self.water_data_rc[i][j] = 0


        self.write_gtiff("calculate_water_area.tif", self.water_data_rc)







    # Éliminer les étendues d'eau dont la superficie est inférieure au nombre de pixels spécifié dans les paramètres
    def calculate_wetland_area(self):

        # Structure pour l'identification des pixels contigus
        struct = [[1,1,1],
                  [1,1,1],
                  [1,1,1]]

        self.labeled_wetland, self.num_wetland = scipy.ndimage.measurements.label(self.wetland_data, structure=struct)


        self.nb_pixel_wetland = [ 0 for i in range(self.num_wetland) ]

        self.communications.show_message("info", u"Élimination des milieux humides dont la superficie est inférieure à %s pixels" % str(self.wetland_area))
        # Remplir la matrice temporaire
        for i, value1 in enumerate(self.labeled_wetland):
            for j, value2 in enumerate(value1):
                if value2 != 0:
                    # Ajouter un pixel a la liste du nombre de pixel par "label"
                    self.nb_pixel_wetland[value2-1] = self.nb_pixel_wetland[value2-1] + 1


        self.wetland_data_rc = self.wetland_data

        # Application du threshold
        for i, value in enumerate(self.labeled_water):
            for j, value2 in enumerate(value):
                if value2 != 0:
                    if self.nb_pixel_water[value2-1] >= int(self.water_area): pass
                    else:
                        self.water_data_rc[i][j] = 0




        self.write_gtiff("calculate_wetland_area.tif", self.wetland_data_rc)





    # Fonction pour gérer l'écriture des GTiff avec GDAL
    def write_gtiff(self, filename, array):
        self.communications.show_message("info", u"Écriture du fichier '%s'\n" % str(filename))

        # Chemin du raster à écrire
        temp_write_path = self.output_path + os.sep + filename

        # Création du fichier
        write_gtiff_img = self.writeDriver.Create(temp_write_path, self.cols, self.rows, 1, GDT_Int32)

        # Obtenir la bande de gris
        write_gtiff_img_band1 = write_gtiff_img.GetRasterBand(1)

        # Écrire la bande
        write_gtiff_img_band1.WriteArray(array, 0, 0)

        # Régler la projection et le GeoTranform du fichier écrit
        write_gtiff_img.SetProjection(self.input_prj)
        write_gtiff_img.SetGeoTransform((self.input_geot[0], self.input_geot[1], self.input_geot[2], self.input_geot[3], self.input_geot[4], self.input_geot[5]))






    # Créer un raster qui calcul la proximité par rapport aux étendues d'eau ou aux milieux humides
    def create_proximity_raster(self, input_type):

        # Valider si c'est wetland ou water et règle le chemin de sortie pour le raster qui sera créé.
        if (input_type == "wetland"):
            self.communications.show_message("info", u"Création du raster de proximité wetland")
            temp_write_path = self.output_path + os.sep + 'create_prox_raster_wl.tif'
        if (input_type == "water"):
            self.communications.show_message("info", u"Création du raster de proximité water")
            temp_write_path = self.output_path + os.sep + 'create_prox_raster_w.tif'

        # Créer l'image en sortie et ouvrir la bande de gris
        proximity_img = self.writeDriver.Create(temp_write_path, self.cols, self.rows, 1, GDT_Float32)
        proximity_img.SetGeoTransform(self.input_geot)
        proximity_img.SetProjection(self.input_prj)
        proximity_img_band1 = proximity_img.GetRasterBand(1)

        # Retourne un raster du calcul de proximité
        self.water_rast_img_band1 = self.water_rast_img.GetRasterBand(1)
        if (input_type == "wetland"):
            gdal.ComputeProximity(self.wetland_rast_img_band1, proximity_img_band1, [])
            self.wetland_prox_data = proximity_img_band1.ReadAsArray(0,0, self.cols, self.rows)
            self.reclass_proximity("wetland", self.wetland_prox_data)

        if (input_type == "water"):
            gdal.ComputeProximity(self.water_rast_img_band1, proximity_img_band1, [])
            self.water_prox_data = proximity_img_band1.ReadAsArray(0,0, self.cols, self.rows)
            self.reclass_proximity("water", self.water_prox_data)





    # Reclassification des rasters de proximités.
    def reclass_proximity(self, name, input):
        self.communications.show_message("info", u"Reclassification des matrices de proximité'")

        # Reclassification de l'entrée
        input[numpy.where((input >= 0) & (input < (10*input.max()/100))) ] = 10
        input[numpy.where((input >= (10*input.max()/100)) & (input < (20*input.max()/100))) ] = 9
        input[numpy.where((input >= (20*input.max()/100)) & (input < (30*input.max()/100))) ] = 8
        input[numpy.where((input >= (30*input.max()/100)) & (input < (40*input.max()/100))) ] = 7
        input[numpy.where((input >= (40*input.max()/100)) & (input < (50*input.max()/100))) ] = 6
        input[numpy.where((input >= (50*input.max()/100)) & (input < (60*input.max()/100))) ] = 5
        input[numpy.where((input >= (60*input.max()/100)) & (input < (70*input.max()/100))) ] = 4
        input[numpy.where((input >= (70*input.max()/100)) & (input < (80*input.max()/100))) ] = 3
        input[numpy.where((input >= (80*input.max()/100)) & (input < (90*input.max()/100))) ] = 2
        input[numpy.where((input >= (90*input.max()/100)) & (input <= (100*input.max()/100))) ] = 1

        input[numpy.where((input == -9999))] = 1
        input[numpy.isnan(input)] = 1

        # Écrire le raster et le array selon la source
        if (name == "water"):
            self.water_prox_data_rc = input
            # Écriture de l'image en output pour la fonction
            self.write_gtiff("water_prox_reclass.tif", self.water_prox_data_rc)

        if (name == "wetland"):
            self.wetland_prox_data_rc = input
            # Écriture de l'image en output pour la fonction
            self.write_gtiff("wetland_prox_reclass.tif", self.wetland_prox_data_rc)





    # Calculer tout les rasters de données pour obtenir la matrice finale. Plus la valeur du pixel est élevée, plus l'habitat est supposé être potentiel.
    def results_calculation(self):
        self.results_raster = self.aspect_data * self.wetland_prox_data_rc * self.water_prox_data_rc * self.falaises_data
        self.write_gtiff("raster_output.tif", self.results_raster)
        self.raster_output = self.output_path + os.sep + "raster_output.tif"






    #####################################################################################
    ###             Trouver le pixel maximum de chaque parcelle de falaise            ###
    #####################################################################################

    def non_max_sup(self):

        self.communications.show_message("info", u"Générer le shapefile de points à partir des falaises")

        # Obtenir le raster de parcelles de falaise
        source = gdal.Open(self.raster_output)
        grey = numpy.array(source.GetRasterBand(1).ReadAsArray())
        # La liste des maxima, identifiés par leur coordonnées en pixels
        points = []

        # Une parcelle est un amas de pixels contigus; des pixels sont contigus s'ils se touchent en diagonale
        s = [[1, 1, 1],
             [1, 1, 1],
             [1, 1, 1]]
        # Étiqueter chaque parcelle, merci numpy!
        labeled_array, num_features = ndimage.measurements.label(grey, structure=s)
        slices = ndimage.find_objects(labeled_array)
        self.communications.show_message("info", "Il y a " + str(num_features) + " parcelles de falaise distinctes")

        # Pour chaque parcelle, mettre la valeur du pixel à zéro s'il existe une plus grande valeur ailleurs dans la parcelle
        for i, slice in enumerate(slices):
            patch = grey[slice]
            # Si la parcelle a plus d'un pixel, trouver le maximum
            if len(patch) > 1:
                ij = [ij for ij, val in ndenumerate(patch) if val == max(patch.flatten())]
                ij = ij[0]
                points.append([ij[0] + slice[0].start + 0.5, ij[1] + slice[
                    1].start + 0.5])  # ajouter 0.5 aux coordonnées pour avoir le centre du pixel
            # Si la parcelle a un seul pixel, on a déjà le maximum
            else:
                points.append([slice[0].start + 0.5, slice[1].start + 0.5])

        # Écrire le tout dans un shapefile
        driver = ogr.GetDriverByName("ESRI Shapefile")
        if os.path.exists(self.output_path + os.sep + "cliffs.shp"):
            driver.DeleteDataSource(self.output_path + os.sep + "cliffs.shp")
        shapeData = driver.CreateDataSource(self.output_path + os.sep + "cliffs.shp")

        out_layer = shapeData.CreateLayer("cliffs", geom_type=ogr.wkbPoint)

        # Créer un fichier .prj correspondant à celui du raster d'entrée
        spatial_ref = source.GetProjection()
        file_handle = open(self.output_path + os.sep + "cliffs.prj", 'w')
        file_handle.write(spatial_ref)
        file_handle.close()

        # Obtenir les coefficients de conversion pour passer de pixels à coordonnées
        affine = source.GetGeoTransform()

        # Écrire chaque point dans le shapefile
        for point in points:
            # Inverser x et y, parce que x = longitude et y = latitude...
            point = point[::-1]
            # Transformer les coordonnées en pixels en coordonnées géographiques
            x = affine[0] + affine[1] * point[0] + affine[2] * point[1]
            y = affine[3] + affine[4] * point[0] + affine[5] * point[1]

            # Écrire chaque point
            out_feat = ogr.Feature(out_layer.GetLayerDefn())

            geometry = ogr.Geometry(ogr.wkbPoint)
            geometry.SetPoint(0, x, y)

            out_feat.SetGeometry(geometry)
            out_layer.CreateFeature(out_feat)
            # Écrire les changements sur disque
            out_layer.SyncToDisk()





    # Ajouter les couches finales dans l'interface de QGIS
    def invert_affine(self, affine, point):
        Xg, Yg = point
        a, b, c, d, e, f = affine
        y = (b * Yg - b * d - e * Xg + e * a) / (b * f - e * c)
        x = (Xg - c * y - a) / b
        return int(x), int(y)






    def fill_attribute_table(self):

        # Ouvrir le shapefile
        cliffs = QgsVectorLayer(self.output_path + os.sep + "cliffs.shp", "cliffs_points", "ogr")
        caps = cliffs.dataProvider().capabilities()
        prov = cliffs.dataProvider()

        # Ouvrir tous les rasters pour obtenir les coefficients de transformation
        orientation = gdal.Open(self.output_path + os.sep + "slope.tif")
        inclinaison = gdal.Open(self.output_path + os.sep + "aspect.tif")
        prox_wetland = gdal.Open(self.output_path + os.sep + "create_prox_raster_wl.tif")
        prox_water = gdal.Open(self.output_path + os.sep + "create_prox_raster_w.tif")
        score = gdal.Open(self.output_path + os.sep + "raster_output.tif")

        # Ajouter tous les nouveaux attributs
        if caps & QgsVectorDataProvider.AddAttributes:
            cliffs.dataProvider().addAttributes([
                QgsField("ORIENT", QVariant.Int),
                QgsField("INCLIN", QVariant.Int),
                QgsField("PROX_MH", QVariant.Int),
                QgsField("PROX_LAC", QVariant.Int),
                QgsField("POINTAGE", QVariant.Int)
            ])
        cliffs.updateFields()

        patches = cliffs.getFeatures()
        if caps & QgsVectorDataProvider.ChangeAttributeValues:
            for patch in patches:
                pt = patch.geometry().asPoint()

                # Valeurs des attributs
                rept = self.invert_affine(orientation.GetGeoTransform(), pt)
                attr_ori = self.aspect_data[rept[::-1]]

                rept = self.invert_affine(inclinaison.GetGeoTransform(), pt)
                attr_inc = self.falaises_data[rept[::-1]]

                rept = self.invert_affine(prox_wetland.GetGeoTransform(), pt)
                attr_wet = self.wetland_prox_data[rept[::-1]]

                rept = self.invert_affine(prox_water.GetGeoTransform(), pt)
                attr_wat = self.wetland_prox_data[rept[::-1]]

                rept = self.invert_affine(score.GetGeoTransform(), pt)
                attr_sco = self.results_raster[rept[::-1]]

                # Inscrire les modifications
                prov.changeAttributeValues({patch.id(): {prov.fieldNameMap()['ORIENT']: int(attr_ori),
                                                         prov.fieldNameMap()['INCLIN']: int(attr_inc),
                                                         prov.fieldNameMap()['PROX_MH']: int(attr_wet),
                                                         prov.fieldNameMap()['PROX_LAC']: int(attr_wat),
                                                         prov.fieldNameMap()['POINTAGE']: int(attr_sco)
                                                         }})






    def add_results_to_qgis(self):
        self.iface.addRasterLayer(self.output_path + os.sep + "raster_output.tif", "raster_output")
        self.iface.addVectorLayer(self.output_path + os.sep + "cliffs.shp", "cliffs_points", "ogr")
