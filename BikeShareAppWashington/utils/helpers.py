import urllib  # Import module for working with URLs
import json  # Import module for working with JSON data
import pandas as pd  # Import pandas for data manipulation
import folium  # Import folium for creating interactive maps
import datetime as dt  # Import datetime for working with dates and times
from geopy.distance import geodesic  # Import geodesic for calculating distances
from geopy.geocoders import Nominatim  # Import Nominatim for geocoding
import streamlit as st  # Import Streamlit for creating web apps
import numpy as np

@st.cache_data  # Cache the function's output to improve performance

## Read Data Function
# Define the function to query station status from a given URL
def query_station_status(url):
    with urllib.request.urlopen(url) as data_url:  # Open the URL
        data = json.loads(data_url.read().decode())  # Read and decode the JSON data

    properties_list = [feature['properties'] for feature in data['features']] # Extract the 'properties' from each feature
    df = pd.DataFrame(properties_list)  # Convert the data to a DataFrame 
    df = df[df.IS_RENTING == "YES"]  # Filter out stations that are not renting
    df = df[df.IS_RETURNING == "YES"]  # Filter out stations that are not returning
    df = df.drop_duplicates(['STATION_ID', 'LAST_REPORTED'])  # Remove duplicate records
    df = df.dropna(subset = ['LAST_REPORTED']) #WL: drop empty rows of required columns 
    df.LAST_REPORTED = df.LAST_REPORTED.map(lambda x: dt.datetime.fromtimestamp(x / 1000, tz = dt.timezone.utc)) 
    df = df.rename(columns = {'GIS_LAST_MOD_DTTM': 'TIME'})  # Add the last updated time to the DataFrame
    df.TIME = df.TIME.map(lambda x: dt.datetime.fromtimestamp(x / 1000, tz = dt.timezone.utc))  # Convert timestamps to datetime (note original is in milliseconds)
    df = df.set_index('TIME')  # Set the time as the index
    df.index = df.index.tz_convert('UTC')  # Localize the index to UTC

    return df  # Return the DataFrame

## Marker Colour Functions
# Function to determine marker color based on the number of bikes available
def get_marker_color(num_bikes_available):
    if num_bikes_available > 3:
        return 'green'
    elif 0 < num_bikes_available <= 3:
        return 'yellow'
    else:
        return 'red'
    
# Function to determine marker colour based on NUM_DOCKS_DISABLED / NUM_BIKES_DISABLED
def get_marker_color_repair(num_things_disabled):
    if sum(num_things_disabled) > 3:
        return "red"
    elif 0 < sum(num_things_disabled) <= 3:
        return "yellow"
    else:
        return "green"

## Get Location Functions
# Define the function to geocode an address
def geocode(address):
    geolocator = Nominatim(user_agent="clicked-demo")  # Create a geolocator object
    location = geolocator.geocode(address)  # Geocode the address
    if location is None:
        return ''  # Return an empty string if the address is not found
    else:
        return (location.latitude, location.longitude)  # Return the latitude and longitude


## Availability Functions
# Define the function to get bike availability near a location
def get_bike_availability(latlon, df, input_bike_modes):

    df = df.copy().reset_index(drop=True) #resets index

    # Compute distances correctly with row positions
    df["distance"] = df.apply(
        lambda row: geodesic(latlon, (row["LATITUDE"], row["LONGITUDE"])).km,
        axis=1
    )
    # Filter by bike types correctly
    if len(input_bike_modes) == 0 or len(input_bike_modes) == 2:
        available = df[(df["NUM_BIKES_AVAILABLE"] > 0) | (df["NUM_EBIKES_AVAILABLE"] > 0)]
    else:
        mode = input_bike_modes[0]
        if mode == "ebike":
            available = df[df["NUM_EBIKES_AVAILABLE"] > 0]
        else:
            available = df[df["NUM_BIKES_AVAILABLE"] > 0]

     # Choose closest
    closest = available.loc[available["distance"].idxmin()]

    return [closest["OBJECTID"], closest["LATITUDE"], closest["LONGITUDE"]]  # Return the chosen station

# Define the function to get dock availability near a location
def get_dock_availability(latlon, df):

    df = df.copy().reset_index(drop=True)

    df["distance"] = df.apply(
        lambda row: geodesic(latlon, (row["LATITUDE"], row["LONGITUDE"])).km,
        axis=1
    )

    available = df[df["NUM_DOCKS_AVAILABLE"] > 0]

    closest = available.loc[available["distance"].idxmin()]

    return [closest["OBJECTID"], closest["LATITUDE"], closest["LONGITUDE"]]

## Unavailability Functions
# Define the function to get bike AND/OR dock unavailability near a location for repair
def get_thing_unavailability(latlon, df, choice_list, isdriving):
    df = df.copy().reset_index(drop=True) #resets index

    # Compute distances correctly with row positions
    df["distance"] = df.apply(
        lambda row: geodesic(latlon, (row["LATITUDE"], row["LONGITUDE"])).km,
        axis=1
    )

    # Find closest station based on user selection
    if choice_list == ["bike"]:
        available = df[df["NUM_BIKES_DISABLED"] > 0]
    elif choice_list == ["dock"]:
        available = df[df["NUM_DOCKS_DISABLED"] > 0]
    else: #if both dock and bike chosen (force user to make an input in main page)
        available = df[(df["NUM_BIKES_DISABLED"] > 0) | (df["NUM_DOCKS_DISABLED"] > 0)]

    if available.empty:
        return None

    if isdriving:
        min_drive_distance_km = 0.5
        available_driving = available[available["distance"] >= min_drive_distance_km]
        if not available_driving.empty:
            available = available_driving

    closest = available.loc[available["distance"].idxmin()] # choose closest

    return [closest["OBJECTID"], closest["LATITUDE"], closest["LONGITUDE"]]  # Return the chosen station


def get_repair_route_greedy(latlon, df, choice_list, isdriving, max_stops, round_trip):
    df = df.copy().reset_index(drop=True)

    candidates = df
    if choice_list == ["bike"]:
        candidates = candidates[candidates["NUM_BIKES_DISABLED"] > 0]
    elif choice_list == ["dock"]:
        candidates = candidates[candidates["NUM_DOCKS_DISABLED"] > 0]
    else:
        candidates = candidates[(candidates["NUM_BIKES_DISABLED"] > 0) | (candidates["NUM_DOCKS_DISABLED"] > 0)]

    if candidates.empty:
        return [], 0.0

    route = []
    total_distance_km = 0.0
    current_point = latlon
    remaining = candidates.copy()

    for i in range(int(max_stops)):
        remaining = remaining.copy()
        remaining["distance"] = remaining.apply(
            lambda row: geodesic(current_point, (row["LATITUDE"], row["LONGITUDE"])).km,
            axis=1
        )

        if remaining.empty:
            break

        if isdriving and i == 0:
            min_drive_distance_km = 0.5
            remaining_driving = remaining[remaining["distance"] >= min_drive_distance_km]
            if not remaining_driving.empty:
                remaining = remaining_driving

        next_stop = remaining.loc[remaining["distance"].idxmin()]
        leg_km = float(next_stop["distance"])
        total_distance_km += leg_km

        route.append({
            "objectid": int(next_stop["OBJECTID"]),
            "lat": float(next_stop["LATITUDE"]),
            "lon": float(next_stop["LONGITUDE"]),
            "bikes_disabled": int(next_stop["NUM_BIKES_DISABLED"]),
            "docks_disabled": int(next_stop["NUM_DOCKS_DISABLED"]),
            "distance_from_prev_km": leg_km,
        })

        current_point = (float(next_stop["LATITUDE"]), float(next_stop["LONGITUDE"]))
        remaining = remaining.drop(index=next_stop.name)

    if round_trip and route:
        total_distance_km += float(geodesic(current_point, latlon).km)

    return route, float(round(total_distance_km, 3))


## Route Function
import requests  # Import requests for making HTTP requests

# Define the function to run OSRM and get route coordinates and duration
def run_osrm(chosen_station, iamhere):
    start = "{},{}".format(iamhere[1], iamhere[0])  # Format the start coordinates (OSRM uses longitude, latitude)
    end = "{},{}".format(chosen_station[2], chosen_station[1])  # Format the end coordinates
    url = 'http://router.project-osrm.org/route/v1/driving/{};{}?geometries=geojson'.format(start, end)  # Create the OSRM API URL

    headers = {'Content-type': 'application/json'}
    r = requests.get(url, headers=headers)  # Make the API request
    print("Calling API ...:", r.status_code)  # Print the status code

    routejson = r.json()  # Parse the JSON response
    coordinates = []
    i = 0
    lst = routejson['routes'][0]['geometry']['coordinates']
    while i < len(lst):
        coordinates.append([lst[i][1], lst[i][0]])  # Extract coordinates
        i = i + 1
    duration = round(routejson['routes'][0]['duration'] / 60, 1)  # Convert duration to minutes

    return coordinates, duration  # Return the coordinates and duration


## Algorithm Functions - separate from old app functions.