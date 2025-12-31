import geopandas as gpd
import osmnx as ox
import pandas as pd
import json


def combine_pois(dom_pois, osm_pois, metadata_file):
    """
    Combines the DOM and OSM POIs into a single DataFrame.
    """
    with open(metadata_file) as f:
        mappings = json.load(f)
        dom_pois['group'] = dom_pois['type'].apply(lambda x: mappings['dom'][x])
        osm_pois['group'] = osm_pois['type'].apply(lambda x: mappings['osm'][x])
    osm_pois = osm_pois.reset_index(drop=True)
    all_pois = pd.concat([dom_pois, osm_pois])
    return all_pois


def load_dom_pois(places_file, establishments_file, metadata_file):
    """
    Reads and cleans the DOM POIs.
    """
    places = _load_dom_places(places_file, metadata_file)
    establishments = _load_dom_establishments(establishments_file, metadata_file)
    dom_pois = pd.concat([
        places[['name', 'type', 'city', 'longitude', 'latitude']],
        establishments[['name', 'type', 'city', 'longitude', 'latitude']]
    ])
    dom_pois = gpd.GeoDataFrame(
        dom_pois,
        geometry=gpd.points_from_xy(dom_pois.longitude, dom_pois.latitude),
        crs='EPSG:4326')
    dom_pois = dom_pois.drop(columns=['longitude', 'latitude'])
    return dom_pois


def load_osm_pois():
    """
    Queries and cleans POI data from OSM.
    """
    # On-island municipalities besides Montreal.
    cities = [
        "Baie-d'Urfé", "Beaconsfield", "Côte Saint-Luc", 
        "Dollard-des-Ormeaux", "Dorval", "Hampstead", 
        "Kirkland", "L'Île-Dorval", "Montréal-Est",
        "Montreal West", "Mount Royal", "Pointe-Claire", 
        "Sainte-Anne-de-Bellevue", "Senneville", "Westmount"
    ]
    # If uncached, this will take around 20 sec.
    gdf = gpd.GeoDataFrame(pd.concat([
        ox.geocode_to_gdf((f'{city}, Quebec, Canada')) for city in cities]))
    # Tags chosen to match DOM POIs as closely as possible.
    amenity_tags = [
        # Healthcare
        'clinic',
        'social_facility'
        # Education
        'college',
        'kindergarten',
        'school',
        'university'
        # Recreation
        'arts_centre'
        'cinema',
        'library',
        'theatre',
        # Community
        'community_centre',
        'exhibition_centre'
        'library',
        'social_centre',
        # Mobility
        'mobility_hub',
        'bus_station',
        # Government
        'courthouse',
        'townhall'
    ]
    government_tags = [
        'public_service',
        'social_services'
    ]
    leisure_tags = [
        'fitness_centre',
        'fitness_station',
        'garden',
        'marina',
        'park',
        'sports_centre',
        'sports_hall',
        'swimming_pool'
    ]
    place_tags = [
        'square'
    ]
    shop_tags = [
        'mall'
    ]
    station_tags = [
        'subway',
        'train'
    ]
    tourism_tags = [
        'gallery'
        'museum'
    ]
    all_tags = {
        'amenity': amenity_tags,
        'government': government_tags,
        'leisure': leisure_tags,
        'place': place_tags,
        'shop': shop_tags,
        'station': station_tags,
        'tourism': tourism_tags
    }
    # If uncached, this will take about 20 sec.
    osm_pois = ox.features_from_polygon(gdf.unary_union, tags=all_tags)
    # Compress the tag columns into one column. 
    city_gdfs = []
    for tag in all_tags.keys():
        if tag in osm_pois.columns:
            gdf = osm_pois[~osm_pois[tag].isna()][
                ['name', 'addr:city', tag, 'geometry']
            ]
            gdf = gdf.rename(columns={'addr:city': 'city', tag: 'type'})
            city_gdfs.append(gdf)
    osm_pois = gpd.GeoDataFrame(pd.concat(city_gdfs))
    return osm_pois


def _load_dom_establishments(filename, metadata_file):
    """
    Reads and cleans the Open Data Montreal data set "Établissements 
    alimentaires".
    """
    establishments = pd.read_csv(filename)
    establishments = establishments[
        ['business_id', 'name', 'city', 'type', 
        'statut', 'latitude', 'longitude']
    ]
    establishments = establishments.rename(columns={
        'business_id': 'id',
        'statut': 'status',
        'date_statut': 'status_date'
    })
    # Translate from French to English using metadata.
    _map_metadata(
        establishments,
        metadata_file,
        columns=['type', 'status'])
    # Select desired types.
    establishments = establishments[establishments['type'].isin([
        'Bakery',
        'Brewery',
        'Butcher',
        'Butcher-Grocery',
        'Caterer',
        'Coffee, Tea, Herbal Infusion',
        'Confectionery / Chocolate Shop',
        'Dairy Bar',
        'Daycare',
        'Deli',
        'Deli / Cheese Shop',
        'Department Store',
        'Fast Food Restaurant',
        'Fish Market',
        'Food Aid Organization',
        'Food Truck',
        'Grocery Store',
        'Grocery with Prepared Food',
        'Hospital',
        'Kiosk',
        'Lounge Bar, Tavern',
        'Natural Foods',
        'Pastry Shop / Bakery',
        'Public Market',
        'Ready-to-Eat Fruits and Vegetables',
        'Restaurant',
        'Senior Residence',
        'Snack Bar',
        'Sugar Shack',
        'Supermarket',
        'Takeout Restaurant'
    ])]
    # Drop closed establishments.
    establishments = establishments[establishments['status'] != 'Closed']
    return establishments


def _load_dom_places(filename, metadata_file):
    """
    Reads and cleans the Open Data Montreal data set "Lieux d'intérêt".
    """
    places = pd.read_csv(filename)
    places = places[
        ['ID', 'Famille', 'Catégorie', 'Nom français', 'Type',
        'Ville', 'Code postal', 'Arrondissement', 'Longitude', 'Latitude']
    ]
    places = places.rename(columns={
        'Famille': 'family',
        'Catégorie': 'category',
        'Nom français': 'name',
        'Ville': 'city',
        'Code postal': 'postal_code',
        'Arrondissement': 'borough'
    })
    places.columns = places.columns.map(str.lower)
    # Translate from French to English using metadata.
    _map_metadata(
        places,
        metadata_file,
        columns=['family', 'category', 'type'])
    # Drop unwanted categories and types.
    places = places[~places['category'].isin([
        'Accommodation',
        'Emergency Service',
        'Public Art',
        'Tourist Information'
    ])]
    places = places[~places['type'].isin([
        'Architectural / Design Building',
        'Commercial Tourist Attraction',
        'Consular Service',
        'Convention / Exhibition Center',
        'Historic / Heritage Building',
        'International Agency',
        'Public Toilet',
        'Recovery and Sorting Center',
        'Taxi Waiting Stand'
    ])]
    return places


def _map_metadata(df, metadata_file, columns):
    """
    Maps metadata values to the input columns.
    """
    with open(metadata_file) as f:
        mappings = json.load(f)
        for col in columns:
            df[col] = df[col].apply(lambda x: mappings[col][x])
