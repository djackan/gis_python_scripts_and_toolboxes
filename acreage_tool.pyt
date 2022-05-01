# -*- coding: utf-8 -*-

# Author: Dale A Jackan
# Created on: 4.29.2022
# Updated on: 4.29.2022
# Email: dale.jackan@alamance-nc.com.com

"""
Acreage Tool

### Description ###
This python toolbox provides a gui interface for users to choose the feature class they are editing and will calculate a new acreage for the selected features.

### limitations ###
This tool utilizes arcpy and therefore is subject to any update issues that may occur with it. This tool only converts the square foot area values to acreage and inserts the new values into the "ACRES" field.

"""

import arcpy, os


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Acreage Toolbox"
        self.alias = "acreage_tool"

        # List of tool classes associated with this toolbox
        self.tools = [acreage_tool]


class acreage_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Acreage Tool"
        self.description = "Calculates acreages for selected features"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
        displayName="Features Class you are editing:",
        name="input_feature_class",
        datatype="GPFeatureLayer",
        parameterType="Required",
        direction="Input")
        params=[param0]
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
        #fc exposes the feature layer which references a feature class. The "layer" has the selection set
        fc=parameters[0].ValueAsText
        s=""
        f=0

        # Creating the Search cursor that utilizes the selection set of the feature layer to iterate through and expose the centroid and area values of the selected polygons
        cursor=arcpy.da.SearchCursor(fc,['SHAPE@AREA'], spatial_reference=arcpy.SpatialReference(102719))

#The main loop for the code using an update cursor to make available the GPIN, OBJECTID, PID, and ACRES fields in a feature layer
        with arcpy.da.UpdateCursor(fc,['GPIN','OBJECTID','PID','ACRES']) as ucursor:
          for urow in ucursor:

            #iterates over the search cursor selected set once for every iteration of the update cursor loop storing the Centroid coordinates and Area for that feature
            iter_cursor=cursor.next()
            print(f)

            cursor_list=list(iter_cursor)
            print(cursor_list[0])

            f=f+1
            #Makes the ObjectID for the current selected feature available
            ob_id=urow[1]

            #Makes the PID for the current selected feature available
            ob_pid=urow[2]

            #Converts the area from square feet to Acres
            area=cursor_list[0]/43560

            #Inserts the new area value and rounds the value
            urow[3]=round(area,6)

            #A message to notify the user what GPIN and area was calculated for which PID
            s+=f'The parcel:{ob_pid}\'s area was updated to {round(area,6)} Acres. \n'

            #Writes or updates to the feature class
            ucursor.updateRow(urow)

        #Reports to the geoprocessing tool messgages the results from the "s" variable    
        messages.addMessage(s)

        print(s)
        print("\nScript completed!")
        return