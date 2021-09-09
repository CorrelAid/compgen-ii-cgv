import gov_extraction as gc
import pandas as pd
import numpy as np

def test_read_gov_item_01():
    assert gc.read_gov_item().dtypes.to_list() == [np.int32, object, np.int32]

def test_read_names_01():
    assert gc.read_names().dtypes.to_list() == [np.int32, object, object, np.int64, np.int64]

def test_read_types_01():
    assert gc.read_types().dtypes.to_list() == [np.int32, np.int32, np.int64, np.int64]

def test_read_relations_01():
    assert gc.read_relations().dtypes.to_list() == [np.int32, np.int32, np.int64, np.int64, ]