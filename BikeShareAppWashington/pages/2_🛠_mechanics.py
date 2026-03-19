from utils.helpers import *
import streamlit as st
import folium
from streamlit_folium import folium_static



#set page icon
st.set_page_config(page_title="Users", page_icon="🛠")

#URL for update
url = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Transportation_Bikes_Trails_WebMercator/MapServer/5/query?outFields=*&where=1%3D1&f=geojson"

#set page header
st.title('DC Bike Repair Status')
st.markdown('This dashboard tracks bike and docks in need to repair in Washington DC.')

#save raw data in variables
data = query_station_status(url)

#initialise values
dc_init = [38.897095, -77.006332] # Coordinates for DC
confirm_local = False # to generate map

#set columns
col1, col2 = st.columns(2)
with col1:
    st.metric(label = "Bikes Disabled Now", value = sum(data['NUM_BIKES_DISABLED']))

with col2:
    st.metric(label = "Docks Disabled Now", value = sum(data['NUM_DOCKS_DISABLED']))

#set side bar
with st.sidebar:
    #generate map AFTER choosing dock or bike and deciding colour based on that AND then total amount if both. 0 = green, 1-3 = yellow, 3+ = red
    #select repair mode
    input_repair_modes = st.multiselect(
            label = "Select choice of repair",
            options = ["bike", "dock"])
    
    #select location
    st.header("Where are you located?")
    input_street = st.text_input("Street", "")  # Text input for street
    input_city = st.text_input("City", "Washington DC")  # Text input for city
    input_country = st.text_input("Country", "USA")  # Text input for country
    
    isdriving = st.checkbox("I am driving!") # Option input for driving

    select_repair_algo = st.selectbox(
        "How would you like to go about repairing?",
        ("Closest location", "Algorithm (multi-stop)")
    )

    if select_repair_algo == "Algorithm (multi-stop)":
        st.header("Route settings")
        max_stops = st.number_input("Max stops per run", min_value=1, max_value=25, value=3, step=1)
        round_trip = st.checkbox("Round trip (return to start)", value=False)
    else:
        max_stops = 1
        round_trip = False

    confirm_local = st.button("Find me!", type = "primary") # Confirm location choices button
    if confirm_local:
        # st.markdown(f"Showing map for {input_street} {input_city} {input_country}") # move this to display with map later 
        if input_street != "":
                iamhere = geocode(input_street + " " + input_city + " " + input_country)
                if iamhere == '':
                    st.subheader(':red[Input address is not valid!]')
        else:
            st.subheader(':red[Please input your location.]')
    
## Initial map setup based on user selection ##
#Logic for finding bike w/o location
if input_repair_modes == ["bike"] and confirm_local == False:
    center = dc_init  #center map on DC
    m = folium.Map(location=center, zoom_start=13, tiles='cartodbpositron')  # Create a map with a grey background
    for _, row in data.iterrows():
        remaining_capacity = row['CAPACITY'] - row['NUM_BIKES_DISABLED'] - row['NUM_DOCKS_DISABLED'] # Calculate remaining capacity  
        if remaining_capacity > 3: 
            marker_color = get_marker_color_repair([row['NUM_BIKES_DISABLED']])  # Determine marker color based on docks bikes disabled
        else:
            marker_color = "black" # Repair immediately after total capacity of stations drops to 3 and under
        folium.CircleMarker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            radius=2,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.7,
            popup=folium.Popup(f"Station ID: {row['OBJECTID']}<br>"
                                f"Total Bikes Disabled: {row['NUM_BIKES_DISABLED']}<br>"
                                f"Total Docks Disabled: {row['NUM_DOCKS_DISABLED']}<br>"
                                f"Total Remaining Capacity: {remaining_capacity}", max_width=300)
        ).add_to(m)
    folium_static(m)  # Display the map in the Streamlit app

#Logic for finding dock w/o location
if input_repair_modes == ["dock"] and confirm_local == False:
    center = dc_init  #center map on DC
    m = folium.Map(location=center, zoom_start=13, tiles='cartodbpositron')  # Create a map with a grey background
    for _, row in data.iterrows():
        remaining_capacity = row['CAPACITY'] - row['NUM_BIKES_DISABLED'] - row['NUM_DOCKS_DISABLED'] # Calculate remaining capacity  
        if remaining_capacity > 3: 
            marker_color = get_marker_color_repair([row['NUM_BIKES_DISABLED']])  # Determine marker color based on docks bikes disabled
        else:
            marker_color = "black" # Repair immediately after total capacity of stations drops to 3 and under
        folium.CircleMarker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            radius=2,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.7,
            popup=folium.Popup(f"Station ID: {row['OBJECTID']}<br>"
                                f"Total Bikes Disabled: {row['NUM_BIKES_DISABLED']}<br>"
                                f"Total Docks Disabled: {row['NUM_DOCKS_DISABLED']}<br>"
                                f"Total Remaining Capacity: {remaining_capacity}", max_width=300)
        ).add_to(m)
    folium_static(m)  # Display the map in the Streamlit app

#Logic if no input it both selected(includes both bike and dock)
if (("dock" in input_repair_modes and "bike" in input_repair_modes) or not input_repair_modes) and confirm_local == False:
    center = dc_init  #center map on DC
    m = folium.Map(location=center, zoom_start=13, tiles='cartodbpositron')  # Create a map with a grey background
    for _, row in data.iterrows():
        remaining_capacity = row['CAPACITY'] - row['NUM_BIKES_DISABLED'] - row['NUM_DOCKS_DISABLED'] # Calculate remaining capacity  
        if remaining_capacity > 3: 
            marker_color = get_marker_color_repair([row['NUM_BIKES_DISABLED']])  # Determine marker color based on docks bikes disabled
        else:
            marker_color = "black" # Repair immediately after total capacity of stations drops to 3 and under
        folium.CircleMarker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            radius=2,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.7,
            popup=folium.Popup(f"Station ID: {row['OBJECTID']}<br>"
                                f"Total Bikes Disabled: {row['NUM_BIKES_DISABLED']}<br>"
                                f"Total Docks Disabled: {row['NUM_DOCKS_DISABLED']}<br>"
                                f"Total Remaining Capacity: {remaining_capacity}", max_width=300)
        ).add_to(m)
    folium_static(m)  # Display the map in the Streamlit app


## Map after location confirmed ##
#Logic for finding bike w/ location
if input_repair_modes and confirm_local == True:
    if input_street != "":
        if iamhere != "":
            center = iamhere #centre map on current location
            if select_repair_algo == "Closest location":
                chosen_station = get_thing_unavailability(iamhere, data, input_repair_modes, isdriving)  # (id, lat, lon) or None
            else:
                route_stops, total_distance_km = get_repair_route_greedy(
                    iamhere,
                    data,
                    input_repair_modes,
                    isdriving,
                    max_stops,
                    round_trip
                )

            m1 = folium.Map(location=center, zoom_start=16, tiles='cartodbpositron')

            for _, row in data.iterrows():
                remaining_capacity = row['CAPACITY'] - row['NUM_BIKES_DISABLED'] - row['NUM_DOCKS_DISABLED']  # Calculate remaining capacity
                if remaining_capacity > 3:
                    if input_repair_modes == ["bike"]:
                        marker_color = get_marker_color_repair([row['NUM_BIKES_DISABLED']])
                    elif input_repair_modes == ["dock"]:
                        marker_color = get_marker_color_repair([row['NUM_DOCKS_DISABLED']])
                    else:
                        marker_color = get_marker_color_repair([row['NUM_BIKES_DISABLED'], row['NUM_DOCKS_DISABLED']])
                else:
                    marker_color = "black"  # Repair immediately after total capacity of stations drops to 3 and under

                folium.CircleMarker(
                    location=[row['LATITUDE'], row['LONGITUDE']],
                    radius=2,
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.7,
                    popup=folium.Popup(
                        f"Station ID: {row['OBJECTID']}<br>"
                        f"Total Bikes Disabled: {row['NUM_BIKES_DISABLED']}<br>"
                        f"Total Docks Disabled: {row['NUM_DOCKS_DISABLED']}<br>"
                        f"Total Remaining Capacity: {remaining_capacity}",
                        max_width=300
                    )
                ).add_to(m1)

            folium.Marker(
                location=iamhere,
                popup="You are here.",
                icon=folium.Icon(color="blue", icon="person", prefix="fa")
            ).add_to(m1)

            if select_repair_algo == "Closest location":
                if chosen_station is None:
                    st.info("No stations currently match your repair selection (0 disabled found).")
                    folium_static(m1)
                else:
                    folium.Marker(
                        location=(chosen_station[1], chosen_station[2]),
                        popup="Repair here.",
                        icon=folium.Icon(color="red", icon="wrench", prefix="fa")
                    ).add_to(m1)

                    coordinates, duration = run_osrm(chosen_station, iamhere)
                    folium.PolyLine(
                        locations=coordinates,
                        color="blue",
                        weight=5,
                        tooltip="it'll take you {} to get here.".format(duration),
                    ).add_to(m1)

                    folium_static(m1)
                    with col2:
                        st.metric(label=":green[Travel Time (min)]", value=duration)
            else:
                if len(route_stops) == 0:
                    st.info("No stations currently match your repair selection (0 disabled found).")
                    folium_static(m1)
                else:
                    polyline_points = [iamhere]
                    for idx, stop in enumerate(route_stops, start=1):
                        polyline_points.append((stop["lat"], stop["lon"]))
                        folium.Marker(
                            location=(stop["lat"], stop["lon"]),
                            popup=folium.Popup(
                                f"Stop {idx}<br>"
                                f"Station ID: {stop['objectid']}<br>"
                                f"Bikes Disabled: {stop['bikes_disabled']}<br>"
                                f"Docks Disabled: {stop['docks_disabled']}<br>"
                                f"Leg Distance (km): {round(stop['distance_from_prev_km'], 2)}",
                                max_width=300
                            ),
                            icon=folium.Icon(color="red", icon="wrench", prefix="fa")
                        ).add_to(m1)

                    if round_trip:
                        polyline_points.append(iamhere)

                    folium.PolyLine(
                        locations=polyline_points,
                        color="blue",
                        weight=5,
                        tooltip="Total distance (km): {}".format(round(total_distance_km, 2)),
                    ).add_to(m1)

                    folium_static(m1)
                    with col2:
                        st.metric(label=":green[Stops]", value=len(route_stops))
                        st.metric(label=":green[Total distance (km)]", value=round(total_distance_km, 2))