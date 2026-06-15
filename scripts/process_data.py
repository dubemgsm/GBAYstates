import pandas as pd
import geopandas as gpd
from shapely.ops import unary_union
import os

def process_data():
    print("Starting data processing...")
    
    # Define file paths
    schools_path = 'data/raw/north_east_schools_complete.csv'
    conflict_path = 'data/raw/conflict_data_nga.csv'
    output_path = 'data/processed/bay_schools.geojson'

    # 1. Load data
    print("Loading raw datasets...")
    schools_df = pd.read_csv(schools_path)
    conflict_df = pd.read_csv(conflict_path)

    # 2. Filter for BAY states
    # Mapping state codes to full names as seen in previous research
    state_map = {'AD': 'Adamawa', 'BR': 'Borno', 'YO': 'Yobe'}
    schools_df['state_full'] = schools_df['state'].map(state_map)
    
    # Filter schools
    schools_df = schools_df[schools_df['state_full'].isin(['Borno', 'Adamawa', 'Yobe'])].copy()
    
    # Filter conflict events (adm_1 contains the state name)
    bay_states = ['Borno', 'Adamawa', 'Yobe']
    conflict_df = conflict_df[conflict_df['adm_1'].str.contains('|'.join(bay_states), case=False, na=False)].copy()

    # 3. Clean coordinates
    print("Cleaning coordinates...")
    schools_df = schools_df.dropna(subset=['latitude', 'longitude'])
    conflict_df = conflict_df.dropna(subset=['latitude', 'longitude'])

    # 4. Convert to GeoDataFrames (EPSG:32632 for meter-based distance)
    print("Converting to GeoDataFrames (EPSG:32632)...")
    schools_gdf = gpd.GeoDataFrame(
        schools_df, 
        geometry=gpd.points_from_xy(schools_df.longitude, schools_df.latitude),
        crs="EPSG:4326"
    ).to_crs("EPSG:32632")

    conflict_gdf = gpd.GeoDataFrame(
        conflict_df,
        geometry=gpd.points_from_xy(conflict_df.longitude, conflict_df.latitude),
        crs="EPSG:4326"
    ).to_crs("EPSG:32632")

    # 5. Spatial Analysis: 5km Buffer
    print("Drawing 5km buffers around conflict events...")
    # Buffer conflict points by 5000 meters
    conflict_buffers = conflict_gdf.buffer(5000)
    # Dissolve buffers into a single geometry for faster intersection testing
    conflict_union = unary_union(conflict_buffers)

    print("Calculating vulnerability scores...")
    # Check if schools are within the conflict union
    schools_gdf['vulnerability_score'] = schools_gdf.geometry.within(conflict_union)
    schools_gdf['vulnerability_score'] = schools_gdf['vulnerability_score'].map({True: 'High', False: 'Low'})

    # 6. Save final data (EPSG:4326)
    print(f"Saving results to {output_path}...")
    # Map back to state name for consistency
    schools_gdf = schools_gdf.drop(columns=['state'])
    schools_gdf = schools_gdf.rename(columns={'state_full': 'state'})
    
    # Export to GeoJSON
    schools_gdf.to_crs("EPSG:4326").to_file(output_path, driver='GeoJSON')
    print("Processing complete!")

if __name__ == "__main__":
    process_data()
