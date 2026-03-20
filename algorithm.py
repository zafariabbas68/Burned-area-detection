# === FILE: algorithm/__init__.py ===
"""
Algorithm module for burned area detection
"""

from .burned_area_detector import BurnedAreaDetectorAlgorithm
from .spectral_indices import SpectralIndices
from .fuzzy_membership import FuzzyMembership
from .region_growing import RegionGrowing
from .validation import ValidationTools

__all__ = [
    'BurnedAreaDetectorAlgorithm',
    'SpectralIndices',
    'FuzzyMembership',
    'RegionGrowing',
    'ValidationTools'
]

# === FILE: algorithm/burned_area_detector.py ===
"""
Main algorithm orchestrator
"""

import numpy as np
from osgeo import gdal
import os
from qgis.PyQt.QtCore import QObject, pyqtSignal

from .spectral_indices import SpectralIndices
from .fuzzy_membership import FuzzyMembership
from .region_growing import RegionGrowing
from .validation import ValidationTools


class BurnedAreaDetectorAlgorithm(QObject):
    """
    Main algorithm class that orchestrates the entire burned area detection process
    Based on the fuzzy logic algorithm from CNR-IREA (Sali et al., 2021)
    """

    # Signals for GUI updates
    progressUpdated = pyqtSignal(int)
    statusUpdated = pyqtSignal(str)

    def __init__(self, parameters=None):
        """
        Initialize algorithm with parameters

        Args:
            parameters: dict with algorithm parameters
        """
        super().__init__()

        # Default parameters
        self.parameters = {
            'seed_threshold': 0.9,  # Region growing seed threshold
            'grow_threshold': 0.1,  # Region growing expansion threshold
            'mask_clouds': True,  # Mask cloud pixels
            'mask_water': True,  # Mask water pixels
            'mask_snow': True,  # Mask snow/ice pixels
            'use_ndvi': True,  # Include NDVI in analysis
            'use_nbr': True,  # Include NBR in analysis
            'use_red_edge': True,  # Include red-edge bands
            'owa_operator': 'and',  # OWA operator type
            'max_iterations': 50  # Maximum region growing iterations
        }

        # Override with user parameters
        if parameters:
            self.parameters.update(parameters)

        # Initialize components
        self.spectral_indices = SpectralIndices()
        self.fuzzy_membership = FuzzyMembership()
        self.region_growing = RegionGrowing()
        self.validation = ValidationTools()

        # State variables
        self.pre_ds = None
        self.post_ds = None
        self.mask = None
        self.burned_prob = None
        self.burned_map = None

    def detect_burned_area(self, pre_path, post_path, output_path):
        """
        Main detection pipeline

        Args:
            pre_path: Path to pre-fire Sentinel-2 image
            post_path: Path to post-fire Sentinel-2 image
            output_path: Path to save output

        Returns:
            Path to output burned area map
        """
        try:
            # Step 1: Load and validate images
            self.statusUpdated.emit("Loading satellite imagery...")
            self.progressUpdated.emit(10)
            self._load_images(pre_path, post_path)

            # Step 2: Extract and validate bands
            self.statusUpdated.emit("Extracting spectral bands...")
            self.progressUpdated.emit(20)
            bands = self._extract_bands()

            # Step 3: Calculate spectral indices
            self.statusUpdated.emit("Calculating spectral indices...")
            self.progressUpdated.emit(30)
            indices = self._calculate_spectral_indices(bands)

            # Step 4: Compute membership degrees
            self.statusUpdated.emit("Computing fuzzy membership...")
            self.progressUpdated.emit(40)
            membership = self._compute_membership(indices)

            # Step 5: Apply OWA aggregation
            self.statusUpdated.emit("Applying OWA aggregation...")
            self.progressUpdated.emit(50)
            burned_prob = self._owa_aggregation(membership)

            # Step 6: Region growing segmentation
            self.statusUpdated.emit("Applying region growing...")
            self.progressUpdated.emit(70)
            burned_map = self._region_growing(burned_prob)

            # Step 7: Apply masks
            self.statusUpdated.emit("Applying masks...")
            self.progressUpdated.emit(85)
            burned_map = self._apply_masks(burned_map)

            # Step 8: Save output
            self.statusUpdated.emit("Saving results...")
            self.progressUpdated.emit(95)
            self._save_output(burned_map, output_path)

            # Step 9: Calculate statistics
            self.statusUpdated.emit("Calculating statistics...")
            self.progressUpdated.emit(100)
            stats = self._calculate_statistics(burned_map)

            self.statusUpdated.emit(f"Detection complete! Burned area: {stats['burned_pixels']} pixels")

            return output_path

        except Exception as e:
            self.statusUpdated.emit(f"Error: {str(e)}")
            raise

    def _load_images(self, pre_path, post_path):
        """
        Load and validate input images
        """
        self.pre_ds = gdal.Open(pre_path)
        self.post_ds = gdal.Open(post_path)

        if not self.pre_ds or not self.post_ds:
            raise Exception("Could not open input images")

        # Check if images have same dimensions
        pre_width = self.pre_ds.RasterXSize
        pre_height = self.pre_ds.RasterYSize
        post_width = self.post_ds.RasterXSize
        post_height = self.post_ds.RasterYSize

        if pre_width != post_width or pre_height != post_height:
            raise Exception("Images must have the same dimensions")

        # Check projections
        pre_proj = self.pre_ds.GetProjection()
        post_proj = self.post_ds.GetProjection()

        if pre_proj != post_proj:
            raise Exception("Images must have the same projection")

    def _extract_bands(self):
        """
        Extract Sentinel-2 bands with proper handling

        Returns:
            dict: Dictionary of band arrays
        """
        bands = {}

        # Sentinel-2 band mapping for Level-2A products
        band_mapping = {
            'blue': 2,  # Band 2: Blue (490 nm)
            'green': 3,  # Band 3: Green (560 nm)
            'red': 4,  # Band 4: Red (665 nm)
            'red_edge_1': 5,  # Band 5: Red Edge 1 (705 nm)
            'red_edge_2': 6,  # Band 6: Red Edge 2 (740 nm)
            'red_edge_3': 7,  # Band 7: Red Edge 3 (783 nm)
            'nir': 8,  # Band 8: NIR (842 nm)
            'nir_narrow': 8,  # Band 8A: Narrow NIR (865 nm) - optional
            'swir_1': 11,  # Band 11: SWIR 1 (1610 nm)
            'swir_2': 12,  # Band 12: SWIR 2 (2190 nm)
            'scl': 0  # Scene Classification Layer (if available)
        }

        # Extract each band
        for band_name, band_num in band_mapping.items():
            try:
                # Check if band exists
                if band_num <= self.pre_ds.RasterCount:
                    pre_band = self.pre_ds.GetRasterBand(band_num)
                    post_band = self.post_ds.GetRasterBand(band_num)

                    # Read as float array
                    pre_array = pre_band.ReadAsArray().astype(np.float32)
                    post_array = post_band.ReadAsArray().astype(np.float32)

                    # Handle NoData values
                    nodata = pre_band.GetNoDataValue()
                    if nodata is not None:
                        pre_array[pre_array == nodata] = np.nan
                        post_array[post_array == nodata] = np.nan

                    bands[band_name] = {
                        'pre': pre_array,
                        'post': post_array
                    }
            except Exception as e:
                self.statusUpdated.emit(f"Warning: Could not extract band {band_name}: {e}")

        # Validate required bands
        required_bands = ['red', 'nir', 'swir_2']
        for band in required_bands:
            if band not in bands:
                raise Exception(f"Required band {band} not found in input images")

        return bands

    def _calculate_spectral_indices(self, bands):
        """
        Calculate spectral indices for burned area detection

        Returns:
            dict: Dictionary of spectral indices
        """
        indices = {}

        # NDVI - Normalized Difference Vegetation Index
        if self.parameters.get('use_ndvi', True):
            pre_ndvi = self.spectral_indices.ndvi(
                bands['nir']['pre'], bands['red']['pre']
            )
            post_ndvi = self.spectral_indices.ndvi(
                bands['nir']['post'], bands['red']['post']
            )
            indices['dndvi'] = pre_ndvi - post_ndvi

        # NBR - Normalized Burn Ratio
        if self.parameters.get('use_nbr', True):
            pre_nbr = self.spectral_indices.nbr(
                bands['nir']['pre'], bands['swir_2']['pre']
            )
            post_nbr = self.spectral_indices.nbr(
                bands['nir']['post'], bands['swir_2']['post']
            )
            indices['dnbr'] = pre_nbr - post_nbr

        # Red Edge indices (if available)
        if self.parameters.get('use_red_edge', True) and 'red_edge_2' in bands:
            pre_red_edge = self.spectral_indices.red_edge_index(
                bands['nir']['pre'], bands['red_edge_2']['pre']
            )
            post_red_edge = self.spectral_indices.red_edge_index(
                bands['nir']['post'], bands['red_edge_2']['post']
            )
            indices['dredge'] = pre_red_edge - post_red_edge

        return indices

    def _compute_membership(self, indices):
        """
        Compute fuzzy membership degrees for each evidence

        Returns:
            list: List of membership degree arrays
        """
        membership_arrays = []

        for key, array in indices.items():
            # Apply sigmoid membership function
            membership = self.fuzzy_membership.sigmoid(
                array,
                x0=self._get_threshold(key, array),
                k=self._get_slope(key, array),
                shape='s' if self._is_increasing(key) else 'z'
            )
            membership_arrays.append(membership)

        return membership_arrays

    def _owa_aggregation(self, membership_arrays):
        """
        Apply Ordered Weighted Averaging (OWA) aggregation

        Args:
            membership_arrays: List of membership degree arrays

        Returns:
            np.array: Aggregated burned probability
        """
        # Stack arrays for sorting
        stacked = np.stack(membership_arrays, axis=2)

        # Sort in descending order along the evidence axis
        sorted_vals = np.sort(stacked, axis=2)[:, :, ::-1]

        # Apply OWA weights based on operator
        if self.parameters['owa_operator'] == 'and':
            # Minimum (conservative - reduces commission errors)
            weights = np.zeros(len(membership_arrays))
            weights[-1] = 1.0

        elif self.parameters['owa_operator'] == 'or':
            # Maximum (aggressive - reduces omission errors)
            weights = np.zeros(len(membership_arrays))
            weights[0] = 1.0

        elif self.parameters['owa_operator'] == 'average':
            # Average (balanced)
            weights = np.ones(len(membership_arrays)) / len(membership_arrays)

        elif self.parameters['owa_operator'] == 'almost_and':
            # Weighted towards minimum
            weights = np.ones(len(membership_arrays)) * 0.1
            weights[-2] = 0.5
            weights[-1] = 0.4

        else:  # almost_or
            # Weighted towards maximum
            weights = np.ones(len(membership_arrays)) * 0.1
            weights[0] = 0.4
            weights[1] = 0.5

        # Apply weights
        aggregated = np.sum(sorted_vals * weights, axis=2)

        return aggregated

    def _region_growing(self, burned_prob):
        """
        Apply region growing algorithm to refine burned areas

        Args:
            burned_prob: Burned probability map (0-1)

        Returns:
            np.array: Binary burned area map (0 or 1)
        """
        seed_threshold = self.parameters['seed_threshold']
        grow_threshold = self.parameters['grow_threshold']
        max_iterations = self.parameters['max_iterations']

        return self.region_growing.apply(
            burned_prob,
            seed_threshold=seed_threshold,
            grow_threshold=grow_threshold,
            max_iterations=max_iterations
        )

    def _apply_masks(self, burned_map):
        """
        Apply cloud, water, and snow masks

        Args:
            burned_map: Binary burned area map

        Returns:
            np.array: Masked burned area map
        """
        # Initialize mask array (0 = valid, 1 = masked)
        mask = np.zeros_like(burned_map, dtype=np.uint8)

        # Try to get SCL band (Scene Classification Layer)
        if 'scl' in self._extract_bands():
            scl = self._extract_bands()['scl']['post']

            # Apply cloud mask
            if self.parameters.get('mask_clouds', True):
                # Cloud classes in SCL: 8=medium probability, 9=high probability
                cloud_mask = (scl == 8) | (scl == 9)
                mask[cloud_mask] = 1

            # Apply water mask
            if self.parameters.get('mask_water', True):
                # Water class in SCL: 6
                water_mask = (scl == 6)
                mask[water_mask] = 1

            # Apply snow/ice mask
            if self.parameters.get('mask_snow', True):
                # Snow class in SCL: 11
                snow_mask = (scl == 11)
                mask[snow_mask] = 1

        # Apply mask to burned map (set masked pixels to 255)
        burned_map_masked = burned_map.copy()
        burned_map_masked[mask == 1] = 255

        return burned_map_masked

    def _save_output(self, burned_map, output_path):
        """
        Save burned area map to GeoTIFF
        """
        driver = gdal.GetDriverByName('GTiff')
        out_ds = driver.Create(
            output_path,
            burned_map.shape[1],
            burned_map.shape[0],
            1,
            gdal.GDT_Byte
        )

        # Copy georeferencing from input
        out_ds.SetGeoTransform(self.pre_ds.GetGeoTransform())
        out_ds.SetProjection(self.pre_ds.GetProjection())

        # Write data
        out_band = out_ds.GetRasterBand(1)
        out_band.WriteArray(burned_map)
        out_band.SetNoDataValue(255)

        # Add metadata
        out_band.SetDescription("Burned Area Map: 1=Burned, 0=Unburned, 255=Masked")

        out_ds.FlushCache()
        out_ds = None

    def _calculate_statistics(self, burned_map):
        """
        Calculate basic statistics of the burned area map
        """
        total_pixels = burned_map.size
        burned_pixels = np.sum(burned_map == 1)
        unburned_pixels = np.sum(burned_map == 0)
        masked_pixels = np.sum(burned_map == 255)

        return {
            'total_pixels': total_pixels,
            'burned_pixels': burned_pixels,
            'unburned_pixels': unburned_pixels,
            'masked_pixels': masked_pixels,
            'burned_percentage': (burned_pixels / (total_pixels - masked_pixels)) * 100
        }

    def _get_threshold(self, key, array):
        """Get membership function threshold for specific index"""
        # Based on empirical thresholds from literature
        thresholds = {
            'dnbr': 0.2,
            'dndvi': 0.15,
            'dredge': 0.1
        }
        return thresholds.get(key, 0.1)

    def _get_slope(self, key, array):
        """Get membership function slope for specific index"""
        slopes = {
            'dnbr': 10.0,
            'dndvi': 12.0,
            'dredge': 8.0
        }
        return slopes.get(key, 10.0)

    def _is_increasing(self, key):
        """Determine if membership function should be increasing or decreasing"""
        increasing_indices = ['dnbr', 'dndvi', 'dredge']
        return key in increasing_indices