# -*- coding: utf-8 -*-


# Spécification des chemins de l'interpreteur et des librairies sous windows
###### Vérifier si le OS est Windows


import gdal, ogr
from gdalconst import *
import numpy
from scipy import ndimage
import scipy.stats
import os
from numpy import ndenumerate
import processing

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


    def set_gdal_driver(self):
        self.writeDriver = gdal.GetDriverByName('GTiff')
        self.communications.write_qgis_logs("info", u"GDAL Driver = GTiff")



    # Ouverture du Slope raster fait à partir de slope_to_dem()
    def open_input_dem(self):
        self.input_ds = gdal.Open(self.input_dem)
        self.communications.write_qgis_logs("info", u"Ouverture du raster %s" % self.input_dem)



    def get_input_data(self):
        self.communications.show_message("info", u"Obtenir une matrice du raster en entrée")
        input_raster_band1 = self.input_ds.GetRasterBand(1)
        self.input_data = input_raster_band1.ReadAsArray(0,0, self.cols, self.rows)




    ####################################################################
    ### Obtenir la projection et le geotransform du raster en entrée ###
    ####################################################################

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

            # Extent
            minx = self.input_geot[0]
            maxy = self.input_geot[3]
            maxx = minx + self.input_geot[1]*self.cols
            miny = maxy + self.input_geot[5]*self.rows


            self.communications.show_message("info", u"Taille de l'image:" + str(self.cols) + " x " + str(self.rows))

            self.communications.write_qgis_logs("info", u"Extent du raster input: " + str(minx) + " " + str(maxy) + " " + str(maxx) + " " + str(miny))
        else:
            self.communications.show_message("critical", "Impossible d'ouvrir le fichier '%s'" % self.input_dem)





    # def get_coordinate_from_xy(self, x, y):
    #     minx = self.input_geot[0]
    #     maxy = self.input_geot[3]
    #     cordx = minx + self.input_geot[1]*x
    #     cordy = maxy + self.input_geot[5]*y
    #     print cordx, cordy





    ##################################################
    ### Obtenir un array numpy du raster en entrée ###
    ##################################################

    def input_raster_data(self):
        self.communications.show_message("info", u"Obtenir un array numpy du raster en entrée\n")
        input_raster_band1 = self.input_ds.GetRasterBand(1)

        return input_raster_band1.ReadAsArray(0,0, self.cols, self.rows)







    def dem_to_slopes(self):
        print "Entering SlopeOrientation"

        self.slope = self.output_path + os.sep + "slope.tif"
        #ALGORITHM: Aspect
            # INPUT <ParameterRaster>
            # BAND <ParameterNumber>
            # COMPUTE_EDGES <ParameterBoolean>
            # ZEVENBERGEN <ParameterBoolean>
            # TRIG_ANGLE <ParameterBoolean>
            # ZERO_FLAT <ParameterBoolean>
            # OUTPUT <OutputRaster>
        processing.runalg("gdalogr:slope", self.input_dem, 1, False, False, False, 1, self.slope)
        self.get_slopes_data()




    def get_slopes_data(self):
        self.input_slopes = gdal.Open(self.slope)
        self.communications.write_qgis_logs("info", u"Ouverture du raster %s" % self.slope)
        slopes_band1 = self.input_slopes.GetRasterBand(1)

        self.slopes_data = slopes_band1.ReadAsArray(0,0, self.cols, self.rows)
        del self.input_slopes





    def dem_to_aspect(self):
        print "Entering SlopeOrientation"

        self.aspect = self.output_path + os.sep + "aspect.tif"
        #ALGORITHM: Aspect
            # INPUT <ParameterRaster>
            # BAND <ParameterNumber>
            # COMPUTE_EDGES <ParameterBoolean>
            # ZEVENBERGEN <ParameterBoolean>
            # TRIG_ANGLE <ParameterBoolean>
            # ZERO_FLAT <ParameterBoolean>
            # OUTPUT <OutputRaster>
        processing.runalg("gdalogr:aspect", self.input_dem, 1, False, False, False, False, self.aspect)
        self.get_aspect_data()



    def get_aspect_data(self):
        self.input_aspect = gdal.Open(self.aspect)
        self.communications.write_qgis_logs("info", u"Ouverture du raster %s" % self.aspect)
        aspect_band1 = self.input_aspect.GetRasterBand(1)

        self.aspect_data = aspect_band1.ReadAsArray(0,0, self.cols, self.rows)




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


    ####################################################################################################
    ### Identifier les pentes dont l'inclinaison (dedgrés) est plus élevée que le paramètre spécifié ###
    ####################################################################################################

    def identify_cliffs(self):
        self.falaises_data = self.slopes_data

        # Enlever tout les pixels dont la valeur est inférieur à celle spécifié dans les paramètres
        self.communications.show_message("info", u"Élimination des pixels inférieur à %s" % str(self.slope_deg))
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
        self.communications.show_message("info", u"Identification des pixels contigus à partir des falaises identifiées")
        self.labeled_cliffs, self.num_cliffs = scipy.ndimage.measurements.label(self.falaises_data, structure=struct)



        # Matrice pour stocker le nombre de pixels par "label"
        self.nb_pixel_cliff = [ 0 for i in range(self.num_cliffs) ]


        # Calculer la moyenne d'inclinaison de chaque cliffs
        hist1, bin_edges1 = numpy.histogram(self.labeled_cliffs, bins=self.num_cliffs)

        hist2, bin_edges2 = numpy.histogram(self.labeled_cliffs, weights=self.falaises_data, bins=self.num_cliffs)


        avg_slope = []
        for i, j in enumerate(hist2):
            avg_slope.append(j / hist1[i])
        avg_slope[0] = 0



        # Reclassification de la matrice de falaise
        self.communications.show_message("info", u"Reclassification de la matrice de falaise")
        self.falaises_data_rc = self.falaises_data


        for i, value in enumerate(self.labeled_cliffs):

            for j, value2 in enumerate(value):
               # print avg_slope[value2-1]
                if value2 != 0:
                    self.falaises_data_rc[i][j] = avg_slope[value2-1]
                else:
                    self.falaises_data_rc[i][j] = 0




        self.write_gtiff("identify_cliffs_rc.tif", self.falaises_data_rc)









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












    def calculate_slope_area(self):

        struct = [[1,1,1],
                  [1,1,1],
                  [1,1,1]]

        self.labeled_slope, self.num_slope = scipy.ndimage.measurements.label(self.falaises_data_rc, structure=struct)


        self.nb_pixel_slope = [ 0 for i in range(self.num_slope) ]

        self.communications.show_message("info", u"Élimination des falaises dont la superficie est inférieure à %s pixels" % str(self.slope_area))

        # Remplir la matrice temporaire
        for i, value1 in enumerate(self.labeled_slope):
            for j, value2 in enumerate(value1):
                if value2 != 0:
                    # Ajouter un pixel a la liste du nombre de pixel par "label"
                    self.nb_pixel_slope[value2-1] = self.nb_pixel_slope[value2-1] + 1




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

        self.communications.show_message("info", u"Élimination des étendues d'eau dont la superficie est inférieure à %s pixels" % str(self.water_area))
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


        self.write_gtiff("calculate_water_area.tif", self.water_data_rc)








    def calculate_wetland_area(self):

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

        #print self.nb_pixel_wetland

        self.wetland_data_rc = self.wetland_data

        for i, value in enumerate(self.labeled_water):
            for j, value2 in enumerate(value):
                if value2 != 0:
                    if self.nb_pixel_water[value2-1] >= int(self.water_area): pass
                    else:
                        self.water_data_rc[i][j] = 0




        self.write_gtiff("calculate_wetland_area.tif", self.wetland_data_rc)







    def write_gtiff(self, filename, array):
        self.communications.show_message("info", u"Écriture du fichier '%s'\n" % str(filename))
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
            self.communications.show_message("info", u"Création du raster de proximité wetland")
            temp_write_path = self.output_path + os.sep + 'create_prox_raster_wl.tif'
        if (input_type == "water"):
            self.communications.show_message("info", u"Création du raster de proximité water")
            temp_write_path = self.output_path + os.sep + 'create_prox_raster_w.tif'


        proximity_img = self.writeDriver.Create(temp_write_path, self.cols, self.rows, 1, GDT_Float32)
        proximity_img.SetGeoTransform(self.input_geot)
        proximity_img.SetProjection(self.input_prj)
        proximity_img_band1 = proximity_img.GetRasterBand(1)

        # Retourne un raster du calcul de proximité
        self.water_rast_img_band1 = self.water_rast_img.GetRasterBand(1)
        if (input_type == "wetland"):
            gdal.ComputeProximity(self.wetland_rast_img_band1, proximity_img_band1, [])
            self.wetland_prox_data = proximity_img_band1.ReadAsArray(0,0, self.cols, self.rows)
        if (input_type == "water"):
            gdal.ComputeProximity(self.water_rast_img_band1, proximity_img_band1, [])
            self.waterland_prox_data = proximity_img_band1.ReadAsArray(0,0, self.cols, self.rows)







    def results_calculation(self):
        self.results_raster = self.aspect_data * self.falaises_data * self.wetland_prox_data * self.waterland_prox_data / 10000
        self.write_gtiff("raster_output.tif", self.results_raster)





    def non_max_sup(self):

        self.communications.show_message("info", "Générer le shapefile de points à partir des falaises")
        source = gdal.Open(self.output_path + os.sep + "raster_output.tif")
        grey = numpy.array(source.GetRasterBand(1).ReadAsArray())
        points = []

        s = [[1, 1, 1],
             [1, 1, 1],
             [1, 1, 1]]

        labeled_array, num_features = ndimage.measurements.label(grey, structure=s)
        slices = ndimage.find_objects(labeled_array)
        print "Found", num_features, "cliff patches in file"

        for i, slice in enumerate(slices):
            if not i % 10:
                print "Treating patch", i
            patch = grey[slice]
            if len(patch) > 1:
                ij = [ij for ij, val in ndenumerate(patch) if val == max(patch.flatten())]
                ij = ij[0]
                points.append([ij[0]+slice[0].start+0.5, ij[1]+slice[1].start+0.5])
            else:
                points.append([slice[0].start+0.5, slice[1].start+0.5])

        driver = ogr.GetDriverByName("ESRI Shapefile")
        if os.path.exists(self.output_path + os.sep + "cliffs.shp"):
            driver.DeleteDataSource(self.output_path + os.sep + "cliffs.shp")
        shapeData = driver.CreateDataSource(self.output_path + os.sep + "cliffs.shp")

        out_layer = shapeData.CreateLayer("cliffs", geom_type=ogr.wkbPoint)

        # Write projection file
        spatial_ref = source.GetProjection()
        file_handle = open(self.output_path + os.sep + "cliffs.prj", 'w')
        file_handle.write(spatial_ref)
        file_handle.close()

        affine = source.GetGeoTransform()

        # Write each point
        for point in points:
            point = point[::-1]
            x = affine[0] + affine[1]*point[0] + affine[2]*point[1]
            y = affine[3] + affine[4]*point[0] + affine[5]*point[1]

            out_feat = ogr.Feature(out_layer.GetLayerDefn())

            geometry = ogr.Geometry(ogr.wkbPoint)
            geometry.SetPoint(0, x, y)

            out_feat.SetGeometry(geometry)
            out_layer.CreateFeature(out_feat)
            # Flush changes to disk
            out_layer.SyncToDisk()






    def add_results_to_qgis(self):
        self.iface.addRasterLayer(self.output_path + os.sep + "raster_output.tif", "raster_output")
        self.iface.addVectorLayer(self.output_path + os.sep + "cliffs.shp", "cliffs_points", "ogr")


# Comment faire le in memory ??
    #memory layer

#module qgis



