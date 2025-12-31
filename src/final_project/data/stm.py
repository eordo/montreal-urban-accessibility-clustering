import geopandas as gpd
from final_project.config import CRS


def load_transit_stops(stops_shp, island_shp):
    island = gpd.read_file(island_shp)
    island = island.to_crs(CRS)
    stops = gpd.read_file(stops_shp).to_crs(CRS)
    stops = stops[stops['geometry'].within(island.unary_union)]
    stops = stops.drop_duplicates(subset=['stop_code'])
    stops = stops[['stop_code', 'stop_id', 'stop_name', 'geometry']]
    return stops.reset_index(drop=True)
