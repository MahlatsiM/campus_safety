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

@st.cache_data(ttl=3600)  # cache route coordinates for 1 hour
def get_route_osrm_cached(start, end):
    """Fetch route coordinates from OSRM or return cached result"""
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"
    resp = requests.get(url).json()
    coords = resp['routes'][0]['geometry']['coordinates']
    return [(lat, lon) for lon, lat in coords]

# ---------------------------
# Main App
# ---------------------------
st.set_page_config(page_title="Campus Safety Dashboard", layout="wide")
st.title("Campus Safety Live Dashboard")

# Auto-refresh every 30 seconds
st_autorefresh(interval=15 * 1000)

# Fetch latest data
safety_reports, safe_routes, loadshedding = get_data()

# ---------------------------
# Plot 1: Safe vs Risky Routes
# ---------------------------
st.subheader("Safe vs Risky Routes on Roads")
fig_routes = go.Figure()

# Limit number of routes to display to avoid lag
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

# ---------------------------
# Plot 2: Distribution of Safety Reports (Pie)
# ---------------------------
st.subheader("Distribution of Safety Report Categories")
category_counts = safety_reports['category'].value_counts().reset_index()
category_counts.columns = ['category', 'count']
category_counts["color"] = category_counts["category"].apply(severity_to_color)

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

# ---------------------------
# Plot 3: Safety Reports by Location (Map with clustering)
# ---------------------------
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

# ---------------------------
# Plot 4: Time-Series Trend
# ---------------------------
st.subheader("Safety Reports Over Time")
safety_reports['timestamp'] = pd.to_datetime(safety_reports['timestamp'])
time_series = safety_reports.groupby(pd.Grouper(key='timestamp', freq='1H')).size().reset_index(name='count')

fig_ts = px.line(time_series, x='timestamp', y='count', title="Safety Reports Over Time")
st.plotly_chart(fig_ts, use_container_width=True)

# ---------------------------
# Plot 5: Overlay Loadshedding & Safety Reports
# ---------------------------
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

# Loadshedding as shaded bars
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
