import streamlit as st
import numpy as np
from typhoon_map import create_typhoon_map
import json
import math

st.title("🌪 Tropical Cyclone Track Generator")

# ======================================
# ✅ PAST TRACK (DYNAMIC ROWS)
# ======================================
st.subheader("🕘 Past Track Input")

if "past_rows" not in st.session_state:
    st.session_state.past_rows = [
        {"lat": 10.0, "lon": 145.0, "intensity": "TD"}
    ]

colA, colB = st.columns(2)

with colA:
    if st.button("➕ Add Row"):
        st.session_state.past_rows.append(
            {"lat": 10.0, "lon": 145.0, "intensity": "TD"}
        )

with colB:
    if st.button("➖ Remove Last"):
        if len(st.session_state.past_rows) > 0:
            st.session_state.past_rows.pop()

past_lats = []
past_lons = []
past_intensities = []

intensity_options = ["LPA", "TD", "TS", "STS", "TY", "STY", "SuTY", "EX"]

for i, row in enumerate(st.session_state.past_rows):

    st.write(f"Past Point {i+1}")

    col1, col2, col3 = st.columns(3)

    lat = col1.number_input(
    f"Lat ({hr}H)",
    value=10.0,        # ✅ FIX
    step=0.1,
    format="%.1f",
    key=f"lat{i}"
    )

    lon = col2.number_input(
    f"Lon ({hr}H)",
    value=140.0,       # ✅ FIX
    step=0.1,
    format="%.1f",
    key=f"lon{i}"
    )
    
    intensity = col3.selectbox(f"Intensity {i+1}",
                               intensity_options,
                               index=intensity_options.index(row["intensity"]),
                               key=f"pintensity{i}")

    st.session_state.past_rows[i] = {"lat": lat, "lon": lon, "intensity": intensity}

    past_lats.append(lat)
    past_lons.append(lon)
    past_intensities.append(intensity)

# ======================================
# ✅ FORECAST TRACK
# ======================================
st.subheader("📍 Forecast Track Input")

fixed_hours = [0, 12, 24, 48, 72, 96, 120]
num_points = st.slider("Number of forecast points", 2, 7, 5)

lats, lons, hours, intensities = [], [], [], []

intensity_options = ["12H", "TD", "TS", "STS", "TY", "STY", "SuTY", "EX", "LPA"]

for i in range(num_points):
    hr = fixed_hours[i]

    st.write(f"### {hr}H")
    col1, col2, col3 = st.columns(3)

    lat = col1.number_input(f"Lat ({hr}H)", step=0.1, format="%.1f", key=f"lat{i}")
    lon = col2.number_input(f"Lon ({hr}H)", step=0.1, format="%.1f", key=f"lon{i}")

    intensity = col3.selectbox(f"Intensity ({hr}H)",
                                intensity_options,
                                index=2,
                                key=f"intensity{i}")

    lats.append(lat)
    lons.append(lon)
    hours.append(hr)
    intensities.append(intensity)

# ======================================
# ✅ WIND RADII
# ======================================
st.subheader("💨 Wind Radii (km)")

col1, col2, col3, col4 = st.columns(4)
strong_NE = col1.number_input("NE", value=0, step=10)
strong_SE = col2.number_input("SE", value=0, step=10)
strong_SW = col3.number_input("SW", value=0, step=10)
strong_NW = col4.number_input("NW", value=0, step=10)

col1, col2, col3, col4 = st.columns(4)
storm_NE = col1.number_input("Storm NE", value=0, step=10)
storm_SE = col2.number_input("Storm SE", value=0, step=10)
storm_SW = col3.number_input("Storm SW", value=0, step=10)
storm_NW = col4.number_input("Storm NW", value=0, step=10)

# ======================================
# ✅ HELPER FUNCTIONS
# ======================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def bearing(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)

    x = math.sin(dlambda) * math.cos(phi2)
    y = math.cos(phi1)*math.sin(phi2) - math.sin(phi1)*math.cos(phi2)*math.cos(dlambda)

    return (math.degrees(math.atan2(x, y)) + 360) % 360

def bearing_to_compass(angle):
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
            "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return dirs[int((angle+11.25)//22.5)%16]

# ======================================
# ✅ BUTTONS (SAFE POSITION)
# ======================================
colA, colB, colC = st.columns(3)

# 🚀 MAP
with colA:
    if st.button("🚀 Generate Map"):
        wind_radii = {
            "strong": [(0,90,strong_NE),(90,180,strong_SE),(180,270,strong_SW),(270,360,strong_NW)],
            "storm": [(0,90,storm_NE),(90,180,storm_SE),(180,270,storm_SW),(270,360,storm_NW)]
        }

        fig = create_typhoon_map(
            lats, lons, hours,
            intensities, wind_radii,
            past_lats, past_lons,
            past_intensities
        )
        st.pyplot(fig)

# 📏 DISTANCE
with colB:
    if st.button("📏 Distance & Motion"):
        if len(lats) >= 2 and lats[0] != 0 and lons[0] != 0:
            d = haversine(lats[0], lons[0], lats[1], lons[1])
            dir = bearing_to_compass(bearing(lats[0], lons[0], lats[1], lons[1]))
            speed = d / (hours[1]-hours[0])

            st.success(f"{dir} {d:.0f} km")
            st.success(f"{dir} at {speed:.1f} km/h")

# 💾 SAVE (NOW FIXED ✅)
with colC:
    if st.button("💾 Save Inputs"):
        data = {
            "forecast": {"lats": lats, "lons": lons, "hours": hours, "intensities": intensities},
            "past": {"lats": past_lats, "lons": past_lons, "intensities": past_intensities}
        }
        st.download_button("📥 Download JSON",
                           json.dumps(data, indent=4),
                           file_name="typhoon.json")

    # ✅ LOAD FILE
    uploaded_file = st.file_uploader("📂 Load File", type=["json"])

    if uploaded_file is not None:
        data = json.load(uploaded_file)

        st.success("✅ File loaded!")

        st.write(data)
