
# -*- coding: utf-8 -*-

# Author: Dale A Jackan
# Created on: 2.24.2020
# Updated on: 2.25.2020
# Email: djackan@hotmail.com

"""
GDAL Raster File Converter Python Toolbox for ArcGIS Pro

### Description ###
This python toolbox provides a gui interface for users to interact with the
GDAL raster conversion functions. The user needs to specify the folder where the file(s) are
and then either enter the file name with file extension, or just enter the file extension (.tif).
If the user chooses to enter just the extension then all files in the folder that are rasters with that
extension will be converted. The user also needs to choose the output file type and folder. The
files are automatically named with the same name as the old file with the new extension added. The toolbox does not
offer to browse for the files because there are file types that GDAL can convert that ArcGIS Pro will not let you see
using their interface, one such example is the ".e00" file extension.

### limitations ###
The conversions are only as good as those that GDAL can perform. The rasters that can be converted
are limited to those the GDAL drivers can read and create: https://gdal.org/drivers/raster/index.html
Not all GDAL drivers have full functionality. At the time of creation this script used the following
environmental packages:
1. gdal 2.3.3
2. python 3.6.9
3. ArcGIS Pro 2.5

"""

import arcpy
from osgeo import gdal
from osgeo import ogr
import os
import gdal


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [GDAL_raster_file_converter]


class GDAL_raster_file_converter(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "GDAL Raster File Converter"
        self.description = "uses GDAL to convert raster files"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
        displayName="Input Folder:",
        name="input_folder",
        datatype="DEFolder",
        parameterType="Required",
        direction="Input")

        """for gathering the GDAL raster read driver list (not used at this time)"""
        # the code below creates a list of the driver names, but the driver names are not the same as the file extensions
        #driver_list = []
        #for name in range(gdal.GetDriverCount()):
        #    driver = gdal.GetDriver(name)
        #    driver_list.append(driver.GetDescription())

        # a pick list of all raster file extensions readable by GDAL could be created and used below
        param1 = arcpy.Parameter(
        displayName="Enter the file name with extension, or just the extension (i.e. .tif) in order to batch convert that file type from input folder:",
        name="input_file_type",
        datatype="GPString",
        parameterType="Required",
        direction="Input")

        """the GDAL driver list for all raster read drivers"""
        # param1.filter.list= sorted(driver_list)

        param2 = arcpy.Parameter(
        displayName="Choose output Folder:",
        name="output_folder",
        datatype="DEFolder",
        parameterType="Required",
        direction="Input")

        param3 = arcpy.Parameter(
        displayName="Choose output File Type:",
        name="output_file_type",
        datatype="GPString",
        parameterType="Required",
        direction="Input")

        """list of gdal raster creation drivers"""
        param3.filter.list = sorted(['ADRG', 'ARG', 'BMP', 'BT', 'BYN', 'CTable2', 'DB2', 'ECW', 'EHdr', 'ELAS', 'ENVI', 'ERS', 'EXR', 'FITS', 'GeoRaster', 'GPKG', 'GS7BG', 'GSBG', 'GTiff', 'HDF4', 'HFA', 'IDA', 'RST', 'ILWIS', 'INGR', 'ISCE', 'ISIS2', 'ISIS3', 'JP2ECW', 'KEA', 'KRO', 'Leveller', 'MRF', 'MBTiles', 'MEM', 'MFF', 'MFF2', 'netCDF', 'NITF', 'NTv2', 'NWT_GRD', 'NWT_GRC', 'PAux', 'PCIDSK', 'PCRaster', 'PDS4', 'RMF', 'ROI_PAC', 'RRASTER', 'SAGA', 'SGI', 'Terragen', 'TileDB', 'USGSDEM', 'VICAR', 'VRT'])

        params = [param0, param1, param2, param3]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        src_folder = parameters[0].valueAsText
        input_format = parameters[1].valueAsText
        outpath = parameters[2].valueAsText
        output_format = parameters[3].valueAsText

        for filename in os.listdir(src_folder):

            if input_format in filename:
                src_file = gdal.OpenEx("{0}\{1}".format(src_folder, filename), 0)
                if src_file.RasterCount >= 1:
                    driver = gdal.GetDriverByName(output_format)
                    basenamesplit = filename.split(".")
                    basename = basenamesplit[0]
                    output_file = "{0}\{1}.tif".format(outpath, basename)

                    driver.CreateCopy(output_file, src_file, 0)

        print("\nScript completed!")
        return
