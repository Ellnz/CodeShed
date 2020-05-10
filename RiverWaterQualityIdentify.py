#Ellis Nimick
# this script automates the aggregation and organisation of NIWA river quality data, converting the monitoring site coordinates to geospatial data,
# coordinate points retain their respective records [as median] for individual reported metrics used asses water quality
# geospatial anaylsis is then used to spatially-infer plausible water quality metrics of NZ rivers, as derived from geographically associated monitoring stations.

# prepare necessary modules.
import arcpy as ap, sys, traceback, os, csv

# establish tool input parameters, environment and spatial coordination system and appropriate geographic transformation.
ap.env.overwriteOutput = True
# wd = (r"C:\Users\Ellis\Documents\ArcGIS\Projects\River") #workspace directory containing all sub-folders and GDBs.
wd = ap.GetParameterAsText(0)           # workspace directory as parameter
NRWQN = ap.GetParameterAsText(1)        # .csv dataset containing National River and Water Quality Network data
RiverPoly = ap.GetParameterAsText(2)    # NZ river polygon, 150k is provided, but other resolutions can be used instead.
os.chdir(wd)

# establishes spatial coordination system and transformation.
ap.env.outputCoordinateSystem = ap.SpatialReference(2193)   #NZTM code
ap.env.geographicTransformations = "NZGD_2000_To_WGS_1984_1; New_Zealand_1949_To_NGD_2000_3_NTv2"

# Function to determine whether workspace geodatabase already exists, and creates a new one if there is not.
if ap.Exists(wd + "\\" + "RQTemp.gdb")== False:
    scrgdb_path = ap.CreateFileGDB_management(wd, "RQTemp.gdb")
else:
    scrgdb_path = wd + "\\RQTemp.gdb"
ap.env.workspace = str(scrgdb_path)         # sets the new file GDB as the current workspace environment.

# Function to determine whether final outout gdb already exists, and creates a new one if there is not.
if ap.Exists(wd + "\\" + "riverFinal.gdb")== False:
    resultgdb_path = ap.CreateFileGDB_management(wd, "riverFinal.gdb")
else:
    resultgdb_path = wd + "\\riverFinal.gdb"
ap.env.workspace = str(resultgdb_path)

# Import rivers quality data from provided (upto-date) .csv file, and save to [empty] list variable.
ap.env.workspace = str(wd)
FWQ_points = []
openf = open(NRWQN)           # NRWQN Parameter input or (wd + "\\ScriptData\\RiverWaterQualityTrends.csv")
fileReader = csv.reader(openf, delimiter = ',')

for row in fileReader:                                                   # function to append each row of the .csv to the variable.
    if fileReader.line_num != 1:                                         # ignores the first [header] row
        for row in fileReader:
            FWQ_points.append(row)                                       # appends the current row as a value to the FWQ_points list


# Process 1: produce individual point feature classes for each of the relevant and reported for measurements of New Zealand river water quality.
# empty list variables for storing relevant values belonging to  ach river water quality measurement.
NI_median = []                  # stores only the median value of total nitrogen.
NI_fc = []                      # stores geographic coordiantes for producing a feature class of total nitrogen monitoring sites.
PH_median = []
PH_fc = []
WC_median = []
WC_fc = []
EC_median = []
EC_fc = []
MV_median = []
MV_fc = []

spatialRef = ap.SpatialReference("WGS 1984")                 # ensures the correct coordinate system is adhered to
for rowSel in FWQ_points:
    if rowSel[9] == "Total nitrogen":                        # if row contains "Total Nitrogen" in field 'np_id"
        NI_median.append(rowSel[23])                         # returns to list variable median data measurement
        NI_pt = ap.Point(rowSel[5], rowSel[6])               # returns to list variable longitude and latitude as point data
        NI_pg = ap.PointGeometry(NI_pt, spatialRef)          # produces point geometry from point data.
        NI_fc.append(NI_pg)                                  # appends each geometry coordinate to a single list.
    elif rowSel[9] == "Total phosphorus":
        PH_median.append(rowSel[23])
        PH_pt = ap.Point(rowSel[5], rowSel[6])
        PH_pg = ap.PointGeometry(PH_pt, spatialRef)
        PH_fc.append(PH_pg)
    elif rowSel[9] == "Clarity":
        WC_median.append(rowSel[23])
        WC_pt = ap.Point(rowSel[5], rowSel[6])
        WC_pg = ap.PointGeometry(WC_pt, spatialRef)
        WC_fc.append(WC_pg)
    elif rowSel[9] == "E. coli":
        EC_median.append(rowSel[23])
        EC_pt = ap.Point(rowSel[5], rowSel[6])
        EC_pg = ap.PointGeometry(EC_pt, spatialRef)
        EC_fc.append(EC_pg)
    elif rowSel[9] == "Macroinvertebrate community index":
        MV_median.append(rowSel[23])
        MV_pt = ap.Point(rowSel[5], rowSel[6])
        MV_pg = ap.PointGeometry(MV_pt, spatialRef)
        MV_fc.append(MV_pg)
    else:
        pass
ap.CopyFeatures_management(NI_fc, "totalNitr")      # produces a point feature class containing every monitoring site with total nitrogen content data.
ap.CopyFeatures_management(PH_fc, "totalPhos")      # produces a point feature class containing every monitoring site with total phosphorus content data.
ap.CopyFeatures_management(WC_fc, "waterClar")      # produces a point feature class containing every monitoring site with water clarity data.
ap.CopyFeatures_management(EC_fc, "EcoliPres")      # produces a point feature class containing every monitoring site with E. coli data,
ap.CopyFeatures_management(MV_fc, "macrInvCo")      # produces a point feature class containing every monitoring site with macroinvertebrate community index data,



# process 2: convert from shapefiles to feature classes within a geodatabase. (I wanted this to happen automatically in the prior step, but "TypeError: unsupported operand type(s) for +: 'Result' and 'str" ensured that it never worked.
ap.env.workspace = str(wd)
ap.ListFeatureClasses()
for fcPre in ap.ListFeatureClasses():               # function to convert new fc to the geodatabase (could not get them to be saved here immediately).
    ap.FeatureClassToGeodatabase_conversion(fcPre, scrgdb_path)

# Process 3: [re] append median measurement values of each NIWA river quality metric to the corresponding geographical coordinate point geometry.
ap.env.workspace = str(wd)
field = "Median"
ap.AddField_management(scrgdb_path + "\\totalNitr_shp", field_name="Median", field_type="FLOAT")         # adds median measurement values to total nitrogen measurement coordinates
pointer = 0                                             #increment variable, to append each subsequential median row value to the approproate coordinates, beginning with the first row.
print(NI_median[pointer])
rows = ap.UpdateCursor(scrgdb_path + "\\totalNitr_shp")
for row in rows:
    print(row)
    row.setValue(field, NI_median[pointer])
    pointer = pointer + 1
    rows.updateRow(row)
ap.AddField_management(scrgdb_path + "\\totalPhos_shp", field_name="Median", field_type="FLOAT")         # adds median measurement values to total phosphorus measurement coordinates
pointer = 0                                             # reset pointer for next cursor update
rows = ap.UpdateCursor(scrgdb_path + "\\totalPhos_shp")
for row in rows:
    print(row)
    row.setValue(field, PH_median[pointer])
    pointer = pointer + 1
    rows.updateRow(row)
ap.AddField_management(scrgdb_path + "\\waterClar_shp", field_name="Median", field_type="FLOAT")         # adds median measurement values to water clarity measurement coordinates
pointer = 0
rows = ap.UpdateCursor(scrgdb_path + "\\waterClar_shp")
for row in rows:
    print(row)
    row.setValue(field, WC_median[pointer])
    pointer = pointer + 1
    rows.updateRow(row)
ap.AddField_management(scrgdb_path + "\\EcoliPres_shp", field_name="Median", field_type="FLOAT")         # adds median measurement values to E. coli measurement coordinates
pointer = 0
rows = ap.UpdateCursor(scrgdb_path + "\\EcoliPres_shp")
for row in rows:
    print(row)
    row.setValue(field, EC_median[pointer])
    pointer = pointer + 1
    rows.updateRow(row)
ap.AddField_management(scrgdb_path + "\\macrInvCo_shp", field_name="Median", field_type="FLOAT")         # adds median measurement values to Macroinvertebrate community index measurement coordinates
pointer = 0
rows = ap.UpdateCursor(scrgdb_path + "\\macrInvCo_shp")
for row in rows:
    print(row)
    row.setValue(field, MV_median[pointer])
    pointer = pointer + 1
    rows.updateRow(row)


# Process 4
ap.env.workspace = scrgdb_path
for points_fc in ap.ListFeatureClasses():
    #print(points_fc)
    ap.CreateThiessenPolygons_analysis(points_fc, points_fc + "_thiess", "ALL")                                                   # Produces Thiessen polygons from each of the monitoring site geospatial coordinate points.
    ap.Clip_analysis(points_fc + "_thiess", RiverPoly, points_fc + "_ThCl_Fin")       # function to clip each Thiessen river polygon within NZ river confines. #wd + "\\ScriptData\\River150kPoly\\River150kPoly.shp" for paramater
    final_fc = (points_fc + "_ThCl_Fin")
    ap.env.workspace = wd
    ap.CopyFeatures_management(scrgdb_path + "\\" + final_fc, resultgdb_path + "\\" + final_fc)                                   # copies final outputs to a separate geodatabase, so that all final outputs are organised and found within a single directory.
    ap.env.workspace = scrgdb_path

# Commented-out function to delete the GDB containing all non-finalized river quality feature classes.
#ap.env.workspace = wd
#ap.Delete_management("RQTemp.gdb")

#The End
