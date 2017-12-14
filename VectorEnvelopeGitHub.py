import arcpy, fileinput, os, string, sys
from arcpy import env
from os import path

#input_fc = "C:/python/Assignment3/Newark.gdb/NewarkCityLimit"
#out_workspace = "C:/python/Assignment3/Newark.gdb"
#output_envelope = "C:/python/Assignment3/Newark.gdb/ncle"

# Get the feature class to be enveloped, the workspace, and the envelope feature class
# from the user
input_fc = arcpy.GetParameterAsText(0)
out_workspace = arcpy.GetParameterAsText(1)
output_envelope = arcpy.GetParameterAsText(2)

print("Input feature class is ", input_fc)
print("Output workspace is ", out_workspace)
print("Envelope feature class is ", output_envelope)

# Only need the name of the envelope feature class for CreateFeatureclass_management, not entire path
output_envelope = os.path.basename(output_envelope)

# Set the workspace and allow overwriting
env.workspace = out_workspace
env.overwriteOutput = True

# Describe the input feature class
desc = arcpy.Describe(input_fc)

# Quit if input feature class is not Point, Polyline, or Polygon shape type
if desc.shapeType != "Point" and desc.shapeType != "Polyline" and desc.shapeType != "Polygon":
    print ("feature class not a Point, Line, or Polygon shape type")
    sys.exit()

# Use spatial reference of input feature class for envelope
spatial_ref = desc.spatialReference

# Initialize envelope coordinates
ymax = 0.0
ymin = 100000000000000000.0
xmax = 0.0
xmin = 100000000000000000.0

# Get coordinates of envelope for Polyline and Polygon feature classes
if desc.shapeType == "Polygon" or desc.shapeType == "Polyline":
    cursor = arcpy.da.SearchCursor(input_fc, ["OID@", "SHAPE@"])
    for row in cursor:
        for part in row[1]:
            for point in part:
                if point:
                    if point.X < xmin:
                        xmin = point.X
                    if point.X > xmax:
                        xmax = point.X
                    if point.Y < ymin:
                        ymin = point.Y
                    if point.Y > ymax:
                        ymax = point.Y

# Get coordinates of envelope for Point feature classes
elif desc.shapeType == "Point":
    cursor = arcpy.da.SearchCursor(input_fc, ["SHAPE@XY"])
    for row in cursor:
        x, y = row[0]
        print("{0}, {1}".format(x,xmax))
        if x < xmin:
            xmin = x
        if x > xmax:
            xmax = x
            print("new xmax {0}, {1}".format(x,y))
        if y < ymin:
            ymin = y
        if y > ymax:
            ymax = y
del cursor

# Make an array of envelope coordinates
array = arcpy.Array()
array.add(arcpy.Point(xmin,ymin))
array.add(arcpy.Point(xmax,ymin))
array.add(arcpy.Point(xmax,ymax))
array.add(arcpy.Point(xmin,ymax))

# Create the envelope feature class
arcpy.CreateFeatureclass_management(out_workspace, output_envelope, "Polygon","","","",spatial_ref)

# Complete envelope polygon by adding envelope coordinates to envelope feature class and exit
cursor = arcpy.da.InsertCursor(output_envelope, ["SHAPE@"])
cursor.insertRow([arcpy.Polygon(array)])

del cursor
