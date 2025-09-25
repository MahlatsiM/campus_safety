# app.py
import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
import requests
import ast
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from geopy.distance import geodesic
import time
import bcrypt


# ---------------------------
# Import authentication and access control
# ---------------------------
from auth.auth import authenticate, register_user
from auth.access_control import is_user_blocked, block_user

# ---------------------------
# Database connection with caching
# ---------------------------
@st.cache_data(ttl=10)
def get_data():
    conn = psycopg2.connect(
        host="localhost",
        database="campus_safety",
        user="postgres",
        password="Mahlatsi#0310"
    )
    safety_reports = pd.read_sql("SELECT * FROM safety_reports", conn)
    safe_routes = pd.read_sql("SELECT * FROM safe_routes", conn)
    loadshedding = pd.read_sql("SELECT * FROM loadshedding", conn)
    conn.close()
    
    # Convert origin/destination string tuples to actual tuples
    if 'origin' in safe_routes.columns and 'destination' in safe_routes.columns:
        safe_routes['origin_coords'] = safe_routes['origin'].apply(ast.literal_eval)
        safe_routes['destination_coords'] = safe_routes['destination'].apply(ast.literal_eval)
    
    return safety_reports, safe_routes, loadshedding

# ---------------------------
# Helper functions
# ---------------------------
def risk_to_color(risk):
    if risk >= 0.75:
        return "red"
    elif risk >= 0.4:
        return "yellow"
    else:
        return "green"

def severity_to_color(category):
    severity_colors = {     
        "harassment": "yellow",
        "accident": "orange",  
        "theft": "red",        
        "suspicious_activity": "green",
        "other": "gray"       
    }
    return severity_colors.get(category, "lightgray")

@st.cache_data(ttl=3600)
def get_route_osrm_cached(start, end):
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"
    resp = requests.get(url).json()
    coords = resp['routes'][0]['geometry']['coordinates']
    return [(lat, lon) for lon, lat in coords]

# ---------------------------
# Temporal Denial-of-Service Check
# ---------------------------
def check_risk_for_user(location, safety_reports, safe_routes, risk_threshold=0.5, distance_threshold_m=500):
    user_lat, user_lon = location
    
    # Check nearby high-risk safety reports
    for _, row in safety_reports.iterrows():
        incident_loc = (row['lat'], row['lon'])
        distance = geodesic(location, incident_loc).meters
        if distance <= distance_threshold_m and row['category'] in ["theft", "harassment", "accident"]:
            return True, f"Near high-risk incident ({row['category']}) within {int(distance)}m"

    # Check nearby high-risk routes
    for _, row in safe_routes.iterrows():
        if row['risk_score'] >= risk_threshold:
            origin = row['origin_coords']
            dest = row['destination_coords']
            mid_point = ((origin[0] + dest[0]) / 2, (origin[1] + dest[1]) / 2)
            distance = geodesic(location, mid_point).meters
            if distance <= distance_threshold_m:
                return True, f"Near high-risk route (risk={row['risk_score']:.2f}) within {int(distance)}m"

    return False, None

# ---------------------------
# Main App
# ---------------------------
st.set_page_config(page_title="Campus Safety Dashboard", layout="wide")
st.title("Campus Safety Dashboard")

# ---------------------------
# Login/Register Flow
# ---------------------------
# Streamlit session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

auth_choice = st.sidebar.radio("Select an option", ["Login", "Register"])
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if auth_choice == "Register" and st.sidebar.button("Register"):
    if username and password:
        success, msg = register_user(username, password)  # always returns tuple
        if success:
            st.success(msg)
        else:
            st.error(msg)
    else:
        st.warning("Enter username and password to register")

elif auth_choice == "Login" and st.sidebar.button("Login"):
    if username and password:
        if is_user_blocked(username):
            st.error("You are temporarily blocked due to repeated failed attempts.")
        elif authenticate(username, password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid username or password")
    else:
        st.warning("Enter username and password to login")

import streamlit as st
import streamlit.components.v1 as components

# JavaScript snippet to get device location
components.html(
    """
    <script>
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            document.body.innerHTML = '<p id="coords">' + lat + ',' + lon + '</p>';
        },
        function(error) {
            document.body.innerHTML = '<p id="coords">error</p>';
        }
    );
    </script>
    <div id="coords">waiting...</div>
    """,
    height=100,
)

# User Location Input (auto-detect)
st.sidebar.subheader("Your Location")
default_lat, default_lon = -28.75, 24.75

try:
    user_query_params = st.query_params
    lat = float(user_query_params.get("lat", [default_lat])[0])
    lon = float(user_query_params.get("lon", [default_lon])[0])
except Exception:
    lat, lon = default_lat, default_lon

user_location = (lat, lon)
st.sidebar.write(f"Using location: {lat}, {lon}")



# Fetch latest data
safety_reports, safe_routes, loadshedding = get_data()

# Check if user should be blocked temporarily
if is_user_blocked(st.session_state['username']):
    st.error("Access temporarily denied due to high-risk location or recent block. Try again later.")
    st.stop()

blocked, reason = check_risk_for_user(user_location, safety_reports, safe_routes)
if blocked:
    block_user(st.session_state['username'], duration_seconds=300)  # 5 minutes
    st.error(f"Access temporarily denied: {reason}. Try again later.")
    st.stop()

# ---------------------------
# Dashboard Plots
# ---------------------------
# 1. Safe vs Risky Routes
st.subheader("Safe vs Risky Routes on Roads")
fig_routes = go.Figure()
max_routes = 50
for _, row in safe_routes.tail(max_routes).iterrows():
    path = get_route_osrm_cached(row['origin_coords'], row['destination_coords'])
    lats, lons = zip(*path)
    fig_routes.add_trace(go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode="lines",
        line=dict(width=3, color=risk_to_color(row['risk_score'])),
        hovertext=f"Origin: {row['origin']}<br>Destination: {row['destination']}<br>Risk: {row['risk_score']:.2f}<br>Time: {row['timestamp']}",
        hoverinfo="text",
        showlegend=False
    ))
fig_routes.update_layout(
    mapbox=dict(
        style="open-street-map",
        zoom=13,
        center=dict(
            lat=safe_routes['origin_coords'].apply(lambda x: x[0]).mean(),
            lon=safe_routes['origin_coords'].apply(lambda x: x[1]).mean()
        )
    ),
    height=600,
    margin=dict(l=0, r=0, t=30, b=0)
)
st.plotly_chart(fig_routes, use_container_width=True)

# 2. Distribution of Safety Reports (Pie)
st.subheader("Distribution of Safety Report Categories")
category_counts = safety_reports['category'].value_counts().reset_index()
category_counts.columns = ['category', 'count']
fig_pie = px.pie(
    category_counts,
    names="category",
    values="count",
    hole=0.35,
    color="category",
    color_discrete_map={c: severity_to_color(c) for c in category_counts['category']}
)
fig_pie.update_traces(textinfo="percent+label")
st.plotly_chart(fig_pie, use_container_width=True)

# 3. Safety Reports by Location
st.subheader("Safety Reports by Location")
fig_map = px.scatter_mapbox(
    safety_reports,
    lat="lat",
    lon="lon",
    color="category",
    hover_name="reporter",
    hover_data=["description", "timestamp"],
    zoom=13,
    height=600,
    color_discrete_map={c: severity_to_color(c) for c in safety_reports['category'].unique()}
)
fig_map.update_layout(mapbox_style="open-street-map", title="Safety Reports by Location")
st.plotly_chart(fig_map, use_container_width=True)

# 4. Time-Series Trend
st.subheader("Safety Reports Over Time")
safety_reports['timestamp'] = pd.to_datetime(safety_reports['timestamp'])
time_series = safety_reports.groupby(pd.Grouper(key='timestamp', freq='1H')).size().reset_index(name='count')
fig_ts = px.line(time_series, x='timestamp', y='count', title="Safety Reports Over Time")
st.plotly_chart(fig_ts, use_container_width=True)

# 5. Overlay Loadshedding & Safety Reports
st.subheader("Loadshedding vs Safety Reports Over Time")
loadshedding['start_time'] = pd.to_datetime(loadshedding['start_time'])
loadshedding['end_time'] = pd.to_datetime(loadshedding['end_time'])
fig_overlay = go.Figure()
fig_overlay.add_trace(go.Scatter(
    x=time_series['timestamp'],
    y=time_series['count'],
    mode='lines+markers',
    name='Safety Reports',
    line=dict(color='red')
))
for _, row in loadshedding.iterrows():
    fig_overlay.add_trace(go.Bar(
        x=[row['start_time'], row['end_time']],
        y=[0, 0],
        width=(row['end_time'] - row['start_time']).total_seconds() / 3600,
        marker_color='yellow',
        opacity=0.3,
        showlegend=False
    ))
fig_overlay.update_layout(
    title="Loadshedding & Safety Reports Timeline",
    xaxis_title="Time",
    yaxis_title="Safety Report Count",
    height=600
)
st.plotly_chart(fig_overlay, use_container_width=True)
