# 
# ArcGIS Version:   10.3
# Python Version:   2.7
#
# Purpose: Creates DSM for solar radiation simulation use. 
#
#
# References: Python 2.7 Documentation (https://docs.python.org/2/)
#             ArcPy Documentation (http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy/what-is-arcpy-.htm)
#             ArcPy Template for Geoprocessing (https://blogs.esri.com/esri/arcgis/2011/08/04/pythontemplate/)
#--------------------------------------------------------------------------------------------------------------
import os
import sys
import arcpy
def LASToDSM_Conversion(input_workspace, output_raster, coordinate_system, tile_index, cell_size, output_layer):
    """TODO: Add documentation about this function here"""
    try:

        # Local Variables

        class_codes = [2,5,6] # Class Codes for surfaces (reduces noise)
        return_values = ['1'] # The desired return value for surfaces (just the first returns)
        output_las_dataset = input_workspace + "\\LASDataset"

        arcpy.env.workspace = input_workspace
        arcpy.env.scratchWorkspace = input_workspace

        #FeatureClasses = arcpy.ListFeatureClasses()

        # Main Analysis

        # - Create LAS Dataset
        arcpy.AddMessage('Creating LAS Dataset...')
        arcpy.management.CreateLasDataset(input_workspace, output_las_dataset, "NO_RECURSION", "", coordinate_system, "NO_COMPUTE_STATS", "RELATIVE_PATHS")
        arcpy.AddMessage('...LAS Dataset Created')

        # - Make LAS Dataset Layer

        input_las_dataset = output_las_dataset + ".lasd"
        
        arcpy.management.MakeLasDatasetLayer(input_las_dataset, output_layer, class_codes, return_values)
        arcpy.AddMessage('...LAS Dataset Layer Created')

        # - - Set the workspace for ListFeatureClasses
        
        fields = ['ORTHO', 'Shape']
        #values = [row[0] for row in arcpy.da.SearchCursor(tile_index, field)]
        

        # -= Extent Filtering and looping
        arcpy.AddMessage('Starting Raster Loop...')
        
        #for row in arcpy.da.SearchCursor(tile_index, fields):

        rows = arcpy.SearchCursor(tile_index, fields)
        arcpy.AddMessage('Search cursor assigned to ' + tile_index)

        # - Create input LAS layer for raster conversion
        input_las_layer = output_layer + ".lasd"
        arcpy.env.outputCOordinateSystem = coordinate_system

        for row in rows:
            feat = row.getValue('Shape')
            tile_name = row.getValue('ORTHO')
            arcpy.AddMessage('...Extent retrieved for ' + tile_name)

            # - Create Name
            tile_output = output_raster + tile_name

            # - Set Extent
            arcpy.env.extent = feat.extent
            arcpy.AddMessage('... set extent for to {0}, {1}, {2}, {3}'.format(arcpy.env.extent.XMin, arcpy.env.extent.YMin, arcpy.env.extent.XMax, arcpy.env.extent.YMax))
            
            # - LASDataset to Raster
            arcpy.AddMessage('Creating output raster: ' + tile_output)
            arcpy.LasDatasetToRaster_conversion(input_las_layer, tile_output, 'ELEVATION', 'BINNING MAXIMUM NATURAL_NEIGHBOR', 'FLOAT', 'CELLSIZE', cell_size, '1')
            arcpy.AddMessage('... created raster tile: ' + tile_name)

        
        pass
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
    except Exception as e:
        print e.args[0]
    finally:
        # Regardless of whether the script succeeds or not, delete 
        #  the row and cursor
        #
        if rows:
            del rows
# End LASToDSM_Conversion function
 
# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE, 
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    # Arguments are optional
    argv = tuple(arcpy.GetParameterAsText(i)
        for i in range(arcpy.GetArgumentCount()))
    LASToDSM_Conversion(*argv)

