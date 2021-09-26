# %%
import geopandas
import pandas as pd
import matplotlib.pyplot as plt

# %%
orte = pd.read_csv('../data/gov_orte_v02_long_lat.csv')
kreise = pd.read_csv('../data/gov_kreise_v02_long_lat.csv')

# %%
orte = orte.dropna(subset=['longitude', 'latitude'])

# %%
orte.sort_values(by=['longitude', 'latitude'])

# %%
orte[orte.duplicated(subset = ['longitude', 'latitude'])].sort_values(by=['longitude', 'latitude'])

# %%
orte[orte.duplicated('textual_id')].sort_values(by=['textual_id'])

# %%
geo_orte = geopandas.GeoDataFrame(orte, geometry=geopandas.points_from_xy(orte.longitude, orte.latitude))
geo_kreise = geopandas.GeoDataFrame(kreise, geometry=geopandas.points_from_xy(kreise.longitude, kreise.latitude))
# geo_orte.set_crs(epsg=4326)
# geo_kreise.set_crs(epsg=4326)

# %%
geo_orte.head()

# %%
geo_kreise.head()

# %%
erster_ort = geo_orte.iloc[0]
distances = geo_kreise.geometry.distance(erster_ort.geometry)
distances

# %%
geo_orte['radius'] = geo_orte.geometry.buffer(1000)

# %%
geo_orte_eu = geo_orte[(geo_orte.longitude > 0) & (geo_orte.longitude < 24) & (geo_orte.latitude > 44) & (geo_orte.latitude < 60)]

# %%
world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

# %%
ax = world[world.iso_a3 == 'DEU'].plot(
    color='white', edgecolor='black')
geo_orte_eu.plot(ax=ax, color='red', alpha=0.1, markersize=0.01)
plt.show()

# %%
