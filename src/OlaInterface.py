"""
/***************************************************************************
UploadActivity
A QGIS plugin
Upload activity to OLA platform
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

# Import the PyQt and QGIS libraries
from ActivityRequestManager import ActivityRequestManager
from OlaInterfaceDialog import OlaInterfaceDialog
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from StakeholderRequestManager import StakeholderRequestManager
from qgis.core import *
from qgis.gui import *
import resources_rc

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class OlaInterface(QObject):
    
    def __init__(self, iface):
        QObject.__init__(self)

        # Save reference to the QGIS interface
        self.iface = iface
        # Reference to the QGIS map canvas
        self.canvas = iface.mapCanvas()
        

    def initGui(self):
        """
        Creates the necessary actions
        """
        # Create an action to start capturing polygons and add it to the digitize toolbar
        icon = QIcon()
        icon.addPixmap(QPixmap(_fromUtf8(":/plugins/olainterface/lo-logo.png")), QIcon.Normal, QIcon.Off)
        self.openDialogAction = QAction(icon, QString("Land Observatory"), self.iface.mainWindow())
        self.iface.pluginToolBar().addAction(self.openDialogAction)

        # Connect to signals for button behaviour
        self.connect(self.openDialogAction, SIGNAL("triggered()"), self.openDialog)
        

    def unload(self):
        """
        Remove the plugin menu item and icon from the toolbar
        """
        self.iface.pluginToolBar().removeAction(self.openDialogAction)

    def openDialog(self):
        """
        Open the main interface dialog
        """

        #file = QFile(":/settings.ini")
        #file.open(QIODevice.ReadOnly)
        #print file.fileName()

        #activityRequestManager = ActivityRequestManager("http://localhost:6543", "admin", "admin")
        #stakeholderRequestManager = StakeholderRequestManager("http://localhost:6543", "admin", "admin")
        
        dialog = OlaInterfaceDialog(self.iface) #, activityRequestManager=activityRequestManager, stakeholderRequestManager=stakeholderRequestManager)
        #activityRequestManager.setLogger(dialog.getLogger())
        #stakeholderRequestManager.setLogger(dialog.getLogger())
        dialog.show()
        dialog.exec_()

def formOpen(dialog, layerid, featureid):

    layer = QgsMapLayerRegistry.instance().mapLayer(layerid)
    feature = QgsFeature()
    layer.featureAtId(featureid, feature)
    attributeMap = feature.attributeMap()
    uuid = attributeMap[0].toString()
    activityRequestManager = ActivityRequestManager("http://localhost:6543", "admin", "admin")
    #activityRequestManager.getActivityById(uuid)
    activityRequestManager.getActivityById("746fba11-5fbe-453a-86a3-5fb1005e90a0")

    dialog.hide()
    new_dialog = Ui_Dialog()
    new_dialog.setupUi(QDialog())