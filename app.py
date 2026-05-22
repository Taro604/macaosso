import streamlit as st
import numpy as np
from typhoon_map import create_typhoon_map
import json
import math

st.title("🌪 Tropical Cyclone Track Generator")

# ======================================
# ✅ PAST TRACK
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

past_lats, past_lons, past_intensities = [], [], []
intensity_options = ["LPA","TD","TS","STS","TY","STY","SuTY","EX"]

for i, row in enumerate(st.session_state.past_rows):

    st.write(f"Past Point {i+1}")
    c1, c2, c3 = st.columns(3)

    lat = c1.number_input(
        f"Past Lat {i+1}",
        value=row["lat"],
        step=0.1,
        format="%.1f",
        key=f"plat{i}"
    )

    lon = c2.number_input(
        f"Past Lon {i+1}",
        value=row["lon"],
        step=0.1,
        format="%.1f",
        key=f"plon{i}"
    )

    intensity = c3.selectbox(
        f"Intensity {i+1}",
        intensity_options,
        index=intensity_options.index(row["intensity"]),
        key=f"pintensity{i}"
    )

    st.session_state.past_rows[i] = {
        "lat": lat,
        "lon": lon,
        "intensity": intensity
    }

    past_lats.append(lat)
    past_lons.append(lon)
    past_intensities.append(intensity)

# ======================================
# ✅ FORECAST TRACK
# ======================================
st.subheader("📍 Forecast Track Input")

fixed_hours = [0,12,24,48,72,96,120]
num_points = st.slider("Number of forecast points", 2, 7, 5)

lats, lons, hours, intensities = [], [], [], []
intensity_options = ["12H","TD","TS","STS","TY","STY","SuTY","EX","LPA"]

for i in range(num_points):
    hr = fixed_hours[i]

    st.write(f"### {hr}H")
    c1, c2, c3 = st.columns(3)

    lat = c1.number_input(
        f"Lat ({hr}H)",
        value=10.0,
        step=0.1,
        format="%.1f",
        key=f"flat{i}"
    )

    lon = c2.number_input(
        f"Lon ({hr}H)",
        value=140.0,
        step=0.1,
        format="%.1f",
        key=f"flon{i}"
    )

    intensity = c3.selectbox(
        f"Intensity ({hr}H)",
        intensity_options,
        index=2,
        key=f"fintensity{i}"
    )

    lats.append(lat)
    lons.append(lon)
    hours.append(hr)
    intensities.append(intensity)

# ======================================
# ✅ WIND RADII (with keys ✅)
# ======================================
st.subheader("💨 Wind Radii (km)")

c1,c2,c3,c4 = st.columns(4)
strong_NE = c1.number_input("NE", 0, key="strong_NE")
strong_SE = c2.number_input("SE", 0, key="strong_SE")
strong_SW = c3.number_input("SW", 0, key="strong_SW")
strong_NW = c4.number_input("NW", 0, key="strong_NW")

c1,c2,c3,c4 = st.columns(4)
storm_NE = c1.number_input("Storm NE", 0, key="storm_NE")
storm_SE = c2.number_input("Storm SE", 0, key="storm_SE")
storm_SW = c3.number_input("Storm SW", 0, key="storm_SW")
storm_NW = c4.number_input("Storm NW", 0, key="storm_NW")

# ======================================
# ✅ HELPER FUNCTIONS
# ======================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2-lat1)
    dlambda = math.radians(lon2-lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1-a))

def bearing(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlambda = math.radians(lon2-lon1)
    x = math.sin(dlambda)*math.cos(phi2)
    y = math.cos(phi1)*math.sin(phi2)-math.sin(phi1)*math.cos(phi2)*math.cos(dlambda)
    return (math.degrees(math.atan2(x,y))+360)%360

def bearing_to_compass(a):
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
            "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return dirs[int((a+11.25)//22.5)%16]

# ======================================
# ✅ BUTTONS
# ======================================
colA,colB,colC = st.columns(3)

# 🚀 MAP
with colA:
    if st.button("🚀 Generate Map"):
        wind = {
            "strong":[(0,90,strong_NE),(90,180,strong_SE),(180,270,strong_SW),(270,360,strong_NW)],
            "storm":[(0,90,storm_NE),(90,180,storm_SE),(180,270,storm_SW),(270,360,storm_NW)]
        }

        fig = create_typhoon_map(
            lats,lons,hours,
            intensities,wind,
            past_lats,past_lons,past_intensities
        )
        st.pyplot(fig)

# 📏 DISTANCE
with colB:
    if st.button("📏 Distance & Motion"):

        if len(lats) >= 2:
            MACAU_LAT, MACAU_LON = 22.1595, 113.5685

            d_macau = haversine(MACAU_LAT,MACAU_LON,lats[0],lons[0])
            dir_macau = bearing_to_compass(
                bearing(MACAU_LAT,MACAU_LON,lats[0],lons[0])
            )

            d_move = haversine(lats[0],lons[0],lats[1],lons[1])
            dir_move = bearing_to_compass(
                bearing(lats[0],lons[0],lats[1],lons[1])
            )

            speed = d_move/(hours[1]-hours[0])

            st.success(f"📍 Macau: {dir_macau} {d_macau:.0f} km")
            st.success(f"🌀 Motion: {dir_move} at {speed:.1f} km/h")

# 💾 SAVE + LOAD ✅ FULL
with colC:

    if st.button("💾 Save Inputs"):
        data = {
            "forecast":{
                "lats":lats,
                "lons":lons,
                "hours":hours,
                "intensities":intensities
            },
            "past":{
                "lats":past_lats,
                "lons":past_lons,
                "intensities":past_intensities
            },
            "wind_radii":{
                "strong":[strong_NE,strong_SE,strong_SW,strong_NW],
                "storm":[storm_NE,storm_SE,storm_SW,storm_NW]
            }
        }

        st.download_button(
            "📥 Download JSON",
            json.dumps(data, indent=4),
            file_name="typhoon.json"
        )

    file = st.file_uploader("📂 Load File", ["json"])

    if file:
        data = json.load(file)

        # forecast
        if "forecast" in data:
            for i in range(len(data["forecast"]["lats"])):
                st.session_state[f"flat{i}"] = data["forecast"]["lats"][i]
                st.session_state[f"flon{i}"] = data["forecast"]["lons"][i]
                st.session_state[f"fintensity{i}"] = data["forecast"]["intensities"][i]

        # past
        if "past" in data:
            st.session_state.past_rows = []
            for i in range(len(data["past"]["lats"])):
                st.session_state.past_rows.append({
                    "lat": data["past"]["lats"][i],
                    "lon": data["past"]["lons"][i],
                    "intensity": data["past"]["intensities"][i]
                })

        # wind radii
        if "wind_radii" in data:
            strong = data["wind_radii"]["strong"]
            storm = data["wind_radii"]["storm"]

            st.session_state["strong_NE"] = strong[0]
            st.session_state["strong_SE"] = strong[1]
            st.session_state["strong_SW"] = strong[2]
            st.session_state["strong_NW"] = strong[3]

            st.session_state["storm_NE"] = storm[0]
            st.session_state["storm_SE"] = storm[1]
            st.session_state["storm_SW"] = storm[2]
            st.session_state["storm_NW"] = storm[3]

        st.success("✅ All inputs restored!")
        st.rerun()
