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

# Deutsches Reich
T_DEUTSCHESREICH_LVL0 = {
    130,
}
T_DEUTSCHESREICH_LVL1 = {
    31,
    61,
    23,
    60,
    34,
    16,
    7,
    45,
}
T_DEUTSCHESREICH_LVL2 = {
    201,
    45,
}
T_DEUTSCHESREICH_LVL3 = {
    46,
    100,
    45,
    32,
}
# Kreisähnliche Gebilde
T_DEUTSCHESREICH_LVL4 = {
    5,
    32,
    222,
    36,
    37,
    110,
    78,
    99,
    149,
    212,
    95,
    53,
    22,
    161,
    86,
    73,
}
# Städte
T_DEUTSCHESREICH_STADT = {
    150,
    51,
}

# Österreich-Ungarn
T_OESTERREICHUNGARN_LVL0 = {
    71,
}
T_OESTERREICHUNGARN_LVL1 = {
    215,
}
T_OESTERREICHUNGARN_LVL2 = {
    80,
    192,
    23,
    31,
    188,
    137,
    62,
    80,
}
T_OESTERREICHUNGARN_LVL3 = {
    113,
    146,
    112,
    270,
    190,
}
T_OESTERREICHUNGARN_STADT = {
    150,
    273,
    51,
}

# Schweiz
T_SCHWEIZ_LVL0 = {
    50,
}
T_SCHWEIZ_LVL1 = {
    25,
    134,
}

# Luxemburg
T_LUXEMBURG_LVL0 = {
    61,
}
T_LUXEMBURG_LVL1 = {
    170,
    25,
}

# Liechtenstein
T_LIECHTENSTEIN_LVL_0 = {
    60,
}

T_KREISUNDHOEHER = set().union(
    T_DEUTSCHESREICH_LVL0,
    T_DEUTSCHESREICH_LVL1,
    T_DEUTSCHESREICH_LVL2,
    T_DEUTSCHESREICH_LVL3,
    T_DEUTSCHESREICH_LVL4,
    T_OESTERREICHUNGARN_LVL0,
    T_OESTERREICHUNGARN_LVL1,
    T_OESTERREICHUNGARN_LVL2,
    T_OESTERREICHUNGARN_LVL3,
    T_LUXEMBURG_LVL0,
    T_LUXEMBURG_LVL1,
    T_SCHWEIZ_LVL0,
    T_SCHWEIZ_LVL1,
    T_LIECHTENSTEIN_LVL_0,
)

T_STADT = set().union(
    T_DEUTSCHESREICH_STADT,
    T_OESTERREICHUNGARN_STADT,
)

T_GEOGRAPHISCH = {
    47,
    107,
    15,
    89,
    166,
}

T_ZIVIL = {
    242,
    172,
    103,
}

T_GERICHT = {
    3,
    202,
    228,
    19,
    105,
    151,
}

T_VERKEHR = {
    118,
    119,
}

T_SONSTIGE = {
    98,
    195,
    198,
    199,
    200,
    74,
    196,
    147,
    104,
    197,
    187,
}

T_UNDEFINED = {
    276,
    278,
}

T_KIRCHE = {
    124,
    250,
    6,
    91,
    9,
    260,
    11,
    12,
    249,
    96,
    219,
    13,
    245,
    26,
    210,
    92,
    27,
    28,
    29,
    30,
    153,
    35,
    244,
    41,
    42,
    43,
    44,
    243,
    155,
    206,
    253,
    49,
    263,
}

# Undesired are thes groups of GOV types:
# - Kirche
# - geographische Typen
# - Zivilverwaltung
# - Gericht
# - Verkehrswesen
# - Sonstige
# - special cases:
#   * politische Verwaltung: 223 Landgericht (älterer Ordnung)
#   * politische Verwaltung: 10 Departement (Aschaffenburg ist fälschlicherweise als Departement eingetragen)
#   * undefined type: 278 Munizipium
# Desired are therefore these groups of GOV types:
# - politische Verwaltung
# - Wohnplatz
T_UNDESIRED = set().union(
    T_GEOGRAPHISCH,
    T_GERICHT,
    T_VERKEHR,
    T_KIRCHE,
    T_ZIVIL,
    T_SONSTIGE,
    {223,10,278,},
)

T_VERWALTUNG = {
    76,
    57,
    78,
    1,
    2,
    99,
    134,
    251,
    190,
    4,
    192,
    5,
    270,
    110,
    146,
    234,
    7,
    130,
    97,
    135,
    136,
    10,
    217,
    170,
    194,
    203,
    82,
    205,
    140,
    148,
    182,
    14,
    109,
    16,
    221,
    115,
    60,
    18,
    169,
    156,
    274,
    174,
    112,
    165,
    157,
    20,
    246,
    268,
    61,
    189,
    108,
    75,
    79,
    22,
    23,
    183,
    154,
    88,
    214,
    184,
    25,
    227,
    84,
    269,
    81,
    185,
    277,
    113,
    191,
    143,
    32,
    222,
    101,
    95,
    175,
    100,
    33,
    272,
    31,
    34,
    152,
    73,
    256,
    201,
    216,
    211,
    85,
    257,
    223,
    128,
    212,
    36,
    149,
    266,
    80,
    259,
    252,
    264,
    167,
    62,
    145,
    180,
    37,
    207,
    116,
    138,
    38,
    226,
    254,
    164,
    144,
    163,
    247,
    224,
    176,
    45,
    168,
    63,
    46,
    133,
    137,
    125,
    142,
    215,
    173,
    77,
    177,
    93,
    225,
    186,
    56,
    178,
    179,
    188,
    204,
    181,
    48,
    248,
    237,
    267,
    160,
    50,
    71,
    218,
    150,
    273,
    271,
    162,
    52,
    275,
    258,
    255,
    171,
    53,
    213,
    262,
    265,
    126,
    86,
    240,
    58,
    235,
    117,
    83,
    122,
    239,
    161,
    94,
    127,
    114,
    70,
    72,
    131,
    59,
    241,
}
