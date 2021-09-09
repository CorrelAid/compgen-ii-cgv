import pandas as pd
from pathlib import Path

gov_dir = r"D:\OneDrive\1 Projects\CorrelAid\compgen II\datenablage_npo"

# +
gov_files = list(Path(gov_dir).glob("gov_t_*.csv"))

for file in gov_files:
    print("loading", file.name, "as", file.stem)
    exec(f"{file.stem} = pd.read_csv(r'{file}', sep='\t')")
# -

gov_t_govitem.head()

gov_t_propertynames.head()

gov_t_propertytypes.head()

gov_t_relation.head()

gov_t_typenames.head()

# # Merge Data

# ?pd.DataFrame.merge

# (347273, 4)
gov_t_propertynames.id.value_counts()

gov_t_propertynames.content.value_counts()

merged_content = gov_t_propertynames.groupby("id").content.apply(list)
gov_propertynames = pd.DataFrame(merged_content)

gov_propertynames

# left outer join -> keep all names from left and match with right
# problem: propertytype is not unique!
# validate: many_to_one is hurt
gov_propertynames.merge(gov_t_propertytypes, how="left", left_index=True, right_on="id", suffixes=('_names', '_types')).query("id == 268036")

gov_t_propertytypes.id.value_counts()

gov_t_propertytypes.merge(gov_t_typenames, how="left", left_on="content", right_on="type_id", validate="many_to_one")

# +
gov_types = gov_t_propertytypes.merge(gov_t_typenames, how="left", left_on="content", right_on="type_id", validate="many_to_one")

gov_types
# -

merged_content = gov_types.groupby("id").value.apply(list)
gov_types = pd.DataFrame(merged_content)

gov_types

# left outer join -> keep all names from left and match with right
df_right = gov_types
gov_names_and_types = gov_propertynames.merge(df_right, how="left", on="id", suffixes=('_names', '_types'), validate="one_to_one")

gov_names_and_types

gov_names_and_types.loc[1136631]

gov_names_and_types = gov_names_and_types.merge(gov_t_govitem, how="left", on="id", validate="one_to_one")

gov_names_and_types

gov_t_relation.groupby("child").parent.apply(list)

gov_t_relation.merge(gov_propertynames, how="left", left_on="child", right_on="id")

gov_t_relation["child_name"] = gov_t_relation.merge(gov_propertynames, how="left", left_on="child", right_on="id", validate="many_to_one").content
gov_t_relation["parent_name"] = gov_t_relation.merge(gov_propertynames, how="left", left_on="parent", right_on="id", validate="many_to_one").content
gov_t_relation["parent_id"] = gov_t_relation.merge(gov_propertynames, how="left", left_on="parent", right_on="id", validate="many_to_one").content

gov_t_relation.query("child == 500")

import numpy as np
gov_relations = pd.DataFrame(gov_t_relation.groupby("child").parent_name.apply(list).apply(np.array, dtype="object").apply(np.ndarray.flatten))
gov_relations["parent_id"] = gov_t_relation.groupby("child").parent.apply(list)

gov_relations

gov_complete = gov_names_and_types.merge(gov_relations, how="left", left_on="id", right_on="child", validate="one_to_one")

gov_complete

# ## Tests

gov_complete.parent_name.isin([["Berlin"]]).any()

gov_complete.query("content in [['Berlin']]")

gov_complete.query("content in [['Aachen']]")

gov_complete.query("content in [['Forst']]")


