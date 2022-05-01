# -*- coding: utf-8 -*-

# Author: Dale A Jackan
# Created on: 4.29.2022
# Updated on: 4.29.2022
# Email: dale.jackan@alamance-nc.com.com

"""
GPIN creator and Acreage Calculator

### Description ###
This python toolbox provides a gui interface for users to choose the feature class they are editing and will be creating GPINs for. The GPINs and acreages are only calculated for the selected features. This tool works regardless of whether you have editing turned on or off in ArcGIS Pro. When the GPINs are created they will be written to the feature records. At the end the tool will report warnings if the new GPINs match any existing GPINs and if so it will report back the object ID and GPIN of the feature that the newly created GPIN matches. In ArcGIS Pro there are no "true" edit sessions like in ArcMap where you have to specify the layer you are editing on. To reduce risk of mistakenly editing on a layer the user doesn't intend the user is asked to choose the feature class they are working on because the tool works regardless of whether or not the "edit button" is on or off. 

### limitations ###
This tool utilizes arcpy and therefore is subject to any update issues that may occur with it. The tool does not try to adapt and create a new GPIN if it finds that the GPIN already exists. The tool only reports a warning message that there is a match and what OBJECTID the new GPIN matches. However, this code can be adapted to do so if a process is agreed upon for iteratively creating the new GPINs when a match is found.

"""

import arcpy, os


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "GPIN and Acreage Toolbox"
        self.alias = "gpin_and_acreage"

        # List of tool classes associated with this toolbox
        self.tools = [gpin_acreage]


class gpin_acreage(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "GPIN and Acreage Tool"
        self.description = "Calculates GPINs and acreages for selected features"
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

        #getting the full catalog path to the selected feature class
        desc=arcpy.Describe(fc).catalogPath

        #the fc_noselect uses the feature layer to find it's referenced feature class and because the feature class doesn't store a selection set anything using this varirable
        # looks at the entire feature class and is not restricted by a selection set. 
        fc_noselect=str(desc)
        print(fc_noselect)
        s=""
        r=""
        f=0

        # Creating the Search cursor that utilizes the selection set of the feature layer to iterate through and expose the centroid and area values of the selected polygons
        cursor=arcpy.da.SearchCursor(fc,['SHAPE@TRUECENTROID','SHAPE@AREA'], spatial_reference=arcpy.SpatialReference(102719))

        noselect_list=[]
        repeat_dict={}

#The main loop for the code using an update cursor to make available the GPIN, OBJECTID, PID, and ACRES fields in a feature layer
        with arcpy.da.UpdateCursor(fc,['GPIN','OBJECTID','PID','ACRES']) as ucursor:
          for urow in ucursor:

            #The cursor created directly from the feature class and ignores any selection set
            cursor_noselect=arcpy.da.SearchCursor(fc_noselect, ['GPIN','OBJECTID'],spatial_reference=arcpy.SpatialReference(102719))

            #makes a list of all GPIN values and their associated OBJECTIDs
            noselect_list.append([v for v in cursor_noselect])

            #iterates over the search cursor selected set once for every iteration of the update cursor loop storing the Centroid coordinates and Area for that feature
            iter_cursor=cursor.next()
            z_set=""
            print(f)

            cursor_list=list(iter_cursor)
            print(cursor_list[0])

            #Takes the X and Y coordinates and creates subsets of their values
            sub_x=str(cursor_list[0][0])[1:6]
            print(sub_x)
            sub_y=str(cursor_list[0][1])[0:5]
            print(sub_y)

            f=f+1
            #Creates the new GPIN in z_set from the centroid X and Y value subsets
            for (x,y) in zip(sub_x,sub_y):
               z_set=z_set+(x+y)

            #checks to see if the GPIN is a repeat of any existing value in the feature class
            repeat_dict={i:z for z,i in noselect_list[0] if (z_set==z)}

            #Inserts the new calculated GPIN into the selected feature
            urow[0]=z_set
            print(urow[0])

            #Makes the ObjectID for the current selected feature available
            ob_id=urow[1]

            #Makes the PID for the current selected feature available
            ob_pid=urow[2]

            #Converts the area from square feet to Acres
            area=cursor_list[1]/43560

            #Inserts the new area value and rounds the value
            urow[3]=round(area,6)

            #A message to notify the user what GPIN and area was calculated for which PID
            s+=f'The parcel:{ob_pid}\'s GPIN was updated to {urow[0]} with an area of {round(area,6)} Acres. \n'

            #Writes or updates to the feature class
            ucursor.updateRow(urow)

        #creates a python dictionary of OBJECTID:GPIN pairs where the newly create GPIN already exists in the feature class. If there is nothing there will be nothing in the variable
        for k,v in repeat_dict.items():
	        r+=f'The parcel with OBJECTID: {k} and GPIN: {v} has already been assigned this GPIN. \n'

        #Reports to the geoprocessing tool messgages the results from the "s" variable    
        messages.addMessage(s)

        #Reports to the geoprocessing tool as a warning the values from "r" showing where the repeat GPINs are
        messages.addWarningMessage(r)

        print(s)
        print(r)
        print("\nScript completed!")
        return