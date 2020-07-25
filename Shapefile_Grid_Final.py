from osgeo import ogr
import os
import geopandas as gpd
import shapefile
from math import ceil  
import ogr, csv  

# Source code for gridmesh function: https://gis.stackexchange.com/questions/54119/creating-square-grid-polygon-shapefile-with-python
# Referencce for GDAL library usage: https://pcjericks.github.io/py-gdalogr-cookbook/layers.html

# Create mesh function depending on metric in which the original shapefile is generated (feet, meters, kms etc.)
def gridmesh(outputGridfn,xmin,xmax,ymin,ymax,gridHeight,gridWidth):

    xmin = float(xmin)
    xmax = float(xmax)
    ymin = float(ymin)
    ymax = float(ymax)
    gridWidth = float(gridWidth)  
    gridHeight = float(gridHeight) 

    # get rows
    rows = ceil((ymax-ymin)/gridHeight)
    # get columns
    cols = ceil((xmax-xmin)/gridWidth)

    # start grid cell envelope
    ringXleftOrigin = xmin
    ringXrightOrigin = xmin + gridWidth
    ringYtopOrigin = ymax
    ringYbottomOrigin = ymax-gridHeight


    # create output file
    outDriver = ogr.GetDriverByName('ESRI Shapefile')
    #if os.path.exists(outputGridfn):
     #   os.remove(outputGridfn)

    outDataSource = outDriver.CreateDataSource(outputGridfn)
    outLayer = outDataSource.CreateLayer(outputGridfn,geom_type=ogr.wkbPolygon)
    featureDefn = outLayer.GetLayerDefn()

    # create grid cells
    countcols = 0
    while countcols < cols:
        countcols += 1

        # reset envelope for rows
        ringYtop = ringYtopOrigin
        ringYbottom =ringYbottomOrigin
        countrows = 0

        while countrows < rows:
            countrows += 1
            ring = ogr.Geometry(ogr.wkbLinearRing)
            ring.AddPoint(ringXleftOrigin, ringYtop)
            ring.AddPoint(ringXrightOrigin, ringYtop)
            ring.AddPoint(ringXrightOrigin, ringYbottom)
            ring.AddPoint(ringXleftOrigin, ringYbottom)
            ring.AddPoint(ringXleftOrigin, ringYtop)
            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(ring)

            # add new geom to layer
            outFeature = ogr.Feature(featureDefn)
            outFeature.SetGeometry(poly)
            outLayer.CreateFeature(outFeature)
            outFeature = None

            # new envelope for next poly
            ringYtop = ringYtop - gridHeight
            ringYbottom = ringYbottom - gridHeight

        # new envelope for next poly
        ringXleftOrigin = ringXleftOrigin + gridWidth
        ringXrightOrigin = ringXrightOrigin + gridWidth

    # Save and close DataSources
    outDataSource = None

# function to create csv files from original shapefile co-ordinates and new meshgrid created shapefile
def creating_csv(outputGridfn,count_x,x_cord,y_cord):
	# Shapefile reader
	sf=shapefile.Reader(outputGridfn)
	shapes = sf.shapes() 
	print("Total Grids in Shapefile"+" "+str(len(shapes)))
	grid_count=len(shapes) #25 shapefiles

#array lists to hold the shapefile data
	lst1=[]
	lst2=[]
	counter=0
	grid_xmin=[]
	grid_ymin=[]
	grid_xmax=[]
	grid_ymax=[]

	excelnumber=0

#shape[0] represents the 1st polygon of the shapefile
	for shapes in sf.iterShapes(): # 1 to 25
	    grid_xmin.append([])
	    grid_ymin.append([])
	    grid_xmax.append([]) 
	    grid_ymax.append([])
	    lst1.append([])
	    lst2.append([])
	    grid_xmin[counter],grid_ymin[counter],grid_xmax[counter],grid_ymax[counter]=shapes.bbox  #ist box
	   #sorting the x and y co-ordinates as per the each grid extent/boundaries in newly created shapefile.
	    for i in range(count_x):
	    	if((x_cord[i])<=(grid_xmax[counter])and (x_cord[i]) >=(grid_xmin[counter]) and (y_cord[i]) <=(grid_ymax[counter])and (y_cord[i])>=(grid_ymin[counter])):
	    		lst1[counter].append(x_cord[i])
	    		lst2[counter].append(y_cord[i])
	    counter+=1
 	#Printing the total number of points which belong to each grid and each grid extent in a shapefile.
	mysum=0
	for i in range(grid_count): # count=25
	    print((grid_xmin[i]),(grid_ymin[i]),(grid_xmax[i]),(grid_ymax[i]))
	    print(len(lst1[i]),len(lst2[i])) 
	    mysum+=len(lst1[i])  

	#creating the csv files as per number of grids and the points which belong inside each grid
	print(mysum)
	name=0
	header=['X_COORD','Y_COORD']
	datalist=['xmin','ymin','xmax','ymax']
	csv_filepath=input("Enter path & CSV file name to be created: ")

	for i in range(grid_count):
	    print((grid_xmin[i]),(grid_ymin[i]),(grid_xmax[i]),(grid_ymax[i]))
	    print(len(lst1[i]),len(lst2[i]))
	    print("CSV File number:"+ " " +str(excelnumber))
	    excelnumber+=1
	    with open(csv_filepath+str(name)+'.csv', 'w+') as f:      
	        filewriter = csv.writer(f)
	        filewriter.writerow(datalist)
	        zipped=zip(((grid_xmin[i]),(grid_ymin[i]),(grid_xmax[i]),(grid_ymax[i])))
	        filewriter.writerow(zipped)  
	        filewriter.writerow(['X_COORD','Y_COORD']) 
	        filewriter.writerows(zip(lst1[i],lst2[i]))  # already converted to meters on line 152
	    name+=1 


def read_shapefile(file):
	shapefile = file

# calculate extent of original shapefile
	driver = ogr.GetDriverByName("ESRI Shapefile")
	dataSource = driver.Open(shapefile, 0)
	layer = dataSource.GetLayer()
	layerDefinition = layer.GetLayerDefn()
	xmin, xmax, ymin, ymax = layer.GetExtent()  # extent of the total shapefile 
	print("Extent of Original Shapefile: " + "xmin: " + str(xmin)+ "," + "xmax: "+str(xmax)+ ","+"ymin: "+ str(ymin) + "," + "ymax: " + str(ymax))

#Priting the field names of in each layer of a shapefile: Currently this shapefile has single layer hence printing the details of just single layer. 
	for i in range(layerDefinition.GetFieldCount()):
		print(layerDefinition.GetFieldDefn(i).GetName())

#user input fields details to be stored in the array list: Currently just considered x and y co-ordinates.
	x=input("Select x co-ordinate Feature to be extracted from the listed fields:")	
	y=input("Select y co-ordinate Feature to be extracted from the listed fields:") 
	x_cord=[]
	y_cord=[]
	for feature in layer:
		x_cord.append(feature.GetField(x))
		y_cord.append(feature.GetField(y))

	count_x=len(x_cord)	
	print("Total x co-ordinates: "+ str(len(x_cord)))
	print("Total y co-ordinates: "+ str(len(y_cord))) 

	#User input path 
	outputGridfn=input("Enter folder path & New Grid Shapefile (.shp) name to be created:")
	#user input height and width for grid creation. 	
	gridHeight=input("Enter GridHeight:")
	gridWidth=input("Enter GridWidth:")

	#Function call for meshgrid file creation
	gridmesh(outputGridfn,xmin,xmax,ymin,ymax,gridHeight,gridWidth)
	print("New Gridmesh Shapefiles as per the specified grid size successfully created.")

	#Function call for csv files creation
	creating_csv(outputGridfn,count_x,x_cord,y_cord)
	print("Output CSV files successfully created.")


if __name__ == "__main__":
	filepath = input("Enter Original Shapefile (.shp) path to list all the features of a layer:") 
	read_shapefile(filepath)









