from utils.helpers import *
import streamlit as st
import folium
from streamlit_folium import folium_static

#set page icon
st.set_page_config(page_title="Users", page_icon="🚲")

#URL for update
url = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Transportation_Bikes_Trails_WebMercator/MapServer/5/query?outFields=*&where=1%3D1&f=geojson"  



st.title('DC Bike Share Station Status')
st.markdown('This dashboard tracks bike availability at each bike share in Washington DC.')

#save raw data in variables
data = query_station_status(url)


# Initialize variables for user input and state
iamhere = 0
iamhere_return = 0
findmeabike = False
findmeadock = False
input_bike_modes = []

#display columns
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label = "Bikes Available Now", value = sum(data['NUM_BIKES_AVAILABLE']))
    st.metric(label = "E-Bikes Available Now", value = sum(data['NUM_EBIKES_AVAILABLE']))
with col2:
    st.metric(label = "Station w Available Bikes", value = len(data[data['NUM_BIKES_AVAILABLE'] > 0]))
    st.metric(label = "Stations w Available E-Bikes", value=len(data[data['NUM_EBIKES_AVAILABLE'] > 0]))  # Display number of stations with available e-bikes
with col3:
    st.metric(label="Stations w Empty Docks", value=len(data[data['NUM_DOCKS_AVAILABLE'] > 0]))

with st.sidebar: 
    bike_method = st.selectbox("Are you looking to rent a bike?", ("Rent", "Return"))
    if bike_method == "Rent":
        input_bike_modes = st.multiselect(
            'What kind of bikes are you looking to rent?',
            ["ebike", "mechanical"]
        )
        st.header("Where are you located?")
        input_street = st.text_input("Street", "")  # Text input for street
        input_city = st.text_input("City", "Washington DC")  # Text input for city
        input_country = st.text_input("Country", "USA")  # Text input for country
        findmeabike = st.button("Find me a bike", type = "primary")
        
        if findmeabike:
            if input_street != "":
                iamhere = geocode(input_street + " " + input_city + " " + input_country)
                if iamhere == '':
                    st.subheader(':red[Input address is not valid!]')
            else:
                st.subheader(':red[Please input your location.]')

    elif bike_method == "Return":
        input_bike_modes = st.multiselect(
            'What kind of bikes are you looking to return?',
            ["ebike", "mechanical"]
        )
        st.subheader('Where are you located?')
        input_street_return = st.text_input("Street", "")  # Text input for street for return
        input_city_return = st.text_input("City", "Washington DC")  # Text input for city for return
        input_country_return = st.text_input("Country", "USA")  # Text input for country for return
        findmeadock = st.button("Find me a dock!", type="primary")  # Button to find a dock
        if findmeadock:
            if input_street_return != "":
                iamhere_return = geocode(input_street_return + " " + input_city_return + " " + input_country_return)
                if iamhere_return == '':
                    st.subheader(':red[Input address is not valid!]')
            else:
                st.subheader(':red[Please input your location.]')

# Initial map setup based on user selection
if bike_method == "Return" and findmeadock == False:
    center = [38.897095, -77.006332]  # Coordinates for DC
    m = folium.Map(location=center, zoom_start=13, tiles='cartodbpositron')  # Create a map with a grey background
    for _, row in data.iterrows():
        marker_color = get_marker_color(row['NUM_BIKES_AVAILABLE'])  # Determine marker color based on bikes available
        n_mech_bikes_available = row['NUM_BIKES_AVAILABLE'] - row['NUM_EBIKES_AVAILABLE'] # Get total number of bikes
        folium.CircleMarker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            radius=2,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.7,
            popup=folium.Popup(f"Station ID: {row['OBJECTID']}<br>"
                                f"Total Bikes Available: {row['NUM_BIKES_AVAILABLE']}<br>"
                                f"Mechanical Bike Available: {n_mech_bikes_available}<br>"
                                f"eBike Available: {row['NUM_EBIKES_AVAILABLE']}<br>"
                                f"Accepted Rental Methods: {row['RENTAL_METHODS']}", max_width=300)
        ).add_to(m)
    folium_static(m)  # Display the map in the Streamlit app


if bike_method == "Rent" and findmeabike == False:
    center = [38.897095, -77.006332]  # Coordinates for DC
    m = folium.Map(location=center, zoom_start=13, tiles='cartodbpositron')  # Create a map with a grey background
    for _, row in data.iterrows():
        marker_color = get_marker_color(row['NUM_BIKES_AVAILABLE'])  # Determine marker color based on bikes available
        n_mech_bikes_available = row['NUM_BIKES_AVAILABLE'] - row['NUM_EBIKES_AVAILABLE'] # Get total number of bikes
        folium.CircleMarker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            radius=2,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.7,
            popup=folium.Popup(f"Station ID: {row['OBJECTID']}<br>"
                                f"Total Bikes Available: {row['NUM_BIKES_AVAILABLE']}<br>"
                                f"Mechanical Bike Available: {n_mech_bikes_available}<br>"
                                f"eBike Available: {row['NUM_EBIKES_AVAILABLE']}<br>"
                                f"Accepted Rental Methods: {row['RENTAL_METHODS']}", max_width=300)
        ).add_to(m)
    folium_static(m)  # Display the map in the Streamlit app

# Logic for finding a bike
if findmeabike:
    if input_street != "":
        if iamhere != "":
            chosen_station = get_bike_availability(iamhere, data, input_bike_modes)  # Get bike availability (location coordinates, raw data, bike mode list)
            print(f"the chosen station is: {chosen_station[0]}")
            center = iamhere  # Center the map on user's location
            m1 = folium.Map(location=center, zoom_start=16, tiles='cartodbpositron')  # Create a detailed map
            for _, row in data.iterrows():
                marker_color = get_marker_color(row['NUM_BIKES_AVAILABLE'])  # Determine marker color based on bikes available
                n_mech_bikes_available = row['NUM_BIKES_AVAILABLE'] - row['NUM_EBIKES_AVAILABLE'] # Get total number of bikes
                folium.CircleMarker(
                    location=[row['LATITUDE'], row['LONGITUDE']],
                    radius=2,
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.7,
                    popup=folium.Popup(f"Station ID: {row['OBJECTID']}<br>"
                                f"Total Bikes Available: {row['NUM_BIKES_AVAILABLE']}<br>"
                                f"Mechanical Bike Available: {n_mech_bikes_available}<br>"
                                f"eBike Available: {row['NUM_EBIKES_AVAILABLE']}<br>"
                                f"Accepted Rental Methods: {row['RENTAL_METHODS']}", max_width=300)
                ).add_to(m1)
            folium.Marker(
                location=iamhere,
                popup="You are here.",
                icon=folium.Icon(color="blue", icon="person", prefix="fa")
            ).add_to(m1)
            folium.Marker(location=(chosen_station[1], chosen_station[2]),
                          popup="Rent your bike here.",
                          icon=folium.Icon(color="red", icon="bicycle", prefix="fa")
                          ).add_to(m1)
            coordinates, duration = run_osrm(chosen_station, iamhere)  # Get route coordinates and duration
            folium.PolyLine(
                locations=coordinates,
                color="blue",
                weight=5,
                tooltip="it'll take you {} to get here.".format(duration),
            ).add_to(m1)
            folium_static(m1)  # Display the map in the Streamlit app
            with col3:
                st.metric(label=":green[Travel Time (min)]", value=duration)  # Display travel time

# Logic for finding a dock
elif findmeadock:
    if input_street_return != "":
        if iamhere_return != "":
            chosen_station = get_dock_availability(iamhere_return, data)  # Get dock availability (id, lat, lon)
            center = iamhere_return  # Center the map on user's location
            m1 = folium.Map(location=center, zoom_start=16, tiles='cartodbpositron')  # Create a detailed map
            for _, row in data.iterrows():
                marker_color = get_marker_color(row['NUM_BIKES_AVAILABLE'])  # Determine marker color based on bikes available
                n_mech_bikes_available = row['NUM_BIKES_AVAILABLE'] - row['NUM_EBIKES_AVAILABLE'] # Get total number of bikes
                folium.CircleMarker(
                    location=[row['LATITUDE'], row['LONGITUDE']],
                    radius=2,
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.7,
                    popup=folium.Popup(f"Station ID: {row['OBJECTID']}<br>"
                                f"Total Bikes Available: {row['NUM_BIKES_AVAILABLE']}<br>"
                                f"Mechanical Bike Available: {n_mech_bikes_available}<br>"
                                f"eBike Available: {row['NUM_EBIKES_AVAILABLE']}<br>"
                                f"Accepted Rental Methods: {row['RENTAL_METHODS']}", max_width=300)
                ).add_to(m1)
            folium.Marker(
                location=iamhere_return,
                popup="You are here.",
                icon=folium.Icon(color="blue", icon="person", prefix="fa")
            ).add_to(m1)
            folium.Marker(location=(chosen_station[1], chosen_station[2]),
                          popup="Return your bike here.",
                          icon=folium.Icon(color="red", icon="bicycle", prefix="fa")
                          ).add_to(m1)
            coordinates, duration = run_osrm(chosen_station, iamhere_return)  # Get route coordinates and duration
            folium.PolyLine(
                locations=coordinates,
                color="blue",
                weight=5,
                tooltip="it'll take you {} to get here.".format(duration),
            ).add_to(m1)
            folium_static(m1)  # Display the map in the Streamlit app
            with col3:
                st.metric(label=":green[Travel Time (min)]", value=duration)  # Display travel time