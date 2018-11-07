import arcpy

def fieldjoiner(intable, infield, jointable, joinfield, addfields):
    # adding new fields to intable
    print(f'Adding new fields to {intable}' )
    fields = arcpy.ListFields(jointable)
    for addfieldName in addfields:
        for field in fields:
            if field.name == addfieldName:
                arcpy.AddField_management(in_table=intable, field_name=field.name, field_type=field.type)

    # creating join dictionary
    print(f'Building dictionary with key of [{joinfield}] and values of {addfields}')
    joinDict = {}
    jointableFields = []
    jointableFields.extend(addfields)
    jointableFields.append(joinfield)
    fieldCount = len(jointableFields)
    searchCursor = arcpy.da.SearchCursor(in_table=jointable, field_names=jointableFields)
    for row in searchCursor:
        joinDict.update({row[fieldCount - 1]: list(row[0: fieldCount - 1])})

    # populating new fields
    print(f'Populating {addfields} fields in {intable}')
    intableFields = []
    intableFields.extend(addfields)
    intableFields.append(infield)
    infieldPosition = len(intableFields) - 1

    updateCursor = arcpy.da.UpdateCursor(in_table=intable, field_names=intableFields)
    for row in updateCursor:
        infieldValue = row[infieldPosition]
        if joinDict.get(infieldValue) is not None:
            # print('Found a match!')
            joinList = joinDict.get(infieldValue)
            joinList.append(infieldValue)
            # print(joinList)

            for index, value in enumerate(joinList):
                row[index] = joinList[index]

            updateCursor.updateRow(row)
