"""
/***************************************************************************
lo-editor
A QGIS plugin to add and edit spatial information to land deals on the Land
Observatory platform.
This script initializes the plugin, making it known to QGIS.
                             -------------------
begin                : 2012-04-05 Holy Thursday
copyright            : (C) 2012 by Adrian Weber
email                : adrian.weber@cde.unibe.ch 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

def name(): 
    return "Land Observatory Editor"
def description():
    return "A plugin to add and edit spatial information to land deals on the Land Observatory platform"
def version(): 
    return "Version 0.1"
def icon():
    return "lo-logo.png"
def qgisMinimumVersion():
    return "1.8"
def classFactory(iface): 
    from OlaInterface import OlaInterface
    return OlaInterface(iface)


