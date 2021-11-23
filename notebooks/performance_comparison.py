# -*- coding: utf-8 -*-
# only run if you are developping/debugging
# # !pip install line_profiler
# %load_ext line_profiler
# %load_ext autoreload
# %autoreload 2

# +
from pathlib import Path

import pandas as pd
import random

from compgen2 import Gov, Matcher, GovTestData, Preprocessing_VL
from compgen2.const import FILENAME_VL, FILENAME_GOV_TEST_SET
from compgen2.testdata import sample_test_set_from_gov, Synthetic, get_accuracy

random.seed(1337)
# -

data_root= Path("../data")

# ## Test sets
# We use 4 test sets:
# - different sample sets from the file "deutsche-verlustlisten-1wk"
# - different sample sets from the gov database 
# - different sample sets from a synthetic data set that tries to mimic the errors found in the original "verlustliste"
# - manually collected correction suggestions from http://wiki-de.genealogy.net/Verlustlisten_Erster_Weltkrieg/Projekt/Ortsnamen
#
# All test sets change when preprocessing is applied.
#
# **Note**: We have a ground truth for all test setsbut the first one as the "verlustliste" is the actual problem we want to solve. So for the test set "verlustliste" we cannot calculate an accuracy score but we can compare who many items we were able to match. Assumption is that more matches are, in general, better.

# ## Test suite without Preprocessing -> Baseline

gov = Gov(data_root)
gov.load_data()
gov.build_indices()

# +
# Test Set 1: VL
assert data_root.joinpath(FILENAME_VL).exists()
test_set_size = 1000

vl = pd.read_parquet(data_root / FILENAME_VL)  # location column has the test data, truth is unknown

vl_test_sets = []
vl_test_sets.append(("vl test set with loc_count=1", vl.query("loc_parts_count == 1").sample(test_set_size)))
vl_test_sets.append(("vl test set with loc_count=2", vl.query("loc_parts_count == 2").sample(test_set_size)))
vl_test_sets.append(("vl test set with loc_count=3", vl.query("loc_parts_count == 3").sample(test_set_size)))
vl_test_sets.append(("vl test set containing '.'", vl[vl.location.str.contains(".", regex=False)].sample(test_set_size)))

# +
# Test Set 2: Gov database
test_set_size = 1000

gov_test_sets = []
gov_test_sets.append(("gov test set with loc_count=1 and valid=1", sample_test_set_from_gov(gov, size=test_set_size, num_parts=1, valid=1)))
gov_test_sets.append(("gov test set with loc_count=1 and valid=0.7", sample_test_set_from_gov(gov, size=test_set_size, num_parts=1, valid=0.7)))
gov_test_sets.append(("gov test set with loc_count=2 and valid=1", sample_test_set_from_gov(gov, size=test_set_size, num_parts=2, valid=1)))
gov_test_sets.append(("gov test set with loc_count=2 and valid=0.7", sample_test_set_from_gov(gov, size=test_set_size, num_parts=2, valid=0.7)))
gov_test_sets.append(("gov test set with loc_count=3 and valid=1", sample_test_set_from_gov(gov, size=test_set_size, num_parts=3, valid=1)))
gov_test_sets.append(("gov test set with loc_count=3 and valid=0.7", sample_test_set_from_gov(gov, size=test_set_size, num_parts=3, valid=0.7)))

# +
# Test Set 3: Synthetic
test_set_size = 1000

syn = Synthetic(gov)

syn_test_sets = []
syn_test_sets.append(("syn test set with default probabilities", syn.create_synthetic_test_set(test_set_size)))

# +
# Test Set 4: GovTestData
assert data_root.joinpath(FILENAME_GOV_TEST_SET).exists()

gtd = GovTestData(gov)
gtd_test_sets = []
gtd_test_sets.append(("gov test set", gtd.get_test_set()))
# -

# ### Run the tests

# Test Set 1

for name, test_set in vl_test_sets:
    m = Matcher(gov)
    print("Running", name)
    m.get_match_for_locations(test_set.location)
    total_matches = len([match for match in m.results.values() if match.get("possible_matches")])
    print(f"Total matches: {total_matches} ({total_matches / len(test_set)}%).")

# Test Set 2

for name, test_set in gov_test_sets:
    m = Matcher(gov)
    print("Running", name)
    m.get_match_for_locations(test_set.location)
    total_matches = len([match for match in m.results.values() if match.get("possible_matches")])
    print(f"Total matches: {total_matches} ({total_matches / len(test_set)}%).")
    
    accuracy = get_accuracy(m.results, test_set)
    print("Accuracy (entries where all parts of truth are in possible matches):", round(accuracy, 2))

# Test Set 3

for name, test_set in syn_test_sets:
    m = Matcher(gov)
    print("Running", name)
    m.get_match_for_locations(test_set.location)
    total_matches = len([match for match in m.results.values() if match.get("possible_matches")])
    print(f"Total matches: {total_matches} ({total_matches / len(test_set)}%).")
    
    accuracy = get_accuracy(m.results, test_set)
    print("Accuracy (entries where all parts of truth are in possible matches):", round(accuracy, 2))

# Test Set 4

for name, test_set in gtd_test_sets:
    m = Matcher(gov)
    print("Running", name)
    m.get_match_for_locations(test_set.location)
    total_matches = len([match for match in m.results.values() if match.get("possible_matches")])
    print(f"Total matches: {total_matches} ({total_matches / len(test_set)}%).")
    
    accuracy = get_accuracy(m.results, test_set)
    print("Accuracy (entries where all parts of truth are in possible matches):", round(accuracy, 2))

# ## Test suite with VL Preprocessing




# ## Test suite with VL + Gov Preprocessing


