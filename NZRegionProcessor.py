# This script is able to input a csv or text file containing custom GPS points, turning it into a geospatial feature class.
# It can then segregate GPS points by region, and analysise the spatial-correlation between GPS points and import infrastructure points within each region.
# Ellis Nimick

# part 1: prepare inputs, configure the geoprocessing environment and prepare data for processing.
# import the necessary python module.
import arcpy as ap, sys, traceback, os, csv
# establish tool input parameters, environment and spatial coordination system and appropriate geographic transformation.
ap.env.overwriteOutput = True
wd = ap.GetParameterAsText(0)           #workspace directory containing all sub-folders and GDBs.
inputCsv = ap.GetParameterAsText(1)     #csv file that contains the GPS coordinates
inputClip = ap.GetParameterAsText(2)    #folder containg all releveant clippion region feature classes.
inputTopo = ap.GetParameterAsText(3)    #folder containing all relevant topographc data feature classes.
outFcRegions = ap.GetParameterAsText(4)
os.chdir(wd)
# Function to determine whether there is a pre-existing output GDB, and creates one if there is not.
if ap.Exists(wd + "\\" + "clippedData.gdb")== False:
    outgdb_path = ap.CreateFileGDB_management(wd, "clippedData.gdb")                      # Variable that returns the workspace GDB location and name.
else:
    outgdb_path = wd + "\\clippedData.gdb"
# spatial coordination and transformation.
ap.env.workspace = str(outgdb_path)
ap.env.outputCoordinateSystem = ap.SpatialReference(2193)   #NZTM code
ap.env.geographicTransformations = "NZGD_2000_To_WGS_1984_1; New_Zealand_1949_To_NGD_2000_3_NTv2"

# imports and processes the provided GPS data
# function to read GPS data from the imported .csv files and stores it to a [empty] list variable.
ap.env.workspace = str(wd)
GPS_points = []
openf = open(inputCsv)                          #new variable, using the open function to gain access the csv contents
fileReader = csv.reader(openf, delimiter = ',')
for row in fileReader:
    if fileReader.line_num != 1:                            #ignores the first [header] row
        for row in fileReader:
            GPS_points.append(row)                          #appends the current row as a value to the GPS_points list
# function to create a new GPS points feature class from the stored coordinates.
spatialRef = ap.SpatialReference("WGS 1984")                #ensures the correct coordinate system is adhered to
ptList = []
for pts in GPS_points:
    pt = ap.Point(pts[2], pts[1])
    pg = ap.PointGeometry(pt, spatialRef)
    ptList.append(pg)
#copies the new GPS_points fc to the topo_data folder, with the other topographic data files, streamlining the following append function by aggregating all the files.
ap.CopyFeatures_management(ptList, wd + "\\Task3_files\\Topo_data\\GPS_points.shp")


# Enables the script to readily access the provided region-clip and topographic data
# mount the directory of each spatial data types to a variable.
gpsdat = wd + str("\\Task3_files\\Topo_data\\GPS_points.shp")
# calls new empty list variables for appending the names and paths of region and topographic data.
clipshp_paths = []                                          #holds a list of directory paths and files names for each regional vector.
clipshp_names = []                                          #holds a list of the names of each region.
topshp_paths = []                                           #holds a list of directory paths and files for topographic data feature class.
topshp_names = []                                           #holds a list of the names of each of the topographic feature class.

# attains the file names and directory pathways of each regional-clip vector and appends them to the appropriate list variables.
ap.env.workspace = inputClip
for clipFCS in ap.ListFeatureClasses():
    print(clipFCS)     #test print
    fn = str(os.path.splitext(str(clipFCS))[0])             #calls a variable that returns the clipFCS value split into a single region [per loop], while also removing thefile-type suffix.
    clipshp_paths.append(inputClip + "\\" + str(clipFCS))
    clipshp_names.append(str(fn))
# attains the file names and directory pathways of each topographic spatial data types (+GPS_Points) and appends them to the appropriate list variables.
ap.env.workspace = inputTopo
for clipFCS in ap.ListFeatureClasses():
    fn = str(os.path.splitext(str(clipFCS))[0])
    topshp_paths.append(inputTopo + "\\" + str(clipFCS))
    topshp_names.append(str(fn))

# test prints of each appended list variable.
print(clipshp_paths)
print(clipshp_names)
print(topshp_paths)
print(topshp_names)


#Part 2: prepare an output directory and the produce initial regionally defined topographic vector data.
# Function used to clip all topographic\GPS data to the current[loop] region vector, placing the output in the correct dataset,
ap.env.workspace = wd + "\\clippedData.gdb"
for clp, item in enumerate(clipshp_paths):                                                # enumerates the name and pathway of each region clip, returning the numeric value of each.
    if ap.Exists(str(clipshp_names[clp])) == False:                                       # determines whether there exists a designated dataset for the current region.
        ap.CreateFeatureDataset_management(outgdb_path, clipshp_names[clp])               # creates a dataset if there is not already one.
        outfc = wd + "\\clippedData.gdb" + "\\" + str(clipshp_names[clp])                              # new variable returning the location of the new dataset.
        print(outfc)
    else:
        outfc = wd + "\\clippedData.gdb" + "\\" + str(clipshp_names[clp])
        print(outfc)
    for inp, item in enumerate(topshp_paths):                                             # begings a second nested for-loop. This returns enumerated values of the Topographic/GPS data, looping through each whilst still within the current region clip loop.
        print(inp,item)
        input_name = topshp_names[inp]
        clpoutname = clipshp_names[clp] + "_" + input_name + "_clip"
        print(clpoutname)
        ap.Clip_analysis(topshp_paths[inp], clipshp_paths[clp], clpoutname)               # clips the currently enumerated Topographic/GPS data with the currently looped though region clip.
        ap.FeatureClassToGeodatabase_conversion(clpoutname, outfc)                        # copies the output to the afore-created dataset for the specific region. nb: requires the GDB_conversion function, as copy_fc does not work here.
        ap.Delete_management(clpoutname)

# Function used to update the ID field, and append a new region field to the GPS feature classes.
for name in clipshp_names:                                                                # now for loop returning the name of each region use for clipping.
    ap.env.workspace = wd + "\\clippedData.gdb" + "\\" + str(name)
    print(name)    #test print
    ap.ListFeatureClasses()                                                               # lists the feature classes found by using the current region[clip] identifiier
    for gps_fc in ap.ListFeatureClasses():                                                # begins a new loop, cycling through the individual rows of each listed feature class.
        desc = ap.Describe(gps_fc)
        if "GPS" in desc.name:
            ap.AddField_management(gps_fc, field_name="Region", field_type="TEXT", field_length=50)     # adds a new field for the 'region' to be appended to.
            fields = ['ID', 'Region']                                                                   # sets the active fields within the FC that can be edited.
            rows = ap.UpdateCursor(gps_fc, fields)                                                      # new variable that returns the [feature class] and [fields] of what is being currently iterated.
            incremental = 1
            for row in rows:                                                                            # new for loop, updates the id field with the current increment value (and then increases it), and appends the current region to the new field.
                row.setValue(fields[0], incremental)
                rows.updateRow(row)
                incremental = incremental + 1
                for region in clipshp_names:
                    if region in desc.name:
                        row.setValue(fields[1], region)
                        rows.updateRow(row)
                ap.AddMessage("updated the fc {}".format(desc.name))
                ap.SetProgressorPosition()
            else:
                pass

# Part 3: perform geoprocessing operations between GPS point data, and the other topographic feature classes for each region dataset,
# this function loops through each regional data set, finding the region's topographic and GPS point feature classes, and then performs an appropriate geoprocessing analysis.
ap.env.workspace = str(outgdb_path)
for dataset in ap.ListDatasets():
    ap.env.workspace = str(outgdb_path) + "\\" + dataset
    print(dataset)     #print test
    fc_list = ap.ListFeatureClasses()
    for fc in ap.ListFeatureClasses():
        #ap.SetProgressor("default", "Geoprocessing different feature class types", 0, len(fc_list), 1)
        desc = ap.Describe(fc)                                                                                      # used to determine the FC type, which is then used to perform different types of analysis, suitable for each type.
        if "GPS" not in desc.name:                                                                                  # determines whether a feature class is GPS or not (ergo, topographic).
            if desc.shapeType == "Polygon":                                                                         # isolates and processes polygons, which are the forest feature classes in the regional topographic data.
                for region in clipshp_names:
                    if region in desc.name:
                        ap.Intersect_analysis([fc, region + "_GPS_points_clip_1"], region + "_GPS_intWithForest")
            elif desc.shapeType == "Point":                                                                         # isolates and processes points, which are the main places feature classes in the regional topographic data.
                for region in clipshp_names:
                    if region in desc.name:
                        ap.Near_analysis(region + "_GPS_points_clip_1", fc)
                        ap.CopyFeatures_management(fc, region + "_GPS_nearMainPlacs")                               # these are being copied into the gdb instead of the regional datasets... Can't fix.
            elif desc.shapeType == "Polyline":                                                                      # isolates and processes lines, which are the railway feature classes in the regional topographic data.
                for region in clipshp_names:
                    if region in desc.name:
                        ap.Buffer_analysis(fc, fc + "_Buffer", buffer_distance_or_field="5 Kilometers")             #how can I make this customisable? paramters?
                        ap.Intersect_analysis([region + "_railways_clip_1_Buffer", region + "_GPS_points_clip_1"], region + "_GPS_intWithRails")
                        ap.Delete_management(fc + "_Buffer")
            else:
                pass
#End
