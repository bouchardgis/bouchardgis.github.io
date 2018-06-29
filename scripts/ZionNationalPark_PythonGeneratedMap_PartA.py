# Copyright:   (c) David Enterprises Inc. 
# ArcGIS Version:   10.3
# Python Version:   2.7
#
# Course: GEOS 455 - Assignment 3: Advanced Python
#
# Purpose: This script takes input features that may be impacted by impacting features (input),
#          and outputs a feature class including the input features that would be impacted within
#          a buffer of the impacting features. 
#
#
# References: Python 2.7 Documentation (https://docs.python.org/2/)
#             ArcPy Documentation (http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy/what-is-arcpy-.htm)
#             ArcPy Template for Geoprocessing (https://blogs.esri.com/esri/arcgis/2011/08/04/pythontemplate/)
#             Extra help with Update Cursor use from:
#                                       http://gis.stackexchange.com/questions/130588/python-script-to-add-fields-to-feature-classes
#--------------------------------------------------------------------------------------------------------------


import os
import sys
import arcpy

def do_partA(workspace, roads, research_areas, buffer_distance, output_feature):
    """This function takes input roads, buffers an area around them, selects the intersecting research areas and outputs them, and their area in acres"""
    try:
        # =- INPUTS ------------------------------------------------------------
        #Get user parameters - these are retrieved as inputs to the function:
        #Workspace - to save a bunch of issues; scratch will be set here as well
        #Roads feature class (impacting features)
        #Research areas feature class (features of concern)
        #Output feature class (impacted features)
        #Buffer distance (default 200m)
        # = Inputs should be retrieved

        # =- INITIALIZE LOCAL VARIABLES & ENV SETTINGS ----------------------------------------
        #  - Local Vars
        output_buffer = workspace + os.sep + 'output_buffer'

        #  - Environment Settings
        arcpy.env.workspace = workspace
        arcpy.env.scratchworkspace = workspace

        
        # =- Execute Buffer (200m)
        arcpy.Buffer_analysis (roads, output_buffer, buffer_distance, 'FULL', 'ROUND', 'ALL', "", 'PLANAR')
        arcpy.AddMessage('Road Buffer created')
        

        # =- Create Feature Layer of buffer
        #  - Initialize Output Layers
        buffer_layer = output_buffer + '_layer'
        research_areas_layer = research_areas + '_layer'
        
        #  - Make Feature layer for roads buffer
        arcpy.MakeFeatureLayer_management (output_buffer, buffer_layer)
        
        #  - Make Feature layer for research areas
        arcpy.MakeFeatureLayer_management (research_areas, research_areas_layer)
        arcpy.AddMessage('Layers Created')
        

        # =-Select by location: whatever features fall within buffer
        #  - Initialize parameters
        overlap_type = 'INTERSECT'
        select_features = buffer_layer
        search_distance = ''
        selection_type = 'NEW_SELECTION'
        invert_spatial_relationship = 'NOT_INVERT'

        #  - Execute Select Layer By Location
        arcpy.SelectLayerByLocation_management (research_areas_layer, overlap_type, select_features, search_distance, selection_type, invert_spatial_relationship)


        # =- Output feature class from selected features
        arcpy.CopyFeatures_management (research_areas_layer, output_feature)
        

        # =- Use an Update Cursor to determine the AREA of IMPACTED FEATURES (convert to acres, or just use AREA field)
        arcpy.AddField_management(output_feature, "Area_Acres", "DOUBLE")
        with arcpy.da.UpdateCursor(output_feature, ["Area_Acres", "AREA"]) as cursor:
            for row in cursor:
                row[0] = row[1]/4046.86
                cursor.updateRow(row)

        # =- Cleanup
        del output_buffer
        
        pass
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
    except Exception as e:
        print e.args[0]
# End do_analysis function
 
# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE, 
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    # Arguments are optional
    argv = tuple(arcpy.GetParameterAsText(i)
        for i in range(arcpy.GetArgumentCount()))
    do_partA(*argv)

