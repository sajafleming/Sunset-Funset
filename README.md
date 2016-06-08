![Sunset Funset Logo](/static/biglogo.png)

Have you ever been to a new city and wondered where to watch the sunset? Sunset Funset does the hard work for you by analyzing 
topographic data from the USGS to find the best sunset viewing locations for a given area.  It does this by searching for 
peaks within a certain radius of a user-specified location. These peaks are then further evaluated as sunset viewing points by
testing if the view is obstructed to the west. They are ranked using a variety of criteria including their elevation and their
viewing angle. The top-ranked sunset viewing points are then plotted on a map along with sample sunset pictures from each 
location that are pulled from the Flickr API.

![App Screen Shot](/readmescreenshot/screenshot.png)

# Contents
* [Data](#data)
* [Finding Peaks](#findinglocations)
* [Displaying Results](#display)

# <a name="data"></a>Data Source
Sunset Funset uses raster elevation data of 1 arc-second resolustion. The data are downloaded as IMG files from the [USGS](http://viewer.nationalmap.gov/basic/) which are then stored locally. Each file contains elevation data for a 1 degree latitude by 1 degree longitude rectangle of the United States.
Below is a visual representation of one such file:

![Data Image](/readmescreenshot/fav.jpg)

The IMG files are named according to the latitude and longitute of the northwest corner of the area for the data they contain. This makes it convient for finding the relevant elevation data for the user's entered location. The file containing the user's (latitude, longitude) and the 8 surrounding files are pulled into memory and read as a 2D numpy array using the osgeo python library. Each array is 3612 x 3612 and each cell contains elevation in meters. The points in the matrix are approximately 30 meters apart.

# <a name="findinglocations"><a/>Finding Viewing Locations
## Finding local maxima
The first step in finding sunset viewing locations is to find all of the local maxima over the search radius. With a 20 mile radius, there are over 4.2 million potential peaks to check. As you can imagine, finding these peaks is very expensive. Initially, I was using [scipy's argrelmax](https://github.com/scipy/scipy/blob/master/scipy/signal/_peak_finding.py) to find local maxima. The results of argrelmax were then checked over a bounding box to see if the candidate were still a local maximums over a certain area. `argrelmax` was able to weed out some points but not enough to make the checking of the bounding box (O(n^2) yikes) doable. It took over 30 seconds to check the bounding box for all these supposed "local maxima".

`argrelmax` only lets you check 1 axis at a time; I could only find local maxima in terms of north and south or east and west but not both at the same time. I tried experimenting with the order (aka the amount of indices to check over) which made `argrelmax` slower and still did not cut down the points enough. Inspired by the source code for `argrelmax`, I was able to write a function that looked at both axes in in my matrix simultaneously using vectorized operations. This significantly decreased the amount of points returned (.3% of the original) and thus a lot less points to have to check the bounding box. The time of finding local maxima decreased from over 30 seconds to just under 4.
## Filtering
The local maxima are then filtered by a minimum elevation (below sea level isn't great for watching sunsets) and by a check to verify they are not obstructed to the west. 
## Scoring and Ranking
The remaining local maxima are scored by elevation relative to the starting elevation. They are also given a score for how much they resemble a cliff. The cliff score adds diversity to the points instead of just finding the tallest peaks. 

# <a name="display"></a>Displaying Results
The results are plotted on a Google map. Each (latitude, longitude) is queried for in the flickr api with the tag "sunset". When the user clicks on a result pin, the pin will change to a sun icon and show the corresponding pictures in a carousel. 
![App Screen Shot2](/static/screenshot2.png)
