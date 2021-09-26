from compgen2 import GOV, Matcher
from compgen2.synthetic import build_test_set

data_root= "../data"

gov = GOV(data_root)
gov.load_data()
gov.build_indices()

# ## Tests

# Test with 100% valid data, so all entries should find a match

matcher = Matcher(gov)
test_data = build_test_set(gov, size=1000, num_parts=2, valid=1)

test_data

matches = matcher.get_match_for_locations(test_data)

matches.id.eq("").sum()

matches[matches.id.eq("")]

# Test with 70% valid data, so 30% should not find a match

matcher = Matcher(gov)
test_data = build_test_set(gov, size=1000, num_parts=2, valid=0.7)

matches = matcher.get_match_for_locations(test_data)

matches.id.eq("").sum()

matches[matches.id.eq("")]


