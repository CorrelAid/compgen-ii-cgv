# -*- coding: utf-8 -*-
# %%
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

# %%
orte = pd.read_csv('../data/gov_orte_v02_long_lat.csv')
kreise = pd.read_csv('../data/gov_kreise_v02_long_lat.csv')
kreise_polygone = pd.read_csv('../data/kreise_polygons.csv')

# %%
orte = orte.drop_duplicates(subset = 'textual_id', keep = 'first')

# %% [markdown]
# 3655 Orte werden gelöscht, die zu einer `textual_id` mehr als eine `id` besitzen. Die geographischen Koordinaten sind dabei aber immmer dieselben.

# %%
geo_orte = gpd.GeoDataFrame(orte, geometry=gpd.points_from_xy(orte.center_longitude, orte.center_latitude), crs = 'epsg:5243')
geo_kreise = gpd.GeoDataFrame(kreise, geometry=gpd.points_from_xy(kreise.center_longitude, kreise.center_latitude), crs = 'epsg:5243')
#geo_orte.set_crs(epsg=4326)
#geo_kreise.set_crs(epsg=4326)
#geo_orte.to_crs({'init': 'epsg:4326'})
#geo_kreise.to_crs({'init': 'epsg:4326'})
# gps: 4326

# %%
print(geo_orte.crs)

# %%
berlin = geo_orte[geo_orte.textual_id == 'BERLINJO62PM']
berlin

# %%
münchen = geo_orte[geo_orte.textual_id == 'adm_139162']
münchen

# %%
berlin.geometry.distance(münchen.geometry)

# %%
geo_kreise.iloc[0, ].geometry

# %%
geo_orte.geometry.distance(geo_kreise.geometry.iloc[0, ])

# %%
geo_kreise['radius'] = geo_orte.geometry.buffer(1000)

# %%
geo_kreise.radius

# %% [markdown]
# # Polygone

# %%
kreise_polygone['points_per_id'] = kreise_polygone.groupby('id').x.transform('count')

# %%
nr_kreise = len(kreise_polygone.id.drop_duplicates())
nr_kreise_pt_1 = len(kreise_polygone[kreise_polygone.points_per_id == 1].id.drop_duplicates())
nr_kreise_pt_2 = len(kreise_polygone[kreise_polygone.points_per_id == 2].id.drop_duplicates())
print(f'''Anzahl aller Kreise: {nr_kreise} 
Anzahl Kreise mit nur einem Punkt als Geo-Information: {nr_kreise_pt_1}
Anzahl Kreise mit nur zwei Punkten als Geo-Information: {nr_kreise_pt_2}
''')

# %% [markdown]
# ## Kreise mit zwei oder weniger Punkten

# %%
kreise_polygone[kreise_polygone.points_per_id == 1].drop_duplicates()

# %%
kreise_polygone[kreise_polygone.points_per_id == 2].drop_duplicates()

# %%
problem_kreise = kreise_polygone[kreise_polygone.points_per_id <= 2].reset_index()

# %%
problem_kreise

# %%
kreise_polygone = kreise_polygone[kreise_polygone.points_per_id > 2]

# %%
geo_orte = gpd.GeoDataFrame(orte, geometry=gpd.points_from_xy(orte.longitude, orte.latitude))
geo_kreise = gpd.GeoDataFrame(kreise_polygone, geometry=gpd.points_from_xy(kreise_polygone.x, kreise_polygone.y))
# geo_orte.set_crs(epsg=4326)
# geo_kreise.set_crs(epsg=4326)

# %%
kreise_polygone['lat_long_list'] = geo_kreise[['x', 'y']].values.tolist()

# %%
kreise_polygone

# %%
kreise_polygone = kreise_polygone.groupby('id')['lat_long_list'].apply(lambda x: Polygon(x.tolist())).reset_index()

# %%
# Declare the result as a new a GeoDataFrame
kreise_polygone = gpd.GeoDataFrame(kreise_polygone, geometry = 'lat_long_list')

# %%
kreise_polygone.plot()

# %% [markdown]
# # Orte

# %%
erster_ort = geo_orte.iloc[0]
distances = geo_kreise.geometry.distance(erster_ort.geometry)
distances

# %%
geo_orte['radius'] = geo_orte.geometry.buffer(1000)

# %%
geo_orte_eu = geo_orte[(geo_orte.longitude > 0) & (geo_orte.longitude < 24) & (geo_orte.latitude > 44) & (geo_orte.latitude < 60)]

# %%
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# %%
ax = world[world.iso_a3 == 'DEU'].plot(
    color='white', edgecolor='black')
geo_orte_eu.plot(ax=ax, color='red', alpha=0.1, markersize=0.01)
plt.show()
