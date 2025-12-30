# Montreal Urban Accessibility Clustering

This is a revised version of my submission for the final project in HES CSCI 108 "Data Mining, Discovery, and Exploration."
It is substantively and technically the same as the original submission but with minor revisions for code structure, clarity, and presentation.

Some of the raw data is too large to upload, so all data apart from the OpenStreetMap networks is linked below instead.
Some processed and precomputed features are included here to facilitate reproducibility.

The notebooks outline the steps, rationale, and code used for the analysis and to create the figures.
Run them in order to reproduce my report.

## Environment

Install all third-party and local dependencies to run the code.
I recommend using [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/eordo/montreal-urban-accessibility-clustering
cd montreal-urban-accessibility-clustering
uv sync
uv pip install -e .
```

## Data

All data pertaining to the city of Montreal is sourced from the city's open data portal.
Census data and boundaries are from Statistics Canada.

**Points of Interest**

- [Places of interest](https://donnees.montreal.ca/dataset/lieux-d-interet)
- [Food establishments](https://donnees.montreal.ca/dataset/etablissements-alimentaires)

**Geography**

- [Island boundaries](https://donnees.montreal.ca/dataset/limites-terrestres)
- [Urban agglomeration boundaries](https://donnees.montreal.ca/en/dataset/limites-administratives-agglomeration)
- [Dissemination area boundaries](https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm?year=21)
- [STM bus and metro stops](https://donnees.montreal.ca/en/dataset/stm-traces-des-lignes-de-bus-et-de-metro)

**Demographics**

- [2021 Census Profile](https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm)

For the dissemination area boundaries, check "Digital Boundary Files (DBF)" under **Type**, "Dissemination areas" under **Statistical boundaries**, and "Shapefile (.shp)" under **Format**.

For the Census Profile tables, download the CSV for "Canada, provinces, territories, census divisions (CDs), census subdivisions (CSDs) and dissemination areas (DAs) - Quebec only."
