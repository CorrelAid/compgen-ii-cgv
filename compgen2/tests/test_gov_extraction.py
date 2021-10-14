from compgen2 import GOV
import numpy as np
import pytest

@pytest.fixture
def gov(data_root):
    gov = GOV(data_root)
    return gov

def test_read_gov_data(gov):
    gov.load_data()
    assert gov.items.dtypes.to_list() == [np.int32, object, bool]
    assert gov.names.dtypes.to_list() == [np.int32, object, object, np.int64, np.int64]
    assert gov.types.dtypes.to_list() == [np.int32, np.int32, np.int64, np.int64]
    assert gov.relations.dtypes.to_list() == [np.int32, np.int32, np.int64, np.int64]
    assert gov.type_names.dtypes.to_list() == [int, object, object]


def test_build_paths(gov):
    gov.load_data()
    gov.build_indices()
    paths = gov.all_paths
    assert isinstance(paths, set)
    assert all(isinstance(path, tuple) for path in paths)
    assert all(isinstance(id_, int) for path in paths for id_ in path)
