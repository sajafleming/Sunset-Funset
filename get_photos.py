import urllib
import urllib2
import md5
import json
import os

URL_BASE = "https://api.flickr.com/services/rest/?"
URL_PARAMS = ("method=flickr.photos.search&api_key={}&tags={}&lat={}&lon={}"
              "&radius={}&radius_units=mi&format=json&nojsoncallback=1")
PHOTO_URL_TEMPLATE = "https://farm{}.staticflickr.com/{}/{}_{}.jpg"


def request_flickr_data(lat, lon, radius, tag="sunset", api_key=None, auth_token=None):
    """Get flickr images based on latlong"""

    api_key = os.environ['FLICKR_KEY']

    url_params_str = URL_PARAMS.format(api_key, tag, lat, lon, radius, auth_token)
    
    api_sig = build_api_sig(url_params_str, os.environ['FLICKR_SECRET'])

    url_request = URL_BASE + url_params_str + "&api_sig=" + api_sig
    # print url_request    

    response = urllib2.urlopen(url_request)
    data = response.read()

    print data
    return json.loads(data)


def data_to_urls(data):
    """Convert flickr returned data to image urls"""

    image_urls = []

    for photo_info in range(len(data['photos']['photo'])):

        farm_id = data['photos']['photo'][photo_info]['farm']
        server_id = data['photos']['photo'][photo_info]['server']
        photo_id = data['photos']['photo'][photo_info]['id']
        photo_secret = data['photos']['photo'][photo_info]['secret']

        image_urls.append(PHOTO_URL_TEMPLATE.format(farm_id, server_id, photo_id, photo_secret))

    print "IMAGE URLS:"
    print image_urls
    return image_urls


def build_api_sig(url_params_str, secret=None):
    """Generate unique api sig for every request by hashing the params 
    in alphabetical order with the secret using md5()"""

    # split the url params and remove the api sig (the last param)
    url_params_list = url_params_str.split('&')
    # sort params alphabetically
    url_params_list.sort()
    # join params as a string 
    joined_params = "".join(url_params_list)
    # get rid of the equals for params, ex. foo=1 to foo1
    joined_params = joined_params.replace("=", "")
    return md5.new(secret + joined_params).hexdigest()

# data = request_flickr_data(37.7749, -122.4194, .5)
# data_to_urls(data)