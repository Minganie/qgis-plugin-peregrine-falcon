# -*- coding: utf-8 -*-

import rasterio
import getopt
import sys
from qgis.core import *


class SlopeOrientation:

    def __init__(self, dem):
        print "Entering SlopeOrientation"
        with rasterio.drivers():
            with rasterio.open(dem) as src:
                grey = src.read()[0]
                #ALGORITHM: Aspect
	# INPUT <ParameterRaster>
	# BAND <ParameterNumber>
	# COMPUTE_EDGES <ParameterBoolean>
	# ZEVENBERGEN <ParameterBoolean>
	# TRIG_ANGLE <ParameterBoolean>
	# ZERO_FLAT <ParameterBoolean>
	# OUTPUT <OutputRaster>

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], '')
    except:
        pass
    n = SlopeOrientation(args[0])

if __name__ == '__main__':
    main()