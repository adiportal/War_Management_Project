import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from qgis.core import *
from qgis.gui import *
import os
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = r'C:\OSGeo4W64\apps\Qt5\plugins'
os.environ['PATH'] += r';C:\OSGeo4W64\apps\qgis\bin;C:\OSGeo4W64\apps\Qt5\bin'
from PyQt5 import QtGui, QtCore, QtWidgets


app = QtGui.QGuiApplication([])
# QgsApplication.setPrefixPath("C:/OSGeo4W64/apps/qgis", True)
# QgsApplication.initQgis()
#
# window = QtWidgets.QMainWindow
# window_frame = QtWidgets.QFrame(window)
# window.setCentralWidget(window_frame)
# frame_layout = QtWidgets.QGridLayout(window_frame)
#
# canvas = QgsMapCanvas()
# frame_layout.addWidget(canvas)
#
# map = "C:\OSGeo4W64\ISRAEL_MAP.mbtiles"
# layer = QgsRasterLayer(map, "raster")
# canvas_layer = QgsMapLayerActionRegistry(layer)
# canvas.setLayers([canvas_layer])
# canvas.zoomToFullExtent()
#
#
# window.show()
# app.exec_()


# app = QApplication(sys.argv)

window = QMainWindow()
window.show() # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec_()
