import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from shutil import get_terminal_size
from final_project.config import (CRS, DATA_DIR, FEATURES_DIR, 
                                  META_DIR, RAW_DIR, ROOT_DIR)
from final_project.data import poi, stm
from final_project.utils import create_grid, create_map_plot, save_figure


def main():
    _step_num = 0
    def print_step(heading):
        nonlocal _step_num
        width = get_terminal_size()[0]
        print('=' * width)
        print('=', f"{_step_num}. {heading.upper()}")
        print('=' * width)
        _step_num += 1


    # 0. Set up the hex grid.
    print_step("Hex grid setup")
    grid_file = DATA_DIR / 'grid.geojson'
    if not grid_file.is_file():
        print(("Creating the hex grid from island and "
               "administrative boundary shapefiles."))
        island_shp = RAW_DIR / 'island/limites-terrestres.shp'
        agglo_shp = RAW_DIR / 'city/limites-administratives-agglomeration.shp'
        grid = create_grid(island_shp, agglo_shp)
        grid.to_file(grid_file, driver='GeoJSON')
    else:
        print("Hex grid already exists. Loading the most recent version from",
              grid_file.relative_to(ROOT_DIR))
        grid = gpd.read_file(grid_file)
        grid = grid.set_index('cell_id')
    
    fig, ax = create_map_plot('Grid representation of Montreal')
    grid.plot(ax=ax, facecolor='skyblue', edgecolor='dimgrey', alpha=0.67)
    grid.dissolve(by='subdivision').boundary.plot(ax=ax, color='black')
    plt.tight_layout()
    plt.show()

    save_figure(fig, 'montreal_hex_grid')

    # 1. Collect Points of Interest.
    print_step("Points of Interest")
    pois_file = FEATURES_DIR / 'pois.geojson'
    if not pois_file.is_file():
        # DOM POIs.
        places_file = RAW_DIR / 'lieux_d_interet.csv'
        establishments_file = RAW_DIR / 'etablissements_alimentaires.csv'
        translation_metadata = META_DIR / 'translations.json'
        mapping_metadata = META_DIR / 'group_mappings.json'
        print(("Extracting DOM POIs from lieux d’intérêt "
               "and établissements alimentaires data."))
        dom_pois = poi.load_dom_pois(
            places_file,
            establishments_file,
            translation_metadata)
        # OSM POIs.
        print("Querying OSM for suburb POIs. This can take a minute...")
        osm_pois = poi.load_osm_pois()
        # Combine the two sets.
        print("Combining DOM and OSM POIs.")
        all_pois = poi.combine_pois(dom_pois, osm_pois, mapping_metadata)
        all_pois = all_pois.to_crs(CRS)
        all_pois.to_file(pois_file, driver='GeoJSON')
    else:
        print("POI data already exists. Loading the most recent version from",
              pois_file.relative_to(ROOT_DIR))
        all_pois = gpd.read_file(pois_file)

    # 2. Get bus stops and metro stations.
    print_step("STM stops and stations")
    stops_file = FEATURES_DIR / 'stops.geojson'
    if not stops_file.is_file():
        print("Getting STM bus stops and metro stations from the shapefile.")
        island_shp = RAW_DIR / 'island' / 'limites-terrestres.shp'
        stm_shp = RAW_DIR / 'stm' / 'stm_arrets_sig.shp'
        stops = stm.load_transit_stops(stm_shp, island_shp)
        stops.to_file(stops_file, driver='GeoJSON')
    else:
        print("STM data already exists. Loading the most recent version from",
              stops_file.relative_to(ROOT_DIR))
        stops = gpd.read_file(stops_file)


if __name__ == "__main__":
    sns.set_theme(style='white', palette='Set1')
    main()
