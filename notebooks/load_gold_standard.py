# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
import numpy as np

# %%
gold_long = pd.read_csv("./data/gold_long.csv", sep = "\t")
gold_work = pd.read_csv("./data/gold_work.csv", sep = "\t")

# %%
gold_long

# %%
gold_long["dse ID"].isna().sum()  / len(gold_work)

# %% [markdown]
# 14% aller Orte konnten auch händisch nicht zugeordnet werden.

# %%
gold_work

# %%
gold_work[8:15]

# %%
gold_work["DSE decision"].isna().sum() / len(gold_work)

# %% [markdown]
# 12% aller Orte konnten auch händisch nicht zugeordnet werden.

# %%
