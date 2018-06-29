# Copyright:   (c) David Enterprises Inc. 
# ArcGIS Version:   10.3
# Python Version:   2.7
#
# Course: GEOS 455 - Assignment 3: Advanced Python
#
# Purpose: This script is for Part B: Adds the provided datasets, and outputs from Part A to an already-created
#          map document (MXD file). The map, once saved programmatically, is then exported to a PDF of the same name. 
#
#
# References: Python 2.7 Documentation (https://docs.python.org/2/)
#             ArcPy Documentation (http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy/what-is-arcpy-.htm)
#             ArcPy Template for Geoprocessing (https://blogs.esri.com/esri/arcgis/2011/08/04/pythontemplate/)
#--------------------------------------------------------------------------------------------------------------

import os
import sys
import arcpy

def do_partB(workspace):
    """As parameters, this function takes the workspace (geodatabase); updates the current MXD document, and outputs a PDF in the same folder it is located"""
    try:
        #======This function adds feature classes in a workspace to a map document, and saves the layers as .lyr files; also exports the layout as PDF======

        # Get user parameters
        # ArcMap document location (arcpy.mapping.MapDocument)
        # Workspace containing features to be added 
        # Output location for PDF export

        # =- INITIALIZE & ENVIRONMENT SETTINGS-----------------------------------
        #  - Initialize
        output_path = os.path.dirname(workspace)
        mxd = arcpy.mapping.MapDocument("CURRENT")
        arcpy.AddMessage('Retrieving data frames from: ' + mxd.filePath)
        #    Data Frame
        data_frame = arcpy.mapping.ListDataFrames(mxd)[0]
        add_position = 'AUTO_ARRANGE'
        #    Legend
        legend = arcpy.mapping.ListLayoutElements(mxd, "LEGEND_ELEMENT", "Legend")[0]
        legend_items = ['Research_areas', 'Roads', 'Affected_areas', 'Park_boundary']

        #  - Environment Settings
        arcpy.env.workspace = workspace
        arcpy.env.ScratchWorkspace = workspace
        arcpy.env.overwriteOutput = True
        
        
        
        # =- MAIN LOOP ----------------------------------------------------------
        arcpy.AddMessage('Starting main loop...')
        for feature_classes in arcpy.ListFeatureClasses():
            # - Legend Prep
            if feature_classes in legend_items:
                legend.autoAdd = True
                arcpy.AddMessage('Add to legend: True')
            else:
                legend.autoAdd = False
                arcpy.AddMessage('Add to legend: False')


            
            # - Make Feature Layer
            temp_layer = output_path + os.sep + feature_classes + '.lyr' 
            arcpy.MakeFeatureLayer_management (feature_classes, temp_layer)
            arcpy.AddMessage('feature layer created ' + temp_layer)

            # - Save to Layer File
            out_layer = output_path + os.sep + feature_classes + '_p.lyr'
            arcpy.AddMessage('Saving layer: ' + out_layer)
            arcpy.SaveToLayerFile_management (temp_layer, out_layer)
            arcpy.AddMessage('Feature layer saved as: ' + out_layer)
            
            # - Add Layer to Map Document        
            arcpy.AddMessage('Data frame retrieved: ' + data_frame.name)
            arcpy.AddMessage('Adding layer to: ' + data_frame.name)
            add_layer = arcpy.mapping.Layer(out_layer)
            arcpy.mapping.AddLayer (data_frame, add_layer, add_position)
            arcpy.AddMessage('Feature layer added to document')

            del add_layer

        #  - End Main Loop-------------------------------------------------------

        # =- UPDATE VIEW --------------------------------------------------------
        arcpy.AddMessage('Refreshing document...')
        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()
        data_frame.zoomToSelectedFeatures()

        
        # =- SAVE MAP DOCUMENT ---------------------------------------------------
        mxd.save()
        arcpy.AddMessage('Document saved: ' + mxd.filePath)


        # =- EXPORT PDF ----------------------------------------------------------
        out_pdf = mxd.filePath[:-4] + '.pdf'
        arcpy.mapping.ExportToPDF(mxd, out_pdf)
        arcpy.AddMessage('PDF Exported to: ' + out_pdf)


        # =- CLEANUP -------------------------------------------------------------
        
        del data_frame
        del mxd
        
        pass
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
    except Exception as e:
        print e.args[0]
# End do_partB function
 
# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE, 
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    # Arguments are optional
    argv = tuple(arcpy.GetParameterAsText(i)
        for i in range(arcpy.GetArgumentCount()))
    do_partB(*argv)

