# -*- coding: utf-8 -*-


# Spécification des chemins de l'interpreteur et des librairies sous windows
###### Vérifier si le OS est Windows


import gdal, ogr
from gdalconst import *
import numpy
import scipy.ndimage
import scipy.stats
import os




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



    def __init__(self, input_raster, input_water, input_wetland, output_path, slope_area, water_area, wetland_area, units, slope_deg):
        self.input_raster = input_raster
        self.input_water = input_water
        self.input_wetland = input_wetland
        self.output_path = output_path
        self.slope_area = slope_area
        self.water_area = water_area
        self.wetland_area = wetland_area
        self.units = units
        self.slope_deg = slope_deg

        print "\n\nPlugin PeregrineFalcon\n\n"




    def set_gdal_driver(self):
        self.writeDriver = gdal.GetDriverByName('GTiff')






    def open_input_raster(self):
        self.input_ds = gdal.Open(self.input_raster)




    def get_input_data(self):
        print "Obtenir un array numpy du raster en entrée\n"
        input_raster_band1 = self.input_ds.GetRasterBand(1)
        self.input_data = input_raster_band1.ReadAsArray(0,0, self.cols, self.rows)






    ####################################################################
    ### Obtenir la projection et le geotransform du raster en entrée ###
    ####################################################################

    def get_raster_spatial_ref(self):

        print "Obtenir la projection et le geotransform du raster en entrée\n"
        if self.input_ds != None:
            # Obtenir la projection de l'image
            self.input_prj = self.input_ds.GetProjection()

            # Informations sur la position de l'image input et de la taille des pixels
            self.input_geot = self.input_ds.GetGeoTransform()

            # Nombre de colonnes et de rows de l'image en input
            self.cols = self.input_ds.RasterXSize
            self.rows = self.input_ds.RasterYSize


            # Extent
            minx = self.input_geot[0]
            maxy = self.input_geot[3]
            maxx = minx + self.input_geot[1]*self.cols
            miny = maxy + self.input_geot[5]*self.rows


            print self.cols, self.rows

            print minx, maxy, maxx, miny
        else:
            print "Impossible d'ouvrir le fichier '%s'" % self.input_raster





    ##################################################
    ### Obtenir un array numpy du raster en entrée ###
    ##################################################

    def input_raster_data(self):
        print "Obtenir un array numpy du raster en entrée\n"
        input_raster_band1 = self.input_ds.GetRasterBand(1)

        return input_raster_band1.ReadAsArray(0,0, self.cols, self.rows)







    def dem_to_slopes(self):
        pass






    def dem_to_aspect(self):
        pass




    ####################################################################################################
    ### Identifier les pentes dont l'inclinaison (dedgrés) est plus élevée que le paramètre spécifié ###
    ####################################################################################################

    def identify_cliffs(self):
        self.falaises_data = self.input_data

        # Enlever tout les pixels dont la valeur est inférieur à celle spécifié dans les paramètres
        print "Élimination des pixels inférieur à %s" % str(self.slope_deg)
        self.falaises_data[self.falaises_data < float(self.slope_deg)] = 0
        self.falaises_data[numpy.isnan(self.falaises_data)] = 0

        # Écriture de l'image en output pour la fonction
        self.write_gtiff("identify_cliffs.tif", self.falaises_data)








    ############################################################################################################################################
    ### Calculer la valeur moyenne de chaque pixel de chaque falaises et faire une reclassification de ces pixels avec les valeurs calculées ###
    ############################################################################################################################################

    def calculate_slope_avg(self):

        # Structure pour l'identification des pixels contigus (gauche, droit, haut, bas et diagonales)
        struct = [[1,1,1],
                  [1,1,1],
                  [1,1,1]]

        # Identification des pixels contigus (un genre d'algorithme de "fill" comme dans Gimp)
        print "Identification des pixels contigus"
        self.labeled_cliffs, self.num_cliffs = scipy.ndimage.measurements.label(self.falaises_data, structure=struct)


        # Matrice temporaire pour stocker les valeurs de chaque pixel de chaque "label"
        tmp_avg_slope = [ [""] for i in range(self.num_cliffs)]

        # Matrice pour stocker le nombre de pixels par "label"
        self.nb_pixel_cliff = [ 0 for i in range(self.num_cliffs) ]


        # Calculer la moyenne d'inclinaison de chaque cliffs
        hist1, bin_edges1 = numpy.histogram(self.labeled_cliffs, bins=self.num_cliffs)

        #print bin_edges1
        #print hist1

        hist2, bin_edges2 = numpy.histogram(self.labeled_cliffs, weights=self.falaises_data, bins=self.num_cliffs)

        #print bin_edges2
        #print hist2
        #print len(hist1), len(hist2)
        avg_slope = []
        for i, j in enumerate(hist2):
            avg_slope.append(j / hist1[i])
        avg_slope[0] = 0



        # Reclassification de la matrice de falaise
        print "Reclassification de la matrice de falaise"
        self.falaises_data_rc = self.falaises_data


        for i, value in enumerate(self.labeled_cliffs):

            for j, value2 in enumerate(value):
               # print avg_slope[value2-1]
                if value2 != 0:
                    self.falaises_data_rc[i][j] = avg_slope[value2-1]
                else:
                    self.falaises_data_rc[i][j] = 0




        self.write_gtiff("identify_cliffs_rc.tif", self.falaises_data_rc)



        self.drop_below_avg()





    ######################################################################################################################################
    ### Éliminer toutes les falaises dont la moyenne calculée est inférieur à la valeur spécifié par l'utilisateur dans les paramètres ###
    ######################################################################################################################################

    ######################### INUTILE #########################
    def drop_below_avg(self):


        # Enlever tout les pixels dont la valeur est inférieur à celle spécifié dans les paramètres
        print "Élimination des falaises avec une moyenne calculée de moins que %s" % str(self.slope_deg)
        self.falaises_data_rc[self.falaises_data < float(self.slope_deg)] = 0
        self.falaises_data_rc[numpy.isnan(self.falaises_data)] = 0


        self.write_gtiff("drop_below_avg.tif", self.falaises_data)
    ######################### INUTILE #########################






    def rasterize_water(self):

        print "Convertir le shapefile d'étendu d'eau en raster\n"
        self.input_water_shp = ogr.Open(self.input_water)
        self.input_water_shp_lyr = self.input_water_shp.GetLayer()

        temp_write_path = self.output_path + os.sep + 'water_rasterized.tif'
        self.water_rast_img = self.writeDriver.Create(temp_write_path, self.cols, self.rows, 1, GDT_Int32)

        self.water_rast_img.SetGeoTransform((self.input_geot[0], self.input_geot[1], self.input_geot[2], self.input_geot[3], self.input_geot[4], self.input_geot[5]))
        self.water_rast_img_band1 = self.water_rast_img.GetRasterBand(1)
        self.water_rast_img_band1.SetNoDataValue(0)



        # Écriture du raster à partir du shapefile
        gdal.RasterizeLayer(self.water_rast_img, [1], self.input_water_shp_lyr, burn_values=[1])

        self.water_rast_img.SetGeoTransform((self.input_geot[0], self.input_geot[1], self.input_geot[2], self.input_geot[3], self.input_geot[4], self.input_geot[5]))
        self.water_rast_img.SetProjection(self.input_prj)

        #
        self.water_data = self.water_rast_img_band1.ReadAsArray(0,0, self.cols, self.rows)








    def rasterize_wetland(self):

        print "Convertir le shapefile de milieu humide en raster\n"
        self.input_wetland_shp = ogr.Open(self.input_wetland)
        self.input_wetland_shp_lyr = self.input_wetland_shp.GetLayer()


        temp_write_path = self.output_path + os.sep + 'wetland_rasterized.tif'
        self.wetland_rast_img = self.writeDriver.Create(temp_write_path, self.cols, self.rows, 1, GDT_Int32)

        self.wetland_rast_img.SetGeoTransform((self.input_geot[0], self.input_geot[1], self.input_geot[2], self.input_geot[3], self.input_geot[4], self.input_geot[5]))
        self.wetland_rast_img_band1 = self.wetland_rast_img.GetRasterBand(1)
        self.wetland_rast_img_band1.SetNoDataValue(0)



        # Écriture du raster à partir du shapefile
        gdal.RasterizeLayer(self.wetland_rast_img, [1], self.input_wetland_shp_lyr, burn_values=[1])

        self.water_rast_img.SetGeoTransform((self.input_geot[0], self.input_geot[1], self.input_geot[2], self.input_geot[3], self.input_geot[4], self.input_geot[5]))
        self.water_rast_img.SetProjection(self.input_prj)

        #
        self.wetland_data = self.wetland_rast_img_band1.ReadAsArray(0,0, self.cols, self.rows)












    def calculate_slope_area(self):

        struct = [[1,1,1],
                  [1,1,1],
                  [1,1,1]]

        self.labeled_slope, self.num_slope = scipy.ndimage.measurements.label(self.falaises_data_rc, structure=struct)


        self.nb_pixel_slope = [ 0 for i in range(self.num_slope) ]

        print "Élimination des falaises dont la superficie est moins de %s pixels" % str(self.slope_area)
        # Remplir la matrice temporaire
        for i, value1 in enumerate(self.labeled_slope):
            for j, value2 in enumerate(value1):
                if value2 != 0:
                    # Ajouter un pixel a la liste du nombre de pixel par "label"
                    self.nb_pixel_slope[value2-1] = self.nb_pixel_slope[value2-1] + 1

        #print self.nb_pixel_slope


        self.falaises_area = self.falaises_data_rc

        for i, value in enumerate(self.labeled_slope):
            for j, value2 in enumerate(value):
                if value2 != 0:
                    if self.nb_pixel_slope[value2-1] >= int(self.slope_area): pass
                    else:
                        self.falaises_data_rc[i][j] = 0



        self.write_gtiff("calculate_slope_area.tif", self.falaises_data_rc)








    def calculate_water_area(self):

        struct = [[1,1,1],
                  [1,1,1],
                  [1,1,1]]

        self.labeled_water, self.num_water = scipy.ndimage.measurements.label(self.water_data, structure=struct)


        self.nb_pixel_water = [ 0 for i in range(self.num_water) ]

        print "Élimination des étendues d'eau dont la superficie est moins de %s pixels" % str(self.water_area)
        # Remplir la matrice temporaire
        for i, value1 in enumerate(self.labeled_water):
            for j, value2 in enumerate(value1):
                if value2 != 0:
                    # Ajouter un pixel a la liste du nombre de pixel par "label"
                    self.nb_pixel_water[value2-1] = self.nb_pixel_water[value2-1] + 1

        #print self.nb_pixel_water


        self.water_data_rc = self.water_data

        for i, value in enumerate(self.labeled_water):
            for j, value2 in enumerate(value):
                if value2 != 0:
                    if self.nb_pixel_water[value2-1] >= int(self.water_area): pass
                    else:
                        self.water_data_rc[i][j] = 0


        # # Threshold pour la superficie des étendues d'eau
        # self.water_data_rc[self.water_data_rc < float(self.water_area)] = 0
        # self.water_data_rc[numpy.isnan(self.water_data_rc)] = 0


        self.write_gtiff("calculate_water_area.tif", self.water_data_rc)








    def calculate_wetland_area(self):

        struct = [[1,1,1],
                  [1,1,1],
                  [1,1,1]]

        self.labeled_wetland, self.num_wetland = scipy.ndimage.measurements.label(self.wetland_data, structure=struct)


        self.nb_pixel_wetland = [ 0 for i in range(self.num_wetland) ]

        print "Élimination des milieux humides dont la superficie est moins de %s pixels" % str(self.wetland_area)
        # Remplir la matrice temporaire
        for i, value1 in enumerate(self.labeled_wetland):
            for j, value2 in enumerate(value1):
                if value2 != 0:
                    # Ajouter un pixel a la liste du nombre de pixel par "label"
                    self.nb_pixel_wetland[value2-1] = self.nb_pixel_wetland[value2-1] + 1

        #print self.nb_pixel_wetland

        self.wetland_data_rc = self.wetland_data

        for i, value in enumerate(self.labeled_water):
            for j, value2 in enumerate(value):
                if value2 != 0:
                    if self.nb_pixel_water[value2-1] >= int(self.water_area): pass
                    else:
                        self.water_data_rc[i][j] = 0


        # # Threshold pour la superficie des milieux humides
        # self.wetland_data_rc[self.wetland_data_rc < float(self.wetland_area)] = 0
        # self.wetland_data_rc[numpy.isnan(self.wetland_data_rc)] = 0

        self.write_gtiff("calculate_wetland_area.tif", self.wetland_data_rc)







    def write_gtiff(self, filename, array):
        print "Écriture du fichier '%s'\n" % str(filename)
        temp_write_path = self.output_path + os.sep + filename
        write_gtiff_img = self.writeDriver.Create(temp_write_path, self.cols, self.rows, 1, GDT_Int32)
        write_gtiff_img_band1 = write_gtiff_img.GetRasterBand(1)
        write_gtiff_img_band1.WriteArray(array, 0, 0)

        # Régler la projection et le GeoTranform du fichier écrit
        write_gtiff_img.SetProjection(self.input_prj)
        write_gtiff_img.SetGeoTransform((self.input_geot[0], self.input_geot[1], self.input_geot[2], self.input_geot[3], self.input_geot[4], self.input_geot[5]))







    def create_proximity_raster(self, input_type):

        # Valider si c'est wetland ou water et règle le chemin de sortie pour le raster qui sera créé.
        if (input_type == "wetland"):
            print "Création du raster de proximité wetland"
            temp_write_path = self.output_path + os.sep + 'create_prox_raster_wl.tif'
        if (input_type == "water"):
            print "Création du raster de proximité water"
            temp_write_path = self.output_path + os.sep + 'create_prox_raster_w.tif'


        proximity_img = self.writeDriver.Create(temp_write_path, self.cols, self.rows, 1, GDT_Float32)
        proximity_img.SetGeoTransform(self.input_geot)
        proximity_img.SetProjection(self.input_prj)
        proximity_img_band1 = proximity_img.GetRasterBand(1)

        # Retourne un raster du calcul de proximité
        self.water_rast_img_band1 = self.water_rast_img.GetRasterBand(1)
        if (input_type == "wetland"):
            gdal.ComputeProximity(self.wetland_rast_img_band1, proximity_img_band1, [])
        if (input_type == "water"):
            gdal.ComputeProximity(self.water_rast_img_band1, proximity_img_band1, [])

































    def manage_threshold_values(self):
        pass
        #
        # # Threshold pour l'inclinaison moyenne du cliff
        # print "Élimination des falaises avec une moyenne calculée de moins que %s" % str(self.slope_deg)
        # self.falaises_data_rc[self.falaises_data_rc < float(self.slope_deg)] = 0
        # self.falaises_data_rc[numpy.isnan(self.falaises_data_rc)] = 0
        #
        # # Threshold pour la superficie de la falaise
        # self.falaises_data_rc[self.falaises_data_rc < float(self.slope_area)] = 0
        # self.falaises_data_rc[numpy.isnan(self.falaises_data_rc)] = 0
        #
        # # Threshold pour la superficie des étendues d'eau
        # self.water_data_rc[self.water_data_rc < float(self.water_area)] = 0
        # self.water_data_rc[numpy.isnan(self.water_data_rc)] = 0
        #
        # # Threshold pour la superficie des milieux humides
        # self.wetland_data_rc[self.wetland_data_rc < float(self.wetland_area)] = 0
        # self.wetland_data_rc[numpy.isnan(self.wetland_data_rc)] = 0
        #

        #
        # for i, value in enumerate(self.input_data):
        #     for j, value2 in enumerate(value):
        #
        #         # Threshold pour l'inclinaison moyenne du cliff
        #         if (self.falaises_data_rc[i][j] >= float(self.slope_deg)): pass
        #         else: self.falaises_data_rc[i][j] = 0
        #
        #         # Threshold pour la superficie de la falaise
        #         if (self.nb_pixel_cliff[self.labeled_cliffs[i][j]-1] >= int(self.slope_area)): pass
        #         else:
        #             self.falaises_data_rc[i][j] = 0
        #
        #         # Threshold pour la superficie des étendues d'eau
        #         if (self.nb_pixel_water[self.labeled_water[i][j]-1] >= int(self.water_area)): pass
        #         else:
        #             self.water_data_rc[i][j] = 0
        #
        #
        #         # Threshold pour la superficie des milieux humides
        #         if (self.nb_pixel_wetland[self.labeled_wetland[i][j]-1] >= int(self.wetland_area)): pass
        #         else:
        #             self.wetland_data_rc[i][j] = 0









# Robustesse du validage en entrée du SRS
# Comment faire le in memory ??

































# ###################################################################################
# #####                        Détermination des falaises                       #####
# ###################################################################################
#
#
# # Ouverture du fichier de slopes en input
# input_slope = r'larouche_slopeq'
# input_ds = gdal.Open(input_slope)
#
# # Obtenir la projection de l'image
# input_prj = input_ds.GetProjection()
#
# # Informations sur la position de l'image input et de la taille des pixels
# input_ds_geo = input_ds.GetGeoTransform()
#
# # Nombre de colonnes et de rows de l'image en input
# cols = input_ds.RasterXSize
# rows = input_ds.RasterYSize
# print cols, rows
#
# # Gris
# band = input_ds.GetRasterBand(1)
#
# # Obtenir un array numpy à partir de la bande de gris
# input_data = band.ReadAsArray(0,0, cols, rows)
#
# # Création du fichier output
# driverOut = gdal.GetDriverByName("GTiff")
# image = driverOut.Create(r'image_out.tif', cols, rows, 1, GDT_Int32)
#
# # Définition des informations sur la position de l'image output et de la taille des pixels (information obtenue avec l'image input)
# image.SetGeoTransform((input_ds_geo[0], input_ds_geo[1], input_ds_geo[2], input_ds_geo[3], input_ds_geo[4], input_ds_geo[5]))
#
#
# falaises_data = input_data
#
# # Tout ce qui vaut plus de 40 prend la valeur 1
# for i, f in enumerate(input_data):
#     for j, g in enumerate(f):
#         if (g >= 30):
#             falaises_data[i][j] = 1
#         else:
#             falaises_data[i][j] = 0
#
#
# """
# # Écriture de l'image
# band = image.GetRasterBand(1)
# band.WriteArray(falaises_data, 0, 0)
#
# # Définition de la projection de l'image output (même projection que input)
# image.SetProjection(input_prj)
# """
#
# # Détermination de la grandeur de chaque falaise (par le nombre de pixel)
#
# struct = [[1,1,1],
#         [1,1,1],
#         [1,1,1]]
#
#
# labeled_array, num_features = scipy.ndimage.measurements.label(falaises_data, structure=struct)
#
# numb = [0 for i in range(num_features)]
#
# for i in labeled_array:
#     for j in i:
#         if (j != 0):
#             numb[j-1] = numb[j-1] + 1
#
#
# for i, label in enumerate(labeled_array):
#     for j, label2 in enumerate(label):
#         if (labeled_array[i][j] != 0):
#             if (numb[labeled_array[i][j]-1] > 4):
#                 labeled_array[i][j] = numb[label2-1]
#             else:
#                 labeled_array[i][j] = 0
#
#
# # Création du fichier output
# driverOut = gdal.GetDriverByName("GTiff")
# image = driverOut.Create(r'image_out_c.tif', cols, rows, 1, GDT_Int32)
#
# # Définition des informations sur la position de l'image output et de la taille des pixels (information obtenue avec l'image input)
# image.SetGeoTransform((input_ds_geo[0], input_ds_geo[1], input_ds_geo[2], input_ds_geo[3], input_ds_geo[4], input_ds_geo[5]))
#
# # Écriture de l'image
# band = image.GetRasterBand(1)
# band.WriteArray(labeled_array, 0, 0)
#
#
#
#
#
#
#
#
# ###################################################################################
# #####            Transformer un shapefile d'étendu d'eau en raster            #####
# ###################################################################################
#
#
#
# # Transformer un shapefile d'étendu d'eau en raster
#
# NoData_value = 0
#
# input_vector = ogr.Open(r'waterbody_2.shp')
# input_vector_layer = input_vector.GetLayer()
# x_min, x_max, y_min, y_max = input_vector_layer.GetExtent()
#
# x_res = int((x_max - x_min) / input_ds_geo[1])
# y_res = int((y_max - y_min) / input_ds_geo[5])
#
# v_driverOut = gdal.GetDriverByName("GTiff")
# v_image = v_driverOut.Create(r'rasterized.tif', cols, rows, 1, GDT_Int32)
#
# v_image.SetGeoTransform((input_ds_geo[0], input_ds_geo[1], input_ds_geo[2], input_ds_geo[3], input_ds_geo[4], input_ds_geo[5]))
# v_band = v_image.GetRasterBand(1)
# v_band.SetNoDataValue(NoData_value)
#
# # Écriture du raster à partir du shapefile
# gdal.RasterizeLayer(v_image, [1], input_vector_layer, burn_values=[100])
#
# # Array numpy de l'image rasterizé
# v_data = v_band.ReadAsArray(0,0, cols, rows)
#
# labeled_lakes, num_lakes = scipy.ndimage.measurements.label(v_data, structure=struct)
#
# numb2 = [0 for i in range(num_lakes)]
#
# for i in labeled_lakes:
#     for j in i:
#         if (j != 0):
#             numb2[j-1] = numb2[j-1] + 1
#
# print numb2
#
# # Pour garder les étendues d'eau de grandeur significatives
# labeled_lakes2 = labeled_lakes
# for i, label in enumerate(labeled_lakes):
#     for j, label2 in enumerate(label):
#         if label2 != 0:
#             if (numb2[label2-1] > 10):
#                 #print numb2[label2-1]
#                 labeled_lakes2[i][j] = 2
#             else:
#                 labeled_lakes2[i][j] = 0
#
#
# # Création du fichier output
# driverOut = gdal.GetDriverByName("GTiff")
# image = driverOut.Create(r'labeled_lakes2.tif', cols, rows, 1, GDT_Int32)
#
# # Définition des informations sur la position de l'image output et de la taille des pixels (information obtenue avec l'image input)
# image.SetGeoTransform((input_ds_geo[0], input_ds_geo[1], input_ds_geo[2], input_ds_geo[3], input_ds_geo[4], input_ds_geo[5]))
#
#
# # Écriture de l'image
# band = image.GetRasterBand(1)
# band.WriteArray(labeled_lakes2, 0, 0)
#
#
#
# prox_image = gdal.Open(r'proximity.tif')
# prox_band = prox_image.GetRasterBand(1)
# prox_data = prox_band.ReadAsArray(0,0, cols, rows)
#
# #print prox_data
#
#
# cliff_prox = labeled_array
#
# for i, label in enumerate(labeled_array):
#     for j, label2 in enumerate(label):
#         if (label2 != 0):
#             print label2
#             cliff_prox[i][j] = label2 * (prox_data.max() - prox_data[i][j])
#             #print cliff_prox[i][j]
#
#
# cliff_prox_img = driverOut.Create(r'cliff_prox.tif', cols, rows, 1, GDT_Float32)
# prox_band = cliff_prox_img.GetRasterBand(1)
# prox_band.WriteArray(cliff_prox, 0, 0)
# cliff_prox_img.SetGeoTransform((input_ds_geo[0], input_ds_geo[1], input_ds_geo[2], input_ds_geo[3], input_ds_geo[4], input_ds_geo[5]))
#
#
# """
# # Création d'un raster qui illustre la proximité de chaque plan d'eau.
#
#     #gdal.ComputeProximity( srcband, dstband, options, callback = prog_func )
#
# creation_options = []
# creation_type = 'Float32'
#
# dst_filename = 'proximity.tif'
#
# drv = gdal.GetDriverByName("GTiff")
# dst_ds = drv.Create( dst_filename, cols, rows, 1, GDT_Float32)
#
# dst_ds.SetGeoTransform(input_ds_geo)
# dst_ds.SetProjection(input_prj)
#
# dstband = dst_ds.GetRasterBand(1)
#
#
#
# gdal.ComputeProximity(v_band, dstband, [])
# """











# Calculer la moyenne de valeur des pixels dans la tache
# Calculer le centroid

# Vérifier la teinte de gris sous le centroid (qui est la distance à un point d'eau)
# Reclassifier les pixels selon les résultats obtenus
# Interpoler entre les centroids