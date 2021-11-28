# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
# only run if you are developping/debugging
# # !pip install line_profiler
# %load_ext line_profiler
# %load_ext autoreload
# %autoreload 2

# %%
from pathlib import Path

import pandas as pd
import random

from collections import Counter

from compgen2 import Gov, Matcher, GovTestData, Preprocessing
from compgen2.const import FILENAME_VL, FILENAME_GOV_TEST_SET
from compgen2.testdata import sample_test_set_from_gov, Synthetic, get_accuracy

random.seed(1337)

# %%
data_root= Path("../data")

# %%
# settings for matcher
matcher_params = {
    "use_difflib": True,  # False will use levenshtein
    "use_phonetic": True,
    "max_cost": 3,
    "search_kreis_first": True,
}

# %%
preprocess_truth = True
preprocess_gov = True

# %%
run_vl_tests = True
run_syn_tests = True
run_gov_web_tests = True

# %%
final_results = []
test_set_names = []

# %% [markdown]
# ## Test sets
# We use 3 test sets:
# - different sample sets from the file "deutsche-verlustlisten-1wk", here is no truth known, so we can only report total matches
# - different sample sets from a synthetic data set that tries to mimic the errors found in the original "verlustliste"
# - manually collected correction suggestions from http://wiki-de.genealogy.net/Verlustlisten_Erster_Weltkrieg/Projekt/Ortsnamen
#
# All test sets change when preprocessing is applied.
#
# **Note**: We have a ground truth for all test setsbut the first one as the "verlustliste" is the actual problem we want to solve. So for the test set "verlustliste" we cannot calculate an accuracy score but we can compare who many items we were able to match. Assumption is that more matches are, in general, better.

# %% [markdown]
# ### Creating the test sets

# %%
gov = Gov(data_root)
gov.load_data()
gov.build_indices()

# %%
# Test Set 1: VL
assert data_root.joinpath(FILENAME_VL).exists()
test_set_size = 100

vl = pd.read_parquet(data_root / FILENAME_VL)  # location column has the test data, truth is unknown

vl_test_sets = []
vl_test_sets.append(("vl test set with loc_count=1", vl.query("loc_parts_count == 1").sample(test_set_size)))
vl_test_sets.append(("vl test set with loc_count=2", vl.query("loc_parts_count == 2").sample(test_set_size)))
vl_test_sets.append(("vl test set with loc_count=3", vl.query("loc_parts_count == 3").sample(test_set_size)))
vl_test_sets.append(("vl test set containing '.'", vl[vl.location.str.contains(".", regex=False)].sample(test_set_size)))

# %%
# Test Set 2: Synthetic
test_set_size = 100

syn = Synthetic(gov)

syn_test_sets = []
syn_test_sets.append(("syn test set with loc_count=1 and distortion=0.", syn.create_synthetic_test_set(size=test_set_size, num_parts=1, distortion_factor=0.)))
syn_test_sets.append(("syn test set with loc_count=1 and distortion=1.", syn.create_synthetic_test_set(size=test_set_size, num_parts=1, distortion_factor=1.)))
syn_test_sets.append(("syn test set with loc_count=2 and distortion=0.", syn.create_synthetic_test_set(size=test_set_size, num_parts=2, distortion_factor=0.)))
syn_test_sets.append(("syn test set with loc_count=2 and distortion=1.", syn.create_synthetic_test_set(size=test_set_size, num_parts=2, distortion_factor=1.)))
syn_test_sets.append(("syn test set with loc_count=3 and distortion=0.", syn.create_synthetic_test_set(size=test_set_size, num_parts=3, distortion_factor=0.)))
syn_test_sets.append(("syn test set with loc_count=3 and distortion=1.", syn.create_synthetic_test_set(size=test_set_size, num_parts=3, distortion_factor=1.)))

# %%
# Test Set 3: GovTestData
assert data_root.joinpath(FILENAME_GOV_TEST_SET).exists()

gtd = GovTestData(gov)
gtd_test_sets = []
gtd_test_sets.append(("gov web test set", gtd.get_test_set()))

# %% [markdown]
# ### Test suite without Preprocessing -> Baseline

# %%
test_set_names.append("Baseline")
result_row = []

# %% [markdown]
# Test Set 1

# %% tags=[]
if run_vl_tests:
    for name, test_set in vl_test_sets:
        m = Matcher(gov, **matcher_params)
        print("Rsnunning", name)
        m.get_match_for_locations(test_set.location)
        print(Counter(v["anchor_method"] for v in m.results.values()))

        total_matches = len([match for match in m.results.values() if match.get("possible_matches")])
        print(f"Total matches: {total_matches} ({round(total_matches / test_set.location.nunique() * 100, 4)}%).")
        print()

        result_row.append(total_matches / test_set.location.nunique())

# %% [markdown]
# Test Set 2

# %%
if run_syn_tests:
    for name, test_set in syn_test_sets:
        m = Matcher(gov, **matcher_params)
        print("Running", name)
        m.get_match_for_locations(test_set.location)
        print(Counter(v["anchor_method"] for v in m.results.values()))

        total_matches = len([match for match in m.results.values() if match.get("possible_matches")])
        print(f"Total matches: {total_matches} ({round(total_matches /  test_set.location.nunique() * 100, 4)}%).")

        accuracy = get_accuracy(m.results, test_set)
        print("Accuracy (entries where all parts of truth are in possible matches):", round(accuracy, 4))
        print()

        result_row.append(total_matches / test_set.location.nunique())
        result_row.append(accuracy)

# %% [markdown]
# Test Set 3

# %%
if run_gov_web_tests:
    for name, test_set in gtd_test_sets:
        m = Matcher(gov, **matcher_params)
        print("Running", name)
        m.get_match_for_locations(test_set.location)
        print(Counter(v["anchor_method"] for v in m.results.values()))


        total_matches = len([match for match in m.results.values() if match.get("possible_matches")])
        print(f"Total matches: {total_matches} ({round(total_matches /  test_set.location.nunique() * 100, 4)}%).")

        accuracy = get_accuracy(m.results, test_set)
        print("Accuracy (entries where all parts of truth are in possible matches):", round(accuracy, 4))
        print()

        result_row.append(total_matches / test_set.location.nunique())
        result_row.append(accuracy)

# %%
final_results.append(result_row)

# %% [markdown]
# ### Test suite with VL + Gov Preprocessing - replace corrections and characters, no substitution

# %%
test_set_names.append(f"Preprocessing locations - gov: {preprocess_gov} - replace corrections and characters.")
result_row = []

# %%
for _, test_set in vl_test_sets + syn_test_sets + gtd_test_sets:
    test_set.location = Preprocessing.replace_corrections_vl(test_set.location).str.strip()
    test_set.location = Preprocessing.replace_characters_vl(test_set.location).str.strip()
    
    if "truth" in test_set and preprocess_truth:
        test_set.truth = Preprocessing.replace_characters_gov(test_set.truth).str.strip()

# %%
from collections import defaultdict

# %%
if preprocess_gov:
    old_names = list(gov.ids_by_name.keys())
    new_names = Preprocessing.replace_characters_gov(pd.Series(old_names, dtype=str)).str.strip()

    ids_by_pname = defaultdict(set)
    for old_name, new_name in zip(old_names, new_names):
        ids_by_pname[new_name] |= gov.ids_by_name[old_name]
    ids_by_pname.default_factory = None
    gov.ids_by_name = ids_by_pname

    pnames_by_id = defaultdict(set)
    for k, v in ids_by_pname.items():
        for i in v:
            pnames_by_id[i] |= {k}
    pnames_by_id.default_factory = None
    gov.names_by_id = pnames_by_id

# %% [markdown]
# Test Set 1

# %%
if run_vl_tests:
    for name, test_set in vl_test_sets:
        m = Matcher(gov, **matcher_params)
        print("Running", name)
        m.get_match_for_locations(test_set.location)
        print(Counter(v["anchor_method"] for v in m.results.values()))

        total_matches = len([match for match in m.results.values() if match.get("possible_matches")])
        print(f"Total matches: {total_matches} ({round(total_matches / test_set.location.nunique() * 100, 4)}%).")
        print()

        result_row.append(total_matches / test_set.location.nunique())

# %% [markdown]
# Test Set 2

# %%
if run_syn_tests:
    for name, test_set in syn_test_sets:
        m = Matcher(gov, **matcher_params)
        print("Running", name)
        m.get_match_for_locations(test_set.location)
        print(Counter(v["anchor_method"] for v in m.results.values()))

        total_matches = len([match for match in m.results.values() if match.get("possible_matches")])
        print(f"Total matches: {total_matches} ({round(total_matches /  test_set.location.nunique() * 100, 4)}%).")

        accuracy = get_accuracy(m.results, test_set)
        print("Accuracy (entries where all parts of truth are in possible matches):", round(accuracy, 4))
        print()

        result_row.append(total_matches / test_set.location.nunique())
        result_row.append(accuracy)

# %% [markdown]
# Test Set 3

# %%
if run_gov_web_tests:
    for name, test_set in gtd_test_sets:
        m = Matcher(gov, **matcher_params)
        print("Running", name)
        m.get_match_for_locations(test_set.location)
        print(Counter(v["anchor_method"] for v in m.results.values()))

        total_matches = len([match for match in m.results.values() if match.get("possible_matches")])
        print(f"Total matches: {total_matches} ({round(total_matches /  test_set.location.nunique() * 100, 4)}%).")

        accuracy = get_accuracy(m.results, test_set)
        print("Accuracy (entries where all parts of truth are in possible matches):", round(accuracy, 4))
        print()

        result_row.append(total_matches / test_set.location.nunique())
        result_row.append(accuracy)

# %%
final_results.append(result_row)

# %% [markdown]
# ### Test suite with VL + Gov Preprocessing - replace corrections and characters + substitution

# %%
test_set_names.append(f"Preprocessing locations - gov: {preprocess_gov} - replace corrections + characters + substitution.")
result_row = []

# %%
for _, test_set in vl_test_sets + syn_test_sets + gtd_test_sets:
    test_set.location = Preprocessing.substitute_partial_words(test_set.location, data_root).str.strip()
    test_set.location = Preprocessing.substitute_delete_words(test_set.location, data_root).str.strip()
    test_set.location = Preprocessing.substitute_full_words(test_set.location, data_root).str.strip()
    
    if "truth" in test_set and preprocess_truth:
        test_set.truth = Preprocessing.substitute_partial_words(test_set.truth, data_root).str.strip()
        test_set.truth = Preprocessing.substitute_delete_words(test_set.truth, data_root).str.strip()
        test_set.truth = Preprocessing.substitute_full_words(test_set.truth, data_root).str.strip()

# %%
from collections import defaultdict

if preprocess_gov:
    old_names = list(gov.ids_by_name.keys())
    new_names = Preprocessing.substitute_partial_words(pd.Series(old_names), data_root).str.strip()
    new_names = Preprocessing.substitute_delete_words(pd.Series(new_names), data_root).str.strip()
    new_names = Preprocessing.substitute_full_words(pd.Series(new_names), data_root).str.strip()

    ids_by_pname = defaultdict(set)
    for old_name, new_name in zip(old_names, new_names):
        ids_by_pname[new_name] |= gov.ids_by_name[old_name]
    ids_by_pname.default_factory = None
    gov.ids_by_name = ids_by_pname

    pnames_by_id = defaultdict(set)
    for k, v in ids_by_pname.items():
        for i in v:
            pnames_by_id[i] |= {k}
    pnames_by_id.default_factory = None
    gov.names_by_id = pnames_by_id

# %% [markdown]
# Test Set 1

# %%
if run_vl_tests:
    for name, test_set in vl_test_sets:
        m = Matcher(gov, **matcher_params)
        print("Running", name)
        m.get_match_for_locations(test_set.location)
        print(Counter(v["anchor_method"] for v in m.results.values()))


        total_matches = len([match for match in m.results.values() if match.get("possible_matches")])
        print(f"Total matches: {total_matches} ({round(total_matches / test_set.location.nunique() * 100, 4)}%).")
        print()

        result_row.append(total_matches / test_set.location.nunique())

# %% [markdown]
# Test Set 2

# %%
if run_syn_tests:
    for name, test_set in syn_test_sets:
        m = Matcher(gov, **matcher_params)
        print("Running", name)
        m.get_match_for_locations(test_set.location)
        print(Counter(v["anchor_method"] for v in m.results.values()))


        total_matches = len([match for match in m.results.values() if match.get("possible_matches")])
        print(f"Total matches: {total_matches} ({round(total_matches /  test_set.location.nunique() * 100, 4)}%).")

        accuracy = get_accuracy(m.results, test_set)
        print("Accuracy (entries where all parts of truth are in possible matches):", round(accuracy, 4))
        print()

        result_row.append(total_matches / test_set.location.nunique())
        result_row.append(accuracy)

# %% [markdown]
# Test Set 3

# %%
if run_gov_web_tests:
    for name, test_set in gtd_test_sets:
        m = Matcher(gov, **matcher_params)
        print("Running", name)
        m.get_match_for_locations(test_set.location)
        print(Counter(v["anchor_method"] for v in m.results.values()))

        total_matches = len([match for match in m.results.values() if match.get("possible_matches")])
        print(f"Total matches: {total_matches} ({round(total_matches /  test_set.location.nunique() * 100, 4)}%).")

        accuracy = get_accuracy(m.results, test_set)
        print("Accuracy (entries where all parts of truth are in possible matches):", round(accuracy, 4))
        print()

        result_row.append(total_matches / test_set.location.nunique())
        result_row.append(accuracy)

# %%
final_results.append(result_row)

# %% [markdown]
# ## Auswertung

# %%
names = []
for name, test_set in vl_test_sets + syn_test_sets + gtd_test_sets:
    for metric in ['total matches', 'accuracy']:
        if name.startswith("vl") and not run_vl_tests:
            continue
        
        if name.startswith("syn") and not run_syn_tests:
            continue
            
        if name.startswith("gov") and not run_gov_web_tests:
            continue               
        
        if name.startswith("vl") and metric == 'accuracy':
            continue
            
        names.append(name + ' ' + metric)
        
final_results = pd.DataFrame(final_results, columns=names)

# %%
final_results["test set"] = test_set_names

# %%
final_results = final_results.set_index("test set")

# %%
from datetime import datetime

# %%
final_results.to_csv(f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}_vl_{run_vl_tests}_syn_{run_syn_tests}_gov_{run_gov_web_tests}.csv")

# %% [markdown]
# ## Spielwiese

# %%
test_set = vl[vl.location.str.contains(".", regex=False)].sample(100)
test_set

# %%
gov = Gov(data_root)
gov.load_data()
gov.build_indices()

# %%
m = Matcher(gov, **matcher_params)
m.get_match_for_locations(test_set.location)

# %%
results_without_prep = m.results

# %%
len([(loc, match) for loc, match in m.results.items() if not match["possible_matches"]])

# %%
#location = pd.Series(["neustadt o.s."])
test_set_prep = test_set.copy()

test_set_prep.location = Preprocessing.replace_corrections_vl(test_set_prep.location)
test_set_prep.location = Preprocessing.replace_characters_vl(test_set_prep.location)
test_set_prep.location = Preprocessing.substitute_partial_words(test_set_prep.location, data_root)
test_set_prep.location = Preprocessing.substitute_delete_words(test_set_prep.location, data_root)
test_set_prep.location = Preprocessing.substitute_full_words(test_set_prep.location, data_root)

# %%
idx = test_set.location.str.lower() != test_set_prep.location.str.lower()
pd.DataFrame([test_set.location[idx], test_set_prep.location[idx]]).T

# %%
from collections import defaultdict

old_names = list(gov.ids_by_name.keys())
new_names = Preprocessing.substitute_partial_words(pd.Series(old_names), data_root)
new_names = Preprocessing.substitute_delete_words(pd.Series(new_names), data_root)
new_names = Preprocessing.substitute_full_words(pd.Series(new_names), data_root)

ids_by_pname = defaultdict(set)
for old_name, new_name in zip(old_names, new_names):
    ids_by_pname[new_name] |= gov.ids_by_name[old_name]
ids_by_pname.default_factory = None
gov.ids_by_name = ids_by_pname

pnames_by_id = defaultdict(set)
for k, v in ids_by_pname.items():
    for i in v:
        pnames_by_id[i] |= {k}
pnames_by_id.default_factory = None
gov.names_by_id = pnames_by_id

# %%
m = Matcher(gov, **matcher_params)
m.get_match_for_locations(test_set_prep.location)

# %%
results_with_prep = m.results

# %%
len([(loc, match) for loc, match in m.results.items() if not match["possible_matches"]])

# %% tags=[]
print(len([(part, partdict) for part, partdict in results_with_prep.items() if not partdict["possible_matches"]]))
[(part, partdict) for part, partdict in results_with_prep.items() if not partdict["possible_matches"]]

# %%
# neddemin, neubrandenburg, mecklenburg
gov.ids_by_name["neddemin"]

# %%
gov.all_reachable_nodes_by_id[356042]

# %%
gov.decode_path_name(gov.all_reachable_nodes_by_id[356042])

# %% tags=[]
gov.all_reachable_nodes_by_id

# %%
m = Matcher(gov, **matcher_params)
m.get_match_for_locations(['geispolsheim, erstein, elsaß'])

# %%
m.results

# %%
gov.ids_by_name['geispolsheim']

# %%
for id in gov.ids_by_name['geispolsheim']:
    print([gov.names_by_id[id] for id in gov.all_reachable_nodes_by_id[id]])

# %%
for id in gov.ids_by_name['erstein']:
    print([gov.names_by_id[id] for id in gov.all_reachable_nodes_by_id[id]])

# %%
ids_geispolsheim = set().union(*(gov.all_reachable_nodes_by_id[id] for id in gov.ids_by_name['geispolsheim']))

# %%
ids_erstein = set().union(*(gov.all_reachable_nodes_by_id[id] for id in gov.ids_by_name['erstein']))

# %%
gov.decode_path_name(ids_geispolsheim & ids_erstein)

# %%
gov.ids_by_name["unter-elsaß"]

# %%
set().union(*(gov.names_by_id[id] for id in gov.all_reachable_nodes_by_id[266451]))

# %%
