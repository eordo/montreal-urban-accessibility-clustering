from pathlib import Path


# Project root directory.
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
# Define directories relative to root.
IMAGES_DIR = ROOT_DIR / 'images'
DATA_DIR = ROOT_DIR / 'data'
FEATURES_DIR = DATA_DIR / 'features'
META_DIR = DATA_DIR / 'meta'
RAW_DIR = DATA_DIR / 'raw'

# CRS most appropriate for grid projections in Quebec.
CRS = 32188

# Parameters.
HEX_RADIUS = 250 # meters
TRAVEL_TIME = 15 # minutes
WALKING_SPEED = 5 # kph
WALKING_DISTANCE = WALKING_SPEED * (TRAVEL_TIME / 60) * 1000
