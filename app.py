import streamlit as st
import numpy as np
from typhoon_map import create_typhoon_map

st.title("🌪 Tropical Cyclone Track Generator")

st.subheader("📍 Forecast Track Input")

# =============================
# TRACK INPUT (INDIVIDUAL BOXES)
# =============================

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
        value=10.0,
        format="%.1f",   # ✅ 1 decimal place
        step=0.1,        # ✅ increment by 0.1
        key=f"lat{i}"
    )

    lon = col2.number_input(
        f"Lon ({hr}H)",
        value=140.0,
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

# =============================
# GENERATE BUTTON
# =============================
if st.button("🚀 Generate Map"):

    try:
        wind_radii = {
            "strong": [
                (0, 90, strong_NE),
                (90, 180, strong_SE),
                (180, 270, strong_SW),
                (270, 360, strong_NW),
            ],
            "storm": [
                (0, 90, storm_NE),
                (90, 180, storm_SE),
                (180, 270, storm_SW),
                (270, 360, storm_NW),
            ]
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
            "📥 Download Map (PNG)",
            data=buf,
            file_name="typhoon_map.png",
            mime="image/png"
        )

    except Exception as e:
        st.error(f"Error generating map: {e}")
