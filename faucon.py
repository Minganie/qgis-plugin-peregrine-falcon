# -*- coding: utf-8 -*-


# Spécification des chemins de l'interpreteur et des librairies sous windows
###### Vérifier si le OS est Windows
import sys,os
sys.path.append(r'C:\OSGeo4W64\apps\Python27\Lib\site-packages')
os.environ['PATH'] = r'C:\OSGeo4W64\bin'


from osgeo import gdal, ogr
from gdalconst import *
import numpy
import scipy.ndimage


class peregrineFalcon:

    input_raster = ""
    input_water = ""
    output_path = ""
    slope_area = ""
    water_area = ""
    units = ""
    slope_deg = ""
    falaises_data = []



    def __init__(self, input_raster, input_water, output_path, slope_area, water_area, units, slope_deg):
        self.input_raster = input_raster
        self.input_water = input_water
        self.output_path = output_path
        self.slope_area = slope_area
        self.water_area = water_area
        self.units = units
        self.slope_deg = slope_deg
        print "Plugin PeregrineFalcon"





    def open_input_raster(self):
        self.input_ds = gdal.Open(self.input_raster)





    def get_raster_spatial_ref(self):
        """print self.input_raster
        print self.input_water
        print self.output_path
        print self.slope_area
        print self.water_area
        print self.units
        print self.slope_deg"""

        if self.input_ds != None:
            # Obtenir la projection de l'image
            self.input_prj = self.input_ds.GetProjection()

            # Informations sur la position de l'image input et de la taille des pixels
            self.input_geot = self.input_ds.GetGeoTransform()

            # Nombre de colonnes et de rows de l'image en input
            self.cols = self.input_ds.RasterXSize
            self.rows = self.input_ds.RasterYSize
            print self.cols, self.rows
        else:
            print "Can't open file %s" % self.input_raster





    def input_raster_data(self):
        input_raster_band1 = self.input_ds.GetRasterBand(1)
        temp = input_raster_band1.ReadAsArray(0,0, self.cols, self.rows)

        return input_raster_band1.ReadAsArray(0,0, self.cols, self.rows)






    def calculate_cliff_area(self):
        pass





    def dem_to_slopes(self):
        pass




    # Identifier les pentes dont l'inclinaison (dedgrés) est plus élevée que le paramètre spécifié
    def identify_cliffs(self):
        self.falaises_data, input_data = self.input_raster_data(), self.input_raster_data()



        #labeled_array, num_features = scipy.ndimage.measurements.label(self.falaises_data, structure=struct)

        ##print falaises_data.min(), falaises_data.max()


        # # Tout ce qui vaut moins de 40 prend la valeur 1
        for i, f in enumerate(input_data):
            for j, g in enumerate(f):
                if (g >= float(self.slope_deg)): pass
                else: self.falaises_data[i][j] = 0

        writeDriver = gdal.GetDriverByName('GTiff')
        identify_cliff_img = writeDriver.Create(r'/home/prototron/temp/identify_cliffs.tif', self.cols, self.rows, 1, GDT_Int32)
        identify_cliff_img_band1 = identify_cliff_img.GetRasterBand(1)
        identify_cliff_img_band1.WriteArray(self.falaises_data, 0, 0)


        #labeled_array, num_features = scipy.ndimage.measurements.label(input_data, structure=struct)
        # hist, bin_edges = numpy.histogram(falaises_data, falaises_data.max())
        # print hist
        # print bin_edges

    def calculate_slope_avg(self):

        struct = [[1,1,1],
                  [1,1,1],
                  [1,1,1]]

        labeled_array, num_features = scipy.ndimage.measurements.label(self.falaises_data, structure=struct)

        tmp_avg_slope = [ [""] for i in range(num_features)]
        avg_slope = [ 0.0 for i in range(num_features)]

        print tmp_avg_slope
        tmp_list = []

        for i, value1 in enumerate(labeled_array):
            for j, value2 in enumerate(value1):
                if value2 != 0:
                    #print value2-1
                    tmp_avg_slope[value2-1].append(self.falaises_data[i][j])

        print tmp_avg_slope
        for i, value in enumerate(tmp_avg_slope):
            total = 0
            for j in value:
                if (j != ''):
                    total = total + j
                    avg_slope[i] = total / len(value)

        print avg_slope

        #print labeled_array
        #print num_features

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