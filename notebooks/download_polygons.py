# %%
import pandas as pd
import requests
import json

# %%
kreise = pd.read_csv('../data/gov_kreise_v02_long_lat.csv')

# %%
kreise.head()

# %%
kreise.textual_id

# %% [markdown]
# # Download eines einzelnen Polygons

# %%
r = requests.get('https://gov.genealogy.net/item/geoJson/object_191059')
d = json.loads(r.text)
list_of_lists = d['features'][0]['geometry']['coordinates'][0]

# %%
coord = pd.DataFrame(list_of_lists, columns = ['x', 'y'])
coord['id'] = 'id'
coord

# %% [markdown]
# # Loop zum Download aller Polygone

# %%
gov_ids = kreise.textual_id.drop_duplicates()
gov_url = 'https://gov.genealogy.net/item/geoJson/'

# %%
list_of_dfs = []
for gov_id in gov_ids:
    full_url = gov_url + gov_id
    r = requests.get(full_url)
    d = json.loads(r.text)
    geom_type = d['features'][0]['geometry']['type']
    coords = d['features'][0]['geometry']['coordinates']
    if geom_type == 'Point':
        df = pd.DataFrame([coords], columns = ['x', 'y'])
    elif geom_type == 'LineString':
        df = pd.DataFrame(coords, columns = ['x', 'y'])
    else:
        list_of_lists = d['features'][0]['geometry']['coordinates'][0]
        df = pd.DataFrame(coords[0], columns = ['x', 'y'])
    df['id'] = gov_id
    list_of_dfs.append(df)

# %%
big_df = pd.concat(list_of_dfs, ignore_index=True)

# %%
big_df

# %%
big_df.to_csv('../data/kreise_polygons.csv')
