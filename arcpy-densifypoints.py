import arcpy
import math
import numpy
arcpy.env.overwriteOutput = True


# region setting up input points to mimic stream FC
print('Copying points to memory...')
inputPoints = r'C:\Users\paul.sesinkclee\Documents\ArcGIS\Projects\scratch.gdb\test_densify_points'
arcpy.CopyFeatures_management(in_features=inputPoints, out_feature_class='in_memory/Points')

print('Sorting points by time...')
arcpy.Sort_management(in_dataset='in_memory/Points', out_dataset='in_memory/sortPoints', sort_field='fixtimeutf')
# endregion


print('Starting search cursor...')
searchCursor = arcpy.da.SearchCursor(in_table='in_memory/sortPoints', field_names=['SHAPE@XY', 'vin', 'fixtimeutf'])

previous = None
for point in searchCursor:
    # create current tuple like this (x, y, vin, fixtimeutf)
    current = (point[0][0], point[0][1], point[1], point[2])

    if previous:
        # calculating distance between current and previous point
        l = math.sqrt((current[0] - previous[0])**2 + (current[1] - previous[1])**2)

        # if distance is less than ~400ft, continue to next point
        if l < 122:
            continue

        # calculating the number of necessary midpoints
        length = numpy.array([l])
        bins = numpy.array([122, 244, 366, 488, 610])
        ind = numpy.digitize(length, bins)
        midpointCount = int(ind.item())
        print('Midpoints needed: ' + str(midpointCount))

        # distance between points > ~2000ft
        if midpointCount > 4:
            print('Long Segment Warning.  Route splitting could happen here...')

        # calculating x and y delta
        x_delta = (current[0] - previous[0]) / float(midpointCount)
        y_delta = (current[1] - previous[1]) / float(midpointCount)

        # creating midpoints and attributing them
        timeAdd = 0
        for i in range(0, midpointCount):
            timeAdd += 1
            mp = (previous[0] + i * x_delta, previous[1] + i * y_delta)

            midpoint = ((mp[0], mp[1]), current[2], current[3] + timeAdd)

            insertCursor = arcpy.da.InsertCursor(in_table='in_memory/sortPoints', field_names=['SHAPE@XY', 'vin', 'fixtimeutf'])
            insertCursor.insertRow(midpoint)

    previous = current

arcpy.CopyFeatures_management(in_features='in_memory/sortPoints', out_feature_class=r'C:\Users\paul.sesinkclee\Documents\ArcGIS\Projects\scratch.gdb\testPoints_densified')