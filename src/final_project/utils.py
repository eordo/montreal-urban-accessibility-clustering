import geohexgrid as ghg
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from final_project.config import CRS, HEX_RADIUS, IMAGES_DIR, ROOT_DIR


def create_grid(island_shp, agglo_shp):
    # Load the island shapefile.
    island = gpd.read_file(island_shp)
    island = island.to_crs(CRS)
    # Make the grid overlay from the island boundaries.
    grid = (ghg.make_grid_from_gdf(island, R=HEX_RADIUS)
               .assign(cell_id=lambda gdf: range(len(gdf)))
               .set_index('cell_id'))
    # Load the subdivisions.
    agglo = (gpd.read_file(agglo_shp)
                .loc[:,['geometry', 'NOM']]
                .rename(columns={'NOM': 'subdivision'})
                .to_crs(CRS))
    # Assign each cell the borough or municipality that its centroid lies in.
    grid_pts = (grid.copy()
                    .assign(pt=lambda gdf: gdf.geometry.centroid)
                    .set_geometry('pt'))
    grid_pts = gpd.sjoin(grid_pts, agglo, how='left', predicate='within')
    grid = (grid.assign(subdivision=grid_pts['subdivision'].values)
                .dropna())
    return grid


def create_map_plot(title=None):
    fig, ax = plt.subplots(figsize=(8, 8))
    if title is not None:
        ax.set_title(title)
    ax.set_axis_off()
    return fig, ax


def save_figure(fig,
                filename,
                destination=IMAGES_DIR,
                dpi=300,
                bbox_inches='tight',
                transparent=False):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    if not filename.endswith('.png'):
        filename += '.png'
    fig.savefig(
        destination / filename,
        dpi=dpi,
        bbox_inches=bbox_inches,
        transparent=transparent
    )
    print(f"Figure saved to {(destination / filename).relative_to(ROOT_DIR)}")
