'''----------------------------------------------------------------------------------
 Tool Name:     WriteFeaturesFromTextFile
 Source Name:   WriteFeaturesFromTextFile.py
 Version:       ArcGIS 9.1
 Author:        Environmental Systems Research Institute Inc.
 Required Argumuments:  An input feature class
                        An output text file
                        An input decimal separator character that indicates what character
                        should be used to separate the whole number from its decimal.
 Description:   Writes the features of a feature class out to a text file.
----------------------------------------------------------------------------------'''
import arcpy
import string, os, sys, locale, arcgisscripting
gp = arcgisscripting.create()
gp.overwriteoutput = 1

inputFC = arcpy.GetParameterAsText(0)
outFile = arcpy.GetParameterAsText(1)
decimalchar = arcpy.GetParameterAsText(2)
z_field = arcpy.GetParameterAsText(3)
m_field = arcpy.GetParameterAsText(4)


msgNotEnoughParams = "Incorrect number of input parameters."
msgUseValidDecimalPointSep = "Please use one of the valid decimal point separators."

def get_sepchar(arg):
    '''Return decimal point separator to use'''
    default_seps = ['default python output', 'locale decimal point', '#']
    valid_seps = {'comma':',', 'period':'.', '$sep$':'$SEP$'}
    for i in default_seps:
        valid_seps[i] = 'locale default'

    arg = arg.lower()
    if arg not in valid_seps:
        raise Exception, msgUseValidDecimalPointSep + str(valid_seps.keys())

    if arg in default_seps:
        locale.setlocale(locale.LC_ALL, '')
        sepchar = locale.localeconv()['decimal_point']
    elif arg in valid_seps:
        sepchar = valid_seps[arg]
    ##elif arg == arg3poss[0]: sepchar = "" # is this ever valid? disabling for now.
    gp.AddMessage('Using "%s" for decimal point separator' % sepchar)
    return sepchar

def get_zfield(fieldname):
    ''' Field name to use for Z or M value, use 'Z' or 'M' for geometry Z or M.
        Returns string of 'Field_name', 'pnt.z', or 'pnt.m'
    '''
    if fieldname.lower() in ['z','m']:
        fname = 'pnt.%s' % fieldname.lower()
    else:
        fname = '%s' % fieldname
    gp.AddMessage('Using "%s" for Z/M values' % fname)
    return fname

##try:
if len(sys.argv) < 4: raise Exception, msgNotEnoughParams
inputFC = sys.argv[1]
outFile = open(sys.argv[2], "w")

#optional parameters
sepchar = get_sepchar(decimalchar)
z_field = get_zfield(z_field)
m_field = get_zfield(m_field)

inDesc = gp.describe(inputFC)
print inDesc

inRows = gp.searchcursor(inputFC)
inRow = inRows.next()
outFile.write(inDesc.ShapeType + "\n")

while inRow:
    feat = inRow.GetValue(inDesc.ShapeFieldName)
    if inDesc.ShapeType.lower() == "point":
        pnt = feat.getpart()
        outLine = str(inRow.GetValue(inDesc.OIDFieldName)) + " " + str(pnt.x) + " " + str(pnt.y) + " " + str(pnt.z) + " " + str(pnt.m) + "\n"
        if sepchar == "": outFile.write(outLine)
        else: outFile.write(outLine.replace(".", sepchar))

    elif inDesc.ShapeType.lower() == "multipoint":
        partnum = 0
        partcount = feat.partcount
        outFile.write(str(inRow.GetValue(inDesc.OIDFieldName)) + " " + str(partnum) + "\n")
        while partnum < partcount:
            pnt = feat.getpart(partnum)
            outLine = str(partnum) + " " + str(pnt.x) + " " + str(pnt.y) + " " + str(pnt.z) + " " + str(pnt.m) + "\n"
            if sepchar == "": outFile.write(outLine)
            else: outFile.write(outLine.replace(".", sepchar))
            partnum += 1

    else:
        partnum = 0
        partcount = feat.partcount
        while partnum < partcount:
            outFile.write(str(inRow.GetValue(inDesc.OIDFieldName)) + " " + str(partnum) + "\n")
            part = feat.getpart(partnum)
            part.reset()
            pnt = part.next()
            pnt_count = 0
            while pnt:
                #outLine = str(pnt_count) + " " + str(pnt.x) + " " + str(pnt.y) + " " + str(pnt.z) + " " + str(pnt.m) + "\n"
                outLine = str(pnt_count) + " " + str(pnt.x) + " " + str(pnt.y) + " " + inRow.GetValue(inDesc.table(z_field)) + " " + str(pnt.m) + "\n"
                if sepchar == "": outFile.write(outLine)
                else: outFile.write(outLine.replace(".", sepchar))
                pnt = part.next()
                pnt_count += 1
                if not pnt:
                    pnt = part.next()
                    if pnt:
                        outFile.write("InteriorRing\n")

            partnum += 1
    inRow = inRows.next()
outFile.write("END")
outFile.flush()
outFile.close()
print gp.GetMessages()

##except Exception, ErrorDesc:
##    gp.AddError(ErrorDesc[0])
##    if outFile: outFile.close()
##    gp.AddError(gp.getmessages(2))
##    print gp.GetMessages()
