# A simple Python script that, for a user-specific number of times, will randomly select a user-specified (%) subset of vector data within a given layer and creates a new layer from that. It then outputs a spreadsheet of derived layer's attribute table.
# Ellis Nimick

# preconfig
import arcpy as ap, sys, traceback, os, csv
ap.env.overwriteOutput = True

# paramaters
inputfc = ap.GetParameterAsText(0)
wd = ap.GetParameterAsText(1)
SubSize = ap.GetParameterAsText(2)
SubsetsN = ap.GetParameterAsText(3)

# spatial coordination and transformation.
ap.env.outputCoordinateSystem = ap.SpatialReference(2193)   #NZTM code
ap.env.geographicTransformations = "NZGD_2000_To_WGS_1984_1; New_Zealand_1949_To_NGD_2000_3_NTv2"

# Function to determine whether there is a pre-existing output GDB, and creates one if there is not.
if ap.Exists(wd + "\\" + "SubsetPatch.gdb")== False:
    outgdb_path = ap.CreateFileGDB_management(wd, "SubsetPatch.gdb")                      # Variable that returns the workspace GDB location and name.
else:
    outgdb_path = wd + "\\SubsetPatch.gdb"

#replication script
ap.env.workspace = outgdb_path
#SubSize = 25        #size of the training feature class subset, can be randomized
incValue = 0        #incremental value
while (incValue < int(SubsetsN)):
    Patch = ap.SubsetFeatures_ga(inputfc, wd + "\\SubsetPatch.gdb" + "\\PatchSubset_" + str(incValue), "", SubSize, "PERCENTAGE_OF_INPUT")
    ap.TableToExcel_conversion(Patch, ("Excel\\PatchSubset_" + str(incValue)))
    incValue = incValue + 1
