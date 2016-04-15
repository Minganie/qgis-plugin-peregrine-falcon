# -*- coding: utf-8 -*-

import fiona
import rasterio
import getopt
import sys
from scipy import ndimage
from numpy import ndenumerate


class NonMaxSupp:

    def __init__(self, cliff_patches):
        print "Entering nonMaxSupp"
        with rasterio.drivers():
            with rasterio.open(cliff_patches) as src:
                grey = src.read()[0]
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

                coordinates = []
                for point in points:
                    point = point[::-1]
                    coordinates.append(src.affine*point)

                schema = {'geometry': 'Point', 'properties': {}}
                record = {'geometry': {'coordinates': (0,0), 'type': 'Point'},
                          'id': '1',
                          'properties': {}}
                with fiona.open("cliffs.shp", 'w', driver='ESRI Shapefile', crs=src.crs, schema=schema) as c:
                    for coord in coordinates:
                        print(len(c))
                        record['geometry']['coordinates'] = coord
                        c.write(record)
                        print(len(c))

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], '')
    except:
        pass
    n = NonMaxSupp(args[0])

if __name__ == '__main__':
    main()