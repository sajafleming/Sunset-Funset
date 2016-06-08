![Sunset Funset Logo](/static/biglogo.png)

Have you ever been to a new city and wondered where to watch the sunset? Sunset Funset does the hard work for you by analyzing 
topographic data from the USGS to find the best sunset viewing locations for a given area.  It does this by searching for 
peaks within a certain radius of a user-specified location. These peaks are then further evaluated as sunset viewing points by
testing if the view is obstructed to the west. They are ranked using a variety of criteria including their elevation and their
viewing angle. The top-ranked sunset viewing points are then plotted on a map along with sample sunset pictures from each 
location that are pulled from the Flickr API.

![App Screen Shot](/readmescreenshot/screenshot.png)

# Contents
* [Motivation](#motivation)
* [Data](#data)
* [Finding Peaks](#findinglocations)
* [Displaying Results](#display)

# <a name="motivation"></a>Motivation

# <a name="data"></a>Data Source
Sunset Funset uses raster elevation data of 1 arc-second resolustion. The data are downloaded as IMG files from the [USGS](http://viewer.nationalmap.gov/basic/) which are then stored locally. Each file contains elevation data for a 1 degree latitude by 1 degree longitude rectangle of the United States.
Below is a visual representation of one such file:

![Data Image](/readmescreenshot/fav.jpg)

The IMG files are named according to the latitude and longitute of the northwest corner of the area for the data they contain. This makes it convient for finding the relevant elevation data for the user's entered location. The file containing the user's (latitude, longitude) and the 8 surrounding files are pulled into memory and read as a 2D numpy array using the osgeo python library. Each array is 3612 x 3612 and each cell contains elevation in meters. The points in the matrix are approximately 30 meters apart.

# <a name="findinglocations"><a/>Finding Viewing Locations

# <a name="display"></a>Displaying Results

![App Screen Shot2](/static/screenshot2.png)
