import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon, LineString
import random

# Load and process GeoJSON file
def load_polygon_from_geojson(filepath):
    gdf = gpd.read_file(filepath)
    geometry = gdf.geometry.unary_union

    # Convert LineString to Polygon if needed
    if geometry.geom_type == 'LineString':
        print("🔄 Converting LineString to Polygon...")
        geometry = Polygon(geometry.coords)

    if not geometry.is_valid:
        print("⚠️ Invalid geometry, attempting to fix...")
        geometry = geometry.buffer(0)

    return geometry

# Generate grid points inside the polygon (excluding border)
def generate_points(polygon, spacing=0.001, border_buffer=0.0001):
    minx, miny, maxx, maxy = polygon.bounds
    points = []
    x = minx
    while x <= maxx:
        y = miny
        while y <= maxy:
            point = Point(x, y)
            if polygon.contains(point) and polygon.buffer(-border_buffer).contains(point):
                points.append(point)
            y += spacing
        x += spacing
    print(f"✅ Generated {len(points)} valid points.")
    return points

# Assign random soil data
def assign_soil_data(points):
    data = []
    for pt in points:
        lat = pt.y
        lon = pt.x
        N = random.randint(0, 100)
        P = random.randint(0, 100)
        K = random.randint(0, 100)
        EC = round(random.uniform(0.1, 2.5), 2)
        Temperature = round(random.uniform(15, 40), 2)
        Humidity = round(random.uniform(10, 50), 2)
        data.append([lat, lon, N, P, K, EC, Temperature, Humidity])
    return data

# Save CSV
def save_to_csv(data, filename='soil_data_inside_polygon.csv'):
    if not data:
        print("⚠️ No data to save! Try reducing border_buffer or increasing spacing.")
        return
    df = pd.DataFrame(data, columns=['Latitude', 'Longitude', 'N', 'P', 'K', 'EC', 'Temperature', 'Humidity'])
    df.to_csv(filename, index=False)
    print(f"✅ CSV saved as {filename}")

# ----------------------------
# Replace this path with your file
geojson_path = "C:/Users/kevin/Desktop/Bhoomi/MainBhoomi/Code/ANN/test/test/mapTest.geojson"

polygon = load_polygon_from_geojson(geojson_path)
points = generate_points(polygon, spacing=0.0005, border_buffer=0.0005)
soil_data = assign_soil_data(points)
save_to_csv(soil_data)


