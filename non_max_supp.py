# -*- coding: utf-8 -*-

import getopt
import sys
from scipy import ndimage
import numpy as np
from numpy import ndenumerate
import gdal, ogr
import os


class NonMaxSupp:

    def __init__(self, cliff_patches):

        print "Entering NonMaxSupp"
        source = gdal.Open(self.cliff_patches)  #c'est qoi input?
        grey = np.array(source.GetRasterBand(1).ReadAsArray())
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
        if os.path.exists(r"E:\INFO\S5 - H2016\GMQ580\qgis-plugin-peregrine-falcon\out_data\cliffs.shp"):
            driver.DeleteDataSource(r"E:\INFO\S5 - H2016\GMQ580\qgis-plugin-peregrine-falcon\out_data\cliffs.shp")
        shapeData = driver.CreateDataSource(r"E:\INFO\S5 - H2016\GMQ580\qgis-plugin-peregrine-falcon\out_data\cliffs.shp")

        out_layer = shapeData.CreateLayer("cliffs", geom_type=ogr.wkbPoint)

        # Write projection file
        spatial_ref = source.GetProjection()
        file_handle = open(r"E:\INFO\S5 - H2016\GMQ580\qgis-plugin-peregrine-falcon\out_data\cliffs.prj", 'w')
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


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], '')
    except:
        pass
    n = NonMaxSupp(args[0])

if __name__ == '__main__':
    main()