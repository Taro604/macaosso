import os
import numpy as np
from scipy.interpolate import PchipInterpolator
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from shapely.geometry import Point
from shapely.ops import unary_union
from datetime import datetime
import pytz

try:
    from shapely.validation import make_valid
except:
    make_valid = lambda g: g

MACAU_LAT = 22.1595
MACAU_LON = 113.5685
KM_PER_DEG = 111.32


# ==========================================
# ICON MAPPING
# ==========================================
def get_icon_path(intensity):
    mapping = {
        "EX": "Ex.png",
        "LPA": "LPA.png",
        "TD": "TD.png",
        "TS": "TS.png",
        "STS": "STS.png",
        "TY": "TY.png",
        "STY": "STY.png",
        "SuTY": "SuTY.png",
        "12H": "12H Large.png"
    }
    return mapping.get(intensity, "TS.png")


# ==========================================
# SMOOTH TRACK
# ==========================================
def create_smooth_track(hours, lons, lats):
    interp_hours = np.linspace(hours.min(), hours.max(), 100)
    smooth_lons = PchipInterpolator(hours, lons)(interp_hours)
    smooth_lats = PchipInterpolator(hours, lats)(interp_hours)
    return smooth_lons, smooth_lats, interp_hours


# ==========================================
# WIND RADII
# ==========================================
def plot_wind_radii(ax, center_lon, center_lat, quadrants, color, alpha=0.05, lw=0.5):
    pts = []
    for start, end, r_km in quadrants:
        r_deg = r_km / KM_PER_DEG
        theta = np.linspace(start, end, 60)

        x = center_lon + r_deg * np.cos(np.deg2rad(theta))
        y = center_lat + r_deg * np.sin(np.deg2rad(theta))

        pts.extend(list(zip(x, y)))

    if pts:
        pts.append(pts[0])
        lons, lats = zip(*pts)
        ax.plot(lons, lats, color=color, linewidth=lw)
        ax.fill(lons, lats, color=color, alpha=alpha)


# ==========================================
# MAIN FUNCTION
# ==========================================
def create_typhoon_map(user_lats, user_lons, user_hours, intensities, wind_radii_input):

    hours = np.array(user_hours)
    lats = np.array(user_lats)
    lons = np.array(user_lons)

    # ======================================
    # SMOOTH TRACK
    # ======================================
    smooth_lons, smooth_lats, interp_hours = create_smooth_track(hours, lons, lats)

    # ======================================
    # JTWC-STYLE ENVELOPE
    # ======================================
# Base JTWC radii
    base_hours = np.array([0, 12, 24, 48, 72, 96, 120])
    base_radii = np.array([15, 60, 100, 170, 255, 345, 465])

# Interpolate radii to match user hours ✅
    radii_km = np.interp(hours, base_hours, base_radii)
    radii_deg = radii_km / KM_PER_DEG   

    smooth_radii = PchipInterpolator(hours, radii_deg)(interp_hours)

    # split ≤72h and >72h
    circles1 = [
        Point(smooth_lons[i], smooth_lats[i]).buffer(smooth_radii[i])
        for i in range(len(smooth_lons))
        if interp_hours[i] <= 72
    ]

    circles2 = [
        Point(smooth_lons[i], smooth_lats[i]).buffer(smooth_radii[i])
        for i in range(len(smooth_lons))
        if interp_hours[i] > 72
    ]

    envelope1 = unary_union(circles1) if circles1 else None
    envelope2 = unary_union(circles2) if circles2 else None

    # fix overlap
    if envelope2:
        idx = np.argmin(np.abs(interp_hours - 72))
        cut_circle = Point(
            smooth_lons[idx],
            smooth_lats[idx]
        ).buffer(smooth_radii[idx])

        envelope2 = make_valid(envelope2.difference(cut_circle))

    if envelope1 and envelope2:
        envelope2 = make_valid(envelope2.difference(envelope1))

    # ======================================
    # FIGURE
    # ======================================
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1,1,1, projection=ccrs.PlateCarree())
    ax.set_extent([110,150,0,35])

    # ======================================
    # MAP STYLE
    # ======================================
    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.25)
    ax.add_feature(cfeature.LAND, edgecolor="#959a9f", facecolor="#2d363f")
    ax.add_feature(cfeature.OCEAN, facecolor="#222a35")

    # ======================================
    # ENVELOPES
    # ======================================
    if envelope1:
        ax.add_geometries([envelope1], crs=ccrs.PlateCarree(),
                          facecolor='white', alpha=0.20)

    if envelope2:
        ax.add_geometries([envelope2], crs=ccrs.PlateCarree(),
                          facecolor='white', alpha=0.10)

    # ======================================
    # TRACK
    # ======================================
    ax.plot(smooth_lons, smooth_lats, color='white', linestyle='--')

    # ======================================
    # ICONS
    # ======================================
    for i, (lon, lat) in enumerate(zip(lons, lats)):
        try:
            icon_file = get_icon_path(intensities[i])
            img_path = os.path.join("TC logo", icon_file)

            img = mpimg.imread(img_path)

            imagebox = OffsetImage(img, zoom=0.004)
            ab = AnnotationBbox(
                imagebox, (lon, lat),
                frameon=False,
                transform=ccrs.PlateCarree()
            )
            ax.add_artist(ab)

        except Exception as e:
            print("Icon error:", e)
            ax.plot(lon, lat, 'wo')

    # ======================================
    # WIND RADII
    # ======================================
    center_lon = lons[0]
    center_lat = lats[0]

    plot_wind_radii(ax, center_lon, center_lat,
                    wind_radii_input["strong"], 'yellow')

    plot_wind_radii(ax, center_lon, center_lat,
                    wind_radii_input["storm"], 'red')

    # ======================================
    # MACAU REFERENCE
    # ======================================
    ax.plot(MACAU_LON, MACAU_LAT, 'o', color='white', markersize=5)

    for km in [100, 205, 410, 850]:
        r = km / KM_PER_DEG
        ax.add_patch(
            plt.Circle((MACAU_LON, MACAU_LAT), r,
                       fill=False, linestyle='--',
                       color='#949494', alpha=0.5,
                       linewidth=0.5,
                       transform=ccrs.PlateCarree())
        )

    # ======================================
    # GRID
    # ======================================
    gl = ax.gridlines(draw_labels=True, linestyle='--', color='gray')
    gl.top_labels = False
    gl.right_labels = False

    # ======================================
    # TITLE
    # ======================================
    now = datetime.now(pytz.timezone("Asia/Macau"))
    ax.set_title(f"Typhoon Track\n{now.strftime('%Y-%m-%d %H:%M')}")

    return fig