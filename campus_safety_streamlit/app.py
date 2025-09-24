# app.py
import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
import requests
import ast
from datetime import datetime, timedelta
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
# Session tracking for usage monitoring
# ---------------------------
if "session_start" not in st.session_state:
    st.session_state.session_start = datetime.now()
if "refresh_count" not in st.session_state:
    st.session_state.refresh_count = 0
if "page_visits" not in st.session_state:
    st.session_state.page_visits = {"Dashboard": 0, "User Monitoring": 0}

st.session_state.refresh_count += 1

# ---------------------------
# Navigation Menu
# ---------------------------
st.set_page_config(page_title="Campus Safety App", layout="wide")
page = st.sidebar.radio("Navigation", ["Dashboard", "User Monitoring"])

# ---------------------------
# PAGE 1: Dashboard
# ---------------------------
if page == "Dashboard":
    st.title("Campus Safety Live Dashboard")

    st_autorefresh(interval=15 * 1000)
    st.session_state.page_visits["Dashboard"] += 1

    safety_reports, safe_routes, loadshedding = get_data()

    # Plot 1: Safe vs Risky Routes
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

    # Plot 2: Pie
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

    # Plot 3: Map of Reports
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
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)

    # Plot 4: Time-Series Trend
    st.subheader("Safety Reports Over Time")
    safety_reports['timestamp'] = pd.to_datetime(safety_reports['timestamp'])
    time_series = safety_reports.groupby(pd.Grouper(key='timestamp', freq='1H')).size().reset_index(name='count')
    fig_ts = px.line(time_series, x='timestamp', y='count', title="Safety Reports Over Time")
    st.plotly_chart(fig_ts, use_container_width=True)

    # Plot 5: Overlay Loadshedding
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
        fig_overlay.add_vrect(
            x0=row['start_time'], x1=row['end_time'],
            fillcolor="yellow", opacity=0.3, line_width=0
        )
    fig_overlay.update_layout(title="Loadshedding & Safety Reports Timeline")
    st.plotly_chart(fig_overlay, use_container_width=True)

# ---------------------------
# PAGE 2: User Monitoring
# ---------------------------
elif page == "User Monitoring":
    st.title("📊 User Engagement & Usage Monitoring")
    st.session_state.page_visits["User Monitoring"] += 1

    session_duration = datetime.now() - st.session_state.session_start

    col1, col2, col3 = st.columns(3)
    col1.metric("Session Duration", str(session_duration).split('.')[0])
    col2.metric("Refresh Count", st.session_state.refresh_count)
    col3.metric("Pages Visited", sum(st.session_state.page_visits.values()))

    st.subheader("Page Visits Breakdown")
    st.bar_chart(pd.DataFrame.from_dict(st.session_state.page_visits, orient='index', columns=['visits']))

    # Temporal Access Denial (demo: deny if > 10 refreshes in < 2 mins)
    if st.session_state.refresh_count > 10 and session_duration < timedelta(minutes=2):
        st.warning("⏳ Access temporarily denied to prevent overexposure. Please take a short break.")
        st.stop()
