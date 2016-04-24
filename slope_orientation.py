# -*- coding: utf-8 -*-

import getopt
import sys
import processing


class SlopeOrientation:

    def __init__(self, dem, out_layer):
        print "Entering SlopeOrientation"

        #ALGORITHM: Aspect
            # INPUT <ParameterRaster>
            # BAND <ParameterNumber>
            # COMPUTE_EDGES <ParameterBoolean>
            # ZEVENBERGEN <ParameterBoolean>
            # TRIG_ANGLE <ParameterBoolean>
            # ZERO_FLAT <ParameterBoolean>
            # OUTPUT <OutputRaster>
        processing.runalg("gdalogr:aspect", dem, 1, False, False, False, False, out_layer)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], '')
    except:
        pass
    n = SlopeOrientation(args[0])

if __name__ == '__main__':
    main()