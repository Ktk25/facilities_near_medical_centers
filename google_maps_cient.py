import requests
import pandas as pd

from math import sin, cos, sqrt, atan2, radians

from urllib.parse import urlencode

GOOGLE_API_KEY = "XXXXX"

class GoogleMapsClient(object):
    lat = None
    lng = None
    data_type = 'json'
    location_query = None
    api_key = None

    def __init__(self, api_key=None, address_or_postal_code=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if api_key == None:
            raise Exception("API key is required")
        self.api_key = api_key
        self.location_query = address_or_postal_code
        if self.location_query != None:
            self.extract_lat_lng()

    def extract_lat_lng(self, location=None):
        loc_query = self.location_query
        if location != None:
            loc_query = location
        endpoint = f"https://maps.googleapis.com/maps/api/geocode/{self.data_type}"
        params = {"address": loc_query, "key": self.api_key}
        url_params = urlencode(params)
        url = f"{endpoint}?{url_params}"
        r = requests.get(url)
        if r.status_code not in range(200, 299):
            return {}
        latlng = {}
        try:
            latlng = r.json()['results'][0]['geometry']['location']
        except:
            pass
        lat, lng = latlng.get("lat"), latlng.get("lng")
        self.lat = lat
        self.lng = lng
        return lat, lng

    def calc_dist(self, lat, lng, p_lat, p_lng):
        # approximate radius of earth in km
        R = 6373.0

        lat1 = radians(lat)
        lon1 = radians(lng)
        lat2 = radians(p_lat)
        lon2 = radians(p_lng)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c * 0.6214

        return distance

    def search(self, keyword="Mexican food", radius=5000, location=None):
        lat, lng = self.lat, self.lng
        if location != None:
            lat, lng = self.extract_lat_lng(location=location)
        endpoint = f"https://maps.googleapis.com/maps/api/place/nearbysearch/{self.data_type}"
        params = {
            "key": self.api_key,
            "location": f"{lat},{lng}",
            "radius": radius,
            "keyword": keyword
        }
        params_encoded = urlencode(params)
        places_url = f"{endpoint}?{params_encoded}"
        r = requests.get(places_url)
        # print(places_url, r.text)
        if r.status_code not in range(200, 299):
            return {}

        places_dict = {'Place': [], 'Distance_in_miles': [],
                       'Rating': [], 'LAT': [], "LON": []}

        json_result = r.json()

        for place in json_result['results']:
            places_dict['Place'].append(place['name'])

            p_lat, p_lng = place['geometry']['location']['lat'], place['geometry']['location']['lng']

            distance = self.calc_dist(lat, lng, p_lat, p_lng)
            places_dict['Distance_in_miles'].append(distance)

            places_dict['Rating'].append(place['rating'])
            places_dict['LAT'].append(p_lat)
            places_dict['LON'].append(p_lng)

        places_df = pd.DataFrame(places_dict)
        places_df = places_df.sort_values(by=['Distance_in_miles'])

        # return r.json()
        return places_df

    def detail(self, place_id="ChIJlXOKcDC3j4ARzal-5j-p-FY",
               fields=["name", "rating", "formatted_phone_number", "formatted_address"]):
        detail_base_endpoint = f"https://maps.googleapis.com/maps/api/place/details/{self.data_type}"
        detail_params = {
            "place_id": f"{place_id}",
            "fields": ",".join(fields),
            "key": self.api_key
        }
        detail_params_encoded = urlencode(detail_params)
        detail_url = f"{detail_base_endpoint}?{detail_params_encoded}"
        r = requests.get(detail_url)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()