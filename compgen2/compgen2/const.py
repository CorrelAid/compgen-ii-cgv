# ## Definitions

GOV_ITEMS = "gov_a_govitem.csv"
GOV_RELATIONS = "gov_a_relation.csv"
GOV_TYPENAMES = "gov_a_typenames.csv"
PROPERTY_NAMES = "gov_a_propertynames.csv"
PROPERTY_TYPES = "gov_a_propertytypes.csv"
VL_FILE = "deutsche-verlustlisten-1wk.tsv"
LOG_PATH = "log/"

# 2404429 = 1. Januar 1871
# 2404794 = 1. Januar 1872
# 2415021 = 1. Januar 1900
# 2420342 = 28. Juli 1914
# 2421594 = 31. Dezember 1917
# 2421909 = 11. November 1918
# -2147483648 = (-1)*2^31
# 2147483647 = 2^31 - 1
T_BEGIN = 2404794*10 + 2
T_END = 2421594*10 + 2
T_MIN = -2147483648
T_MAX = 2147483647

# 190315=Deutches Reich, 191050=Schweiz, 306245=Österreich-Ungarn, 220100=Liechtenstein, 218129=Luxemburg
SUPERNODES = {190315, 191050, 306245, 220100, 218129}

# Staatsähnliche Gebilde
T_DEUTSCHESREICH_LVL0 = {
    31,
    61,
    23,
    60,
    34,
    16,
    7,
    45,
}

T_DEUTSCHESREICH_LVL1 = {
    201,
    45,
}

T_DEUTSCHESREICH_LVL2 = {
    45,
    32,
}

# Kreisähnliche Gebilde
T_DEUTSCHESREICH_LVL3 = {
    5,
    32,
    36,
    37,
    110,
    78,
    99,
    149,
    212,
    95,
}

# Österreich-Ungarn
T_OESTERREICHUNGARN_LVL0 = {
    215,
}

T_OESTERREICHUNGARN_LVL1 = {
    80,
    23,
    31,
    188,
    137,
    62,
    80,
}

T_OESTERREICHUNGARN_LVL2 = {
    113,
    146,
    270,
    190,
}

# Kreisähnlich Schweiz
T_SCHWEIZ_LVL1 = {
    25,
    134,
}

# Kreisähnlich Luxemburg
T_LUXEMBURG_LVL1 = {
    170,
    25,
}

T_KREISUNDHOEHER = set().union(
    T_DEUTSCHESREICH_LVL0,
    T_DEUTSCHESREICH_LVL1,
    T_DEUTSCHESREICH_LVL2,
    T_DEUTSCHESREICH_LVL3,
    T_OESTERREICHUNGARN_LVL0,
    T_OESTERREICHUNGARN_LVL1,
    T_OESTERREICHUNGARN_LVL2,
    T_LUXEMBURG_LVL1,
    T_SCHWEIZ_LVL1,
)

# Undesired are thes groups of GOV types:
# - Kirche
# - geographische Typen
# - Zivilverwaltung
# - Gericht
# - Verkehrswesen
# - Sonstige
# - special cases:
#   * politische Verwaltung: 223 Landgericht (älterer Ordnung)
# Desired are therefore these groups of GOV types:
# - politische Verwaltung
# - Wohnplatz
TUNDESIRED = {
    47,
    107,
    3,
    19,
    10,
    151,
    202,
    228,
    6,
    9,
    11,
    12,
    13,
    26,
    27,
    28,
    29,
    35,
    41,
    42,
    43,
    44,
    49,
    91,
    92,
    96,
    124,
    153,
    155,
    206,
    210,
    219,
    243,
    244,
    245,
    249,
    250,
    253,
    260,
    263,
    15,
    89,
    119,
    166,
    74,
    98,
    104,
    147,
    187,
    195,
    196,
    197,
    198,
    199,
    200,
    103,
    172,
    242,
    118,
    223,
}
