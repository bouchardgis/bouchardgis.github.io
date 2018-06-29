# 
# ArcGIS Version:   10.3
# Python Version:   2.7
#
# Purpose:  Creates solar radiation maps for the buildings specified in the building
#           footprint and SQL search query parameters. Outputs a feature estimating
#           the ideal solar installation for the building or home, and a solar map
#           raster of its solar insolation in watt-hour per meter squared.   
#
#
# References: Python 2.7 Documentation (https://docs.python.org/2/)
#             ArcPy Documentation (http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy/what-is-arcpy-.htm)
#             ArcPy Template for Geoprocessing (https://blogs.esri.com/esri/arcgis/2011/08/04/pythontemplate/)
#             Arcpy SearchCursor documentation (http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-data-access/searchcursor-class.htm)
#--------------------------------------------------------------------------------------------------------------
import os
import sys
import arcpy
def SolarMain(workspace, search_query, building_footprints, dsm_surface, time_configuration, output_location_parameter, output_root):
    """This function automates the SEEP Solar Model - which yields solar installation estimates for buildings in a feature class"""
    try:
        workspace_location = os.path.dirname(workspace)
        #arcpy.AddMessage(workspace_location)
        
        fc = building_footprints
        fields = ['Address', 'Area', 'OBJECTID', 'SHAPE@']
        sql_where_clause = search_query
        cell_size = 0.5
        desc = arcpy.Describe(fc)
        sr = desc.spatialReference
        output_location = output_location_parameter + os.sep

        # SCRIPT OUTPUT LIST (for Merge function)
        seep_sol_map_list = []

        # ENVIRONMENT SETTINGS
        arcpy.env.workspace = workspace
        arcpy.env.scratchworkspace = workspace
        arcpy.env.cellSize = cell_size
        arcpy.env.overwriteOutput = True
        arcpy.env.outputCoordinateSystem = sr

        # CHECKOUT EXTENSIONS
        arcpy.CheckOutExtension("Spatial")


        # ===== Main Loop - For each row print address and area of building, based on where clause =====
        cursor = arcpy.da.SearchCursor (fc, fields, where_clause=(sql_where_clause))
        for row in cursor:
            # -- Initialize function variables
            object_id = str(row[2])
            fc_out = workspace + os.sep + 'SInt_' + object_id
            select_clause = "Address = " + "'" + row[0] + "'"
            out_raster = workspace + os.sep + 'SInt_r' + object_id
            field = fields[2] # for building height
    
			
            # -- SetExtent - around Study area
            extent = desc.extent
            arcpy.env.extent = extent
    

            # -- Create individual feature in_feature, using Select_analysis()
            arcpy.Select_analysis(fc, fc_out, select_clause)
            

            # -- Create in_feature
            in_feature = arcpy.Describe(fc_out)
            

            # -- SetExtent - around building
            extent = in_feature.extent
            arcpy.env.extent = extent

    
            # -- Get points to run solar radiation functions on - Feature to Raster
            arcpy.FeatureToRaster_conversion (fc_out, field, out_raster, cell_size)


            # -- Raster to Point around building
            #      Initialize function variables
            in_raster = out_raster
            out_point_feature = workspace + os.sep + 'SInt_p' + object_id
    
            arcpy.RasterToPoint_conversion (in_raster, out_point_feature)


            # -- Run Solar Points - on building rooftop
            #      Init solar variables
            in_point_feature = out_point_feature
            out_sol_feature = workspace + os.sep + 'SInt_SolRaw_' + object_id
            diffuse_model_type = ""
            diffuse_proportion = 0.3
            transmittivity = 0.5

            #      Extend Extent for Solar Radiation calculations (250 m)
            in_buffer = fc_out
            out_buffer = workspace + os.sep + 'SInt_BExtent_' + object_id
            distance = '250 Meters'
            arcpy.Buffer_analysis (in_buffer, out_buffer, distance)

            #      Set new Extent to environment parameters
            buffer_obj = arcpy.Describe(out_buffer)
            arcpy.env.extent = buffer_obj.extent

            arcpy.sa.PointsSolarRadiation(dsm_surface, in_point_feature, out_sol_feature, "", "", "",
                                          time_configuration, "", "", "", "", "", "", "", "",
                                          diffuse_model_type, diffuse_proportion, transmittivity, "", "", "")


            # -- Create Solar Map - Feature to Raster

            #      Initialize
            in_sol_map = out_sol_feature
            sol_field = 'T0'
            out_sol_map = workspace + os.sep + 'SO_SM' + object_id

            #      Set Extents around building again
            extent = in_feature.extent
            arcpy.env.extent = extent

            #      Execute Function
            arcpy.FeatureToRaster_conversion (in_sol_map, sol_field, out_sol_map, cell_size)
            

            # -- Generate suitable solar panel area total (total potential area)
            #        See Esri Blog - Solar Siting
            #      Initialization
            in_reclass_raster = out_sol_map
            reclass_field = "Value"

            #      Reclassify - ideal in class 3
            out_reclass = arcpy.sa.Reclassify(in_reclass_raster, reclass_field,
                                              arcpy.sa.RemapRange([[0.0,900000.0,1],[900000.01,1000000.0,2],
                                                                   [1000000.01,1500000.0,3]]))

            #      Raster to Polygon (simplify) - using out_reclass as an input
            out_rc_feature = workspace + os.sep + 'SInt_RC_' + object_id
            arcpy.RasterToPolygon_conversion (out_reclass, out_rc_feature)

            #      Select from Reclassified polygon - only class 3 for solar panel area
            rc_where_clause = "gridcode = 3"
            out_ideal_sol = workspace + os.sep + 'SOut_Ideal_' + object_id
            arcpy.Select_analysis (out_rc_feature, out_ideal_sol, rc_where_clause)


            # -- Determine mean solar rad on ideal rooftop location
            #     Initialize
            
            #     Check if out_ideal_sol has a feature
            in_zone_data = out_ideal_sol

            #     Continue Initialization
            zone_field = "gridcode"
            in_value_raster = out_sol_map
            out_table = workspace + os.sep + 'SInt_IRad_' + object_id

            #     Execute
            try: 
                arcpy.sa.ZonalStatisticsAsTable (in_zone_data, zone_field, in_value_raster, out_table)
            except:
                arcpy.sa.ZonalStatisticsAsTable (out_rc_feature, zone_field, in_value_raster, out_table)

            actual_rad_cursor = arcpy.da.SearchCursor (out_table, ['MEAN'])
            actual_rad = 0.0

            for out_table_row in actual_rad_cursor:
                actual_rad = float(out_table_row[0])
            

            # -- Determine Ideal Rooftop Area - limited to 85% of ideal area (for irregular shapes)
            #       uses Statistics_analysis
            #      Initialize
            in_stats = out_ideal_sol
            out_stats = workspace + os.sep + 'SInt_StatA_' + object_id
            statistics_field = [["Shape_Area","SUM"]]

            #      Execute
            arcpy.Statistics_analysis (in_stats, out_stats, statistics_field)
            ideal_rooftop_area = arcpy.da.SearchCursor (out_stats, ['Sum_Shape_Area'])
            rooftop_area = 0.0

            for rooftop_row in ideal_rooftop_area:
                rooftop_area = float(rooftop_row[0]) * 0.85


            # -- Calculate System Estimates using SEEP Estimation Model (a text file)
            #     Calculation Constants: 
            lifetime = 33.0
            average_sun_hr = 6.7
            cdn_rate = 0.76
            dc_ac_ratio = 1.1
            reference_rad = 1000.0
            temp_co = -0.0047
            temp_ref = 25
            temp_cell = 17
            cost_initial = 0.0
            cost_maint = 0.0
            system_loss = 0.86
            inverter_loss = 0.96
            area_rating_ratio = 168.3
            
            #     Variable Calculations
            actual_rad_hr = actual_rad / 365.0 / average_sun_hr
            np_rating = rooftop_area * area_rating_ratio
            #arcpy.AddMessage('System Rating: ' + str(np_rating) + ' W')
            
            dc_power = (actual_rad_hr / reference_rad) * np_rating * (1 + (temp_co * (temp_cell - temp_ref)))
            ac_power = (dc_power / dc_ac_ratio) * (system_loss * inverter_loss)

            #     Defining Costs
            if np_rating < 10000:
                cost_initial = 3000.0 * (np_rating / 1000.0)
               
            if (np_rating >= 10000) and (np_rating < 100000):
                cost_initial = 2900.0 * (np_rating / 1000.0)
               
            if np_rating < 10000.0:
                cost_maint = 21.0 * (np_rating / 1000.0)
               
            if (np_rating >= 10000.0) and (np_rating < 100000.0):
                cost_maint = 19.0 * (np_rating / 1000.0)
               
            total_system_cost = (cost_initial + cost_maint) / cdn_rate

            power_cost = 0.0
            if ac_power > 0: # Prevents divide by zero errors when no AC power is projected
                power_cost = (total_system_cost / (ac_power / 1000)) / lifetime / 365 / average_sun_hr

            #arcpy.AddMessage('AC output: ' + str(ac_power) + ' W')
            #arcpy.AddMessage('System cost: $' + str(total_system_cost))
            #arcpy.AddMessage('Resulting amortized power cost: $' + str(power_cost))

            

            # -- Return Useful Area & Calculations to Feature Class (fc_out)
            #     Initialize
            seep_output = fc_out
            output_fields = ['System_Rating', 'AC_Power', 'System_Cost', 'Power_Cost']

            #     Add fields (System rating, AC Power, System Cost, Power Cost) to Output Feature
            arcpy.AddField_management (seep_output, output_fields[0], "FLOAT")
            arcpy.AddField_management (seep_output, output_fields[1], "FLOAT")
            arcpy.AddField_management (seep_output, output_fields[2], "FLOAT")
            arcpy.AddField_management (seep_output, output_fields[3], "FLOAT")

            #     Update values in new fields
            with arcpy.da.UpdateCursor (seep_output, output_fields) as cursor:
                for update_row in cursor:
                    update_row[0] = np_rating
                    update_row[1] = ac_power
                    update_row[2] = total_system_cost
                    update_row[3] = power_cost
                    cursor.updateRow(update_row)
            #     END UpdateCursor Loop

            #     Save feature class as an output
            output_path = workspace + os.sep
            output_name = 'SOut_Data_' + object_id
            seep_output_fc = output_path + output_name
            arcpy.FeatureClassToFeatureClass_conversion (seep_output, output_path, output_name)

            # -- Append Feature Class & Raster List
            #seep_data_list.append(r"" + seep_output_fc)
            seep_sol_map_list.append(out_sol_map)

            #Delete Intermediates
            del extent, in_feature, buffer_obj, out_reclass, actual_rad_cursor, ideal_rooftop_area, cursor
            
            #arcpy.AddMessage(('Completed: {0}, {1} in {2}'.format(row[0], row[1], sql_where_clause)))
            arcpy.AddMessage('Building analysis completed: ' + object_id)

            #=========================== END MAIN LOOP ==========================================

            
        arcpy.AddMessage('Buildings processed, starting merge...')
        
        
        # -- The Merge (of all calculations done during this script)
        #      Initialize
        seep_out_data = output_location + 'SO_' + output_root
        seep_out_raster = 'SM' + output_root
        pixel_type = "64_BIT"

        #arcpy.AddMessage('Initialized...')

        #      Retrieve List of Feature Outputs
        seep_data_list_raw = arcpy.ListFeatureClasses ("SOut_Data_*")
        
        seep_data_list = []
        for s in seep_data_list_raw:
            ds = arcpy.Describe(s)
            seep_data_list.append(ds.catalogPath)

        #      Merge Raster Solar Maps (create raster dataset, workspace to raster dataset)
        try:
            arcpy.CreateRasterDataset_management (output_location, seep_out_raster, cell_size, pixel_type)
        except:
            print 'Raster dataset exists already, proceeding...'
            
        try:
            arcpy.Mosaic_management (seep_sol_map_list, output_location + seep_out_raster)
        except:
            print 'No data for Mosaic - proceeding...'
            

        # -- Reset environment to proper extent
        extent = desc.extent
        arcpy.env.extent = extent

        #      Merge Feature Classes
        arcpy.Merge_management (seep_data_list, seep_out_data)


        # -- Clean-Up
        try:
            arcpy.Delete_management (workspace)
            arcpy.CreateFileGDB_management (workspace_location, os.path.basename(workspace))
            arcpy.AddMessage ('Workspace reset...')
        except:
            arcpy.AddMessage ('Workspace was not reset...')

        del extent

        
        pass
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
    except Exception as e:
        print e.args[0]
# End SolarMain function
 
# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE, 
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    argv = tuple(arcpy.GetParameterAsText(i)
        for i in range(arcpy.GetArgumentCount()))
    SolarMain(*argv)

