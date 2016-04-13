# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PeregrineFalcon
                                 A QGIS plugin
 A tool to help identify potential habitats for the Peregrine Falcon in Northern American
                             -------------------
        begin                : 2016-04-12
        copyright            : (C) 2016 by Myriam Luce, Patrice Pineault
        email                : Myriam.Luce@USherbrooke.ca, patrice.pineault@usherbrooke.ca
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PeregrineFalcon class from file PeregrineFalcon.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .peregrinefalcon import PeregrineFalcon
    return PeregrineFalcon(iface)
