"""
QGIS Plugin Architecture Pattern
Based on MVC (Model-View-Controller) Pattern
"""

# === FILE: __init__.py ===
"""
Plugin Entry Point - Controller Layer
"""
import os
import sys
from qgis.core import QgsApplication
from .burned_area_detector import BurnedAreaDetector


def classFactory(iface):
    """
    QGIS entry point - creates plugin instance

    Args:
        iface: QGIS interface object (QgisInterface)

    Returns:
        BurnedAreaDetector: Plugin instance
    """
    return BurnedAreaDetector(iface)


# === FILE: burned_area_detector.py ===
"""
Main Plugin Class - Controller Layer
"""
import os
import traceback
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QProgressBar
from qgis.core import QgsProject, QgsMessageLog, Qgis, QgsRasterLayer
from qgis.gui import QgsMessageBar

from .gui.burned_area_dialog import BurnedAreaDialog
from .algorithm.burned_area_detector import BurnedAreaDetectorAlgorithm
from .utils.logger import PluginLogger


class BurnedAreaDetector:
    """
    Main plugin controller class
    Manages plugin lifecycle and coordinates between GUI and Algorithm
    """

    def __init__(self, iface):
        """
        Initialize plugin controller

        Args:
            iface: QGIS interface instance
        """
        # Core references
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        # Initialize components
        self.logger = PluginLogger(self.plugin_dir)
        self.dialog = None
        self.algorithm = None
        self.actions = []

        # Initialize locale for internationalization
        self._init_locale()

        self.logger.info("Plugin initialized successfully")

    def _init_locale(self):
        """Initialize translation support"""
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n', f'bad_{locale}.qm')

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        """
        Called when plugin is loaded
        Creates GUI elements (toolbar icon, menu items)
        """
        # Create toolbar action
        icon_path = os.path.join(self.plugin_dir, 'resources', 'icons', 'icon.png')
        action = QAction(
            QIcon(icon_path) if os.path.exists(icon_path) else QIcon(),
            'Burned Area Detector',
            self.iface.mainWindow()
        )
        action.setWhatsThis('Detect burned areas from Sentinel-2 imagery')
        action.setStatusTip('Detect burned areas using fuzzy logic and region growing')
        action.triggered.connect(self.run)

        # Add to toolbar and menu
        self.iface.addToolBarIcon(action)
        self.iface.addPluginToMenu('&Burned Area Detector', action)
        self.actions.append(action)

        self.logger.info("Plugin GUI initialized")

    def unload(self):
        """
        Called when plugin is unloaded
        Cleans up GUI elements
        """
        for action in self.actions:
            self.iface.removePluginMenu('&Burned Area Detector', action)
            self.iface.removeToolBarIcon(action)

        self.logger.info("Plugin unloaded")

    def run(self):
        """
        Main entry point when plugin icon is clicked
        """
        try:
            # Create and show dialog
            self.dialog = BurnedAreaDialog(self.iface)
            self.dialog.show()

            # Execute dialog and process if accepted
            if self.dialog.exec_():
                self._process()

        except Exception as e:
            self.logger.error(f"Error in run: {str(e)}")
            self.iface.messageBar().pushMessage(
                "Error",
                f"Failed to open plugin: {str(e)}",
                level=Qgis.Critical,
                duration=10
            )

    def _process(self):
        """
        Process burned area detection
        """
        try:
            # Get user inputs from dialog
            pre_fire_layer = self.dialog.get_pre_fire_layer()
            post_fire_layer = self.dialog.get_post_fire_layer()
            output_path = self.dialog.get_output_path()
            parameters = self.dialog.get_parameters()

            # Validate inputs
            if not pre_fire_layer or not post_fire_layer:
                self.iface.messageBar().pushMessage(
                    "Error",
                    "Please select both pre-fire and post-fire images",
                    level=Qgis.Critical,
                    duration=5
                )
                return

            if not output_path:
                self.iface.messageBar().pushMessage(
                    "Error",
                    "Please specify output file path",
                    level=Qgis.Critical,
                    duration=5
                )
                return

            # Show progress bar
            progress = QgsMessageBar().createMessage("Processing...")
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress.layout().addWidget(progress_bar)
            self.iface.messageBar().pushWidget(progress, Qgis.Info)

            # Initialize algorithm
            self.algorithm = BurnedAreaDetectorAlgorithm(parameters)

            # Connect signals for progress updates
            self.algorithm.progressUpdated.connect(
                lambda value: progress_bar.setValue(value)
            )
            self.algorithm.statusUpdated.connect(
                lambda msg: self.iface.messageBar().pushMessage(
                    "Info", msg, level=Qgis.Info, duration=0
                )
            )

            # Run algorithm
            result_path = self.algorithm.detect_burned_area(
                pre_fire_layer.source(),
                post_fire_layer.source(),
                output_path
            )

            # Clear progress bar
            self.iface.messageBar().clearWidgets()

            # Add result to map
            if os.path.exists(result_path):
                result_layer = QgsRasterLayer(result_path, "Burned Area Map")
                if result_layer.isValid():
                    QgsProject.instance().addMapLayer(result_layer)

                    # Zoom to layer
                    self.iface.setActiveLayer(result_layer)
                    self.iface.zoomToActiveLayer()

            # Show success message
            self.iface.messageBar().pushMessage(
                "Success",
                f"Burned area detection completed!\nResult saved to: {result_path}",
                level=Qgis.Success,
                duration=10
            )

            self.logger.info(f"Processing completed successfully: {result_path}")

        except Exception as e:
            self.logger.error(f"Processing error: {str(e)}")
            self.iface.messageBar().clearWidgets()
            self.iface.messageBar().pushMessage(
                "Error",
                f"Processing failed: {str(e)}",
                level=Qgis.Critical,
                duration=10
            )