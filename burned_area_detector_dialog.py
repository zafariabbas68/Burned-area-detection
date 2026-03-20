"""
Dialog class for Burned Area Detector plugin
"""

import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QMessageBox
from qgis.core import QgsMapLayerProxyModel

# Try to load the compiled UI, fallback to direct loading
ui_file = os.path.join(os.path.dirname(__file__), 'burned_area_detector_dialog_base.ui')
FORM_CLASS, _ = uic.loadUiType(ui_file)


class BurnedAreaDetectorDialog(QDialog, FORM_CLASS):
    """Dialog for user input"""
    
    def __init__(self, iface, parent=None):
        super(BurnedAreaDetectorDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        
        # Set up layer selection - only show raster layers
        self.preFireLayerComboBox.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.postFireLayerComboBox.setFilters(QgsMapLayerProxyModel.RasterLayer)
        
        # Connect buttons
        self.outputFilePushButton.clicked.connect(self.select_output_file)
        self.helpPushButton.clicked.connect(self.show_help)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        # Set default values
        self.seedThresholdDoubleSpinBox.setValue(0.9)
        self.growThresholdDoubleSpinBox.setValue(0.1)
    
    def select_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Output", "", "GeoTIFF Files (*.tif *.tiff)"
        )
        if file_path:
            if not file_path.endswith(('.tif', '.tiff')):
                file_path += '.tif'
            self.outputLineEdit.setText(file_path)
    
    def get_pre_fire_layer(self):
        return self.preFireLayerComboBox.currentLayer()
    
    def get_post_fire_layer(self):
        return self.postFireLayerComboBox.currentLayer()
    
    def get_output_path(self):
        return self.outputLineEdit.text()
    
    def get_mask_clouds(self):
        return self.maskCloudsCheckBox.isChecked()
    
    def get_mask_water(self):
        return self.maskWaterCheckBox.isChecked()
    
    def get_seed_threshold(self):
        return self.seedThresholdDoubleSpinBox.value()
    
    def get_grow_threshold(self):
        return self.growThresholdDoubleSpinBox.value()
    
    def show_help(self):
        help_text = """
        <h3>Burned Area Detector Help</h3>
        
        <p><b>How to use:</b></p>
        <ol>
            <li>Select a pre-fire Sentinel-2 image (before the fire)</li>
            <li>Select a post-fire Sentinel-2 image (after the fire)</li>
            <li>Choose an output path for the result</li>
            <li>Adjust optional parameters if needed</li>
            <li>Click OK to run the detection</li>
        </ol>
        
        <p><b>Output:</b></p>
        <p>The plugin generates a burned area map where:
            <ul>
                <li><b>Value 1</b>: Burned area</li>
                <li><b>Value 0</b>: Unburned area</li>
                <li><b>Value 255</b>: No data / masked</li>
            </ul>
        </p>
        """
        QMessageBox.information(self, "Help", help_text)
