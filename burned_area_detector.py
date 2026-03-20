"""
Main plugin class for Burned Area Detector
"""

import os
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject, QgsMessageLog, Qgis, QgsRasterLayer

from .burned_area_detector_dialog import BurnedAreaDetectorDialog


class BurnedAreaDetector:
    """Main plugin class"""
    
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.dialog = None
        self.action = None
        
    def initGui(self):
        """Called when plugin is loaded"""
        icon_path = os.path.join(self.plugin_dir, 'images', 'icon.png')
        self.action = QAction(
            QIcon(icon_path) if os.path.exists(icon_path) else QIcon(),
            'Burned Area Detector',
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu('&Burned Area Detector', self.action)
        
    def unload(self):
        """Called when plugin is unloaded"""
        self.iface.removePluginMenu('&Burned Area Detector', self.action)
        self.iface.removeToolBarIcon(self.action)
        
    def run(self):
        """Main entry point"""
        self.dialog = BurnedAreaDetectorDialog(self.iface)
        self.dialog.show()
        if self.dialog.exec_():
            self.process()
    
    def process(self):
        """Process the burned area detection"""
        try:
            pre_layer = self.dialog.get_pre_fire_layer()
            post_layer = self.dialog.get_post_fire_layer()
            output_path = self.dialog.get_output_path()
            
            if not pre_layer or not post_layer:
                self.iface.messageBar().pushMessage(
                    "Error", "Please select both layers", level=Qgis.Critical, duration=5
                )
                return
            
            if not output_path:
                self.iface.messageBar().pushMessage(
                    "Error", "Please specify output path", level=Qgis.Critical, duration=5
                )
                return
            
            from .algorithm import BurnedAreaDetectorAlgorithm
            
            algorithm = BurnedAreaDetectorAlgorithm()
            algorithm.mask_clouds = self.dialog.get_mask_clouds()
            algorithm.mask_water = self.dialog.get_mask_water()
            algorithm.seed_threshold = self.dialog.get_seed_threshold()
            algorithm.grow_threshold = self.dialog.get_grow_threshold()
            
            self.iface.messageBar().pushMessage(
                "Processing", "Detecting burned areas...", level=Qgis.Info, duration=0
            )
            
            result_path = algorithm.detect_burned_area(
                pre_layer.source(),
                post_layer.source(),
                output_path
            )
            
            if os.path.exists(result_path):
                layer = QgsRasterLayer(result_path, "Burned Area Map")
                if layer.isValid():
                    QgsProject.instance().addMapLayer(layer)
            
            self.iface.messageBar().pushMessage(
                "Success", "Detection completed!", level=Qgis.Success, duration=5
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QgsMessageLog.logMessage(str(e), "BAD", Qgis.Critical)
            self.iface.messageBar().pushMessage(
                "Error", str(e), level=Qgis.Critical, duration=10
            )
