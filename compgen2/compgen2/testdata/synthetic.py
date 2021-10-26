import random

import pandas as pd


def build_test_set(gov, size: int, num_parts: int = 2, valid: float = 1):
    test_set = []
    population = [p for p in gov.all_paths if 190315 in p and len(p) >= num_parts]
    
    samples = random.sample(population=population, k=size)
    for sample in samples:
        while True:
            sample_nodes = random.sample(sample, k=num_parts)
            try:
                test_set.append(
                    ", ".join(
                        map(
                            lambda id_: random.sample(list(gov.names_by_id[id_]), k=1)[
                                0
                            ],
                            sample_nodes,
                        )
                    )
                )
                break
            except KeyError:
                pass

    if valid < 1:
        num_invalid = int(size * (1 - valid))
        num_invalid_idx = random.sample(range(size), k=num_invalid)
        for i in num_invalid_idx:
            test_set[i] = ", ".join(random.sample(list(gov.names.content.values), k=2))

    return pd.Series(test_set, name="location")
