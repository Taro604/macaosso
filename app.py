import streamlit as st
import numpy as np
from typhoon_map import create_typhoon_map

st.title("🌪 Tropical Cyclone Track Generator")

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

colA, colB, colC = st.columns(3)

# =============================
# GENERATE MAP BUTTON
# =============================
with colA:
    if st.button("Generate Map"):

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
            intensities=intensities
        )

        fig.set_dpi(150)
        st.pyplot(fig)

        import io
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=800, bbox_inches='tight')
        buf.seek(0)

        st.download_button(
            "Download Map (PNG)",
            data=buf,
            file_name="typhoon_map.png",
            mime="image/png"
        )
        
# =============================
# DISTANCE BUTTON ✅ NEW
# =============================
with colB:
    if st.button("Distance"):

        lat0 = lats[0]
        lon0 = lons[0]

        dist = haversine(MACAU_LAT, MACAU_LON, lat0, lon0)
        ang = bearing(MACAU_LAT, MACAU_LON, lat0, lon0)
        direction = bearing_to_compass(ang)

        st.success(
            f"Distance from Macau: {direction} {dist:.0f} km"
        )

    if len(lats) < 2:
            st.error("Need at least 0H and 12H points")
        else:
            lat0, lon0 = lats[0], lons[0]
            lat1, lon1 = lats[1], lons[1]

            dist = haversine(lat0, lon0, lat1, lon1)
            ang = bearing(lat0, lon0, lat1, lon1)

            direction = bearing_to_compass(ang)

            # hours difference (normally 12h)
            time_diff = hours[1] - hours[0]

            speed = dist / time_diff  # km/h

            st.success(
                f"Movement: {direction} at {speed:.1f} km/h"
            )

