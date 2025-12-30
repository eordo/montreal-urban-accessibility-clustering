import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from shutil import get_terminal_size
from final_project.config import DATA_DIR, RAW_DIR, ROOT_DIR
from final_project.utils import create_grid, create_map_plot, save_figure


def main():
    sns.set_theme(style='white', palette='Set1')

    _step_num = 0
    def print_step(heading):
        nonlocal _step_num
        _step_num += 1
        width = get_terminal_size()[0]
        print('=' * width)
        print('=', f"{_step_num}. {heading.upper()}")
        print('=' * width)

    # 1. Set up the hex grid.
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


if __name__ == "__main__":
    main()
