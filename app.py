import streamlit as st
import numpy as np
from typhoon_map import create_typhoon_map

st.title("🌪 Tropical Cyclone Track Generator")
# ✅ initialize past track storage

# ======================================
# ✅ PAST TRACK (DYNAMIC ROWS)
# ======================================

st.subheader("🕘 Past Track Input")

# initialize
if "past_rows" not in st.session_state:
    st.session_state.past_rows = [
        {"lat": 10.0, "lon": 145.0, "intensity": "TD"}
    ]

# buttons
colA, colB, colC = st.columns(3)

with colA:
    if st.button("➕ Add Row"):
        st.session_state.past_rows.append(
            {"lat": 10.0, "lon": 145.0, "intensity": "TD"}
        )

with colB:
    if st.button("➖ Remove Last"):
        if len(st.session_state.past_rows) > 0:
            st.session_state.past_rows.pop()
import json

import json

with colC:

    # ✅ SAVE BUTTON
    if st.button("💾 Save Inputs"):

        data = {
            "forecast": {
                "lats": lats,
                "lons": lons,
                "hours": hours,
                "intensities": intensities
            },
            "past": {
                "lats": past_lats,
                "lons": past_lons,
                "intensities": past_intensities
            },
            "wind_radii": {
                "strong": [strong_NE, strong_SE, strong_SW, strong_NW],
                "storm": [storm_NE, storm_SE, storm_SW, storm_NW]
            }
        }

        json_data = json.dumps(data, indent=4)

        st.download_button(
            "📥 Download JSON",
            json_data,
            file_name="typhoon_input.json",
            mime="application/json"
        )


    # ✅ LOAD BUTTON
    uploaded_file = st.file_uploader("📂 Load File", type=["json"])

    if uploaded_file is not None:
        data = json.load(uploaded_file)
        st.success("✅ File loaded!")
        st.write(data)

# data containers
past_lats = []
past_lons = []
past_intensities = []

intensity_options = ["LPA", "TD", "TS", "STS", "TY", "STY", "SuTY", "EX"]

# ✅ Dynamic loop (NO num_past anymore)
for i, row in enumerate(st.session_state.past_rows):

    st.write(f"Past Point {i+1}")

    col1, col2, col3 = st.columns(3)

    lat = col1.number_input(
        f"Past Lat {i+1}",
        value=row["lat"],
        step=0.1,
        format="%.1f",
        key=f"plat{i}"
    )

    lon = col2.number_input(
        f"Past Lon {i+1}",
        value=row["lon"],
        step=0.1,
        format="%.1f",
        key=f"plon{i}"
    )

    intensity = col3.selectbox(
        f"Intensity {i+1}",
        intensity_options,
        index=intensity_options.index(row["intensity"]),
        key=f"pintensity{i}"
    )

    # update stored values
    st.session_state.past_rows[i] = {
        "lat": lat,
        "lon": lon,
        "intensity": intensity
    }

    past_lats.append(lat)
    past_lons.append(lon)
    past_intensities.append(intensity)
    
st.subheader("📍 Forecast Track Input")

# =============================
# TRACK INPUT (INDIVIDUAL BOXES)
# =============================
MACAU_LAT = 22.1595
MACAU_LON = 113.5685
# ✅ Fixed official forecast hours (no 36H)
fixed_hours = [0, 12, 24, 48, 72, 96, 120]

num_points = st.slider("Number of forecast points", 2, 7, 5)

lats = []
lons = []
hours = []
intensities = []

# ✅ Intensity options
intensity_options = ["12H", "TD", "TS", "STS", "TY", "STY", "SuTY","EX", "LPA", ]

st.subheader("📍 Forecast Track Input")

for i in range(num_points):
    hr = fixed_hours[i]

    st.write(f"### {hr}H")

    col1, col2, col4 = st.columns(3)
 

    lat = col1.number_input(
        f"Lat ({hr}H)",
        format="%.1f",   # ✅ 1 decimal place
        step=0.1,        # ✅ increment by 0.1
        key=f"lat{i}"
    )

    lon = col2.number_input(
        f"Lon ({hr}H)",
        format="%.1f",
        step=0.1,
        key=f"lon{i}"
    )

    intensity = col4.selectbox(
        f"Intensity ({hr}H)",
        intensity_options,
        index=3,
        key=f"intensity{i}"
    )

    lats.append(lat)
    lons.append(lon)
    hours.append(hr)
    intensities.append(intensity)

# =============================
# WIND RADII INPUT (8 BOXES)
# =============================
st.subheader("💨 Wind Radii (km)")

st.markdown("### Strong Wind")

col1, col2, col3, col4 = st.columns(4)
strong_NE = col1.number_input("NE", value=0, step=10)
strong_SE = col2.number_input("SE", value=0, step=10)
strong_SW = col3.number_input("SW", value=0, step=10)
strong_NW = col4.number_input("NW", value=0, step=10)

st.markdown("### Storm Wind")

col1, col2, col3, col4 = st.columns(4)
storm_NE = col1.number_input("NE (storm)", value=0, step=10)
storm_SE = col2.number_input("SE (storm)", value=0, step=10)
storm_SW = col3.number_input("SW (storm)", value=0, step=10)
storm_NW = col4.number_input("NW (storm)", value=0, step=10)

import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius (km)

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


def bearing(lat1, lon1, lat2, lon2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)

    x = math.sin(dlambda) * math.cos(phi2)
    y = math.cos(phi1)*math.sin(phi2) - math.sin(phi1)*math.cos(phi2)*math.cos(dlambda)

    angle = math.degrees(math.atan2(x, y))
    return (angle + 360) % 360


def bearing_to_compass(angle):
    directions = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
                  "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    index = int((angle + 11.25) // 22.5) % 16
    return directions[index]
# =============================
# GENERATE BUTTON
# =============================

colA, colB = st.columns(2)

# =============================
# GENERATE MAP
# =============================
with colA:
    if st.button("🚀 Generate Map"):

        wind_radii = {
            "strong": [(0, 90, strong_NE), (90, 180, strong_SE),
                       (180, 270, strong_SW), (270, 360, strong_NW)],
            "storm": [(0, 90, storm_NE), (90, 180, storm_SE),
                      (180, 270, storm_SW), (270, 360, storm_NW)]
        }

        fig = create_typhoon_map(
            user_lats=lats,
            user_lons=lons,
            user_hours=hours,
            wind_radii_input=wind_radii,
            intensities=intensities,
            past_lats=past_lats,   
            past_lons=past_lons,
            past_intensities=past_intensities
        )

        fig.set_dpi(50)
        st.pyplot(fig)


# =============================
# ✅ MERGED: DISTANCE + MOTION
# =============================
with colB:
    if st.button("📏 Distance & Motion"):

        if len(lats) < 2:
            st.error("Need at least 0H and 12H points")
        else:
            MACAU_LAT = 22.1595
            MACAU_LON = 113.5685

            # =============================
            # Distance from Macau
            # =============================
            lat0, lon0 = lats[0], lons[0]

            dist_macau = haversine(MACAU_LAT, MACAU_LON, lat0, lon0)
            ang_macau = bearing(MACAU_LAT, MACAU_LON, lat0, lon0)
            dir_macau = bearing_to_compass(ang_macau)

            # =============================
            # Motion (0H → 12H)
            # =============================
            lat1, lon1 = lats[1], lons[1]

            dist_move = haversine(lat0, lon0, lat1, lon1)
            ang_move = bearing(lat0, lon0, lat1, lon1)
            dir_move = bearing_to_compass(ang_move)

            time_diff = hours[1] - hours[0]
            speed = dist_move / time_diff

            # =============================
            # DISPLAY
            # =============================
            st.success(f"📍 Macau: {dir_macau} {dist_macau:.0f} km")
            st.success(f"🌀 Motion: {dir_move} at {speed:.1f} km/h")
