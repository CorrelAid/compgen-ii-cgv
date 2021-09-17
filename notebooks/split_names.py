from compgen2 import Pipeline

data_root = "../data"
p = Pipeline(data_root)

vl = p.read_vl()

sorted(vl[vl.location.str.contains("-")].location)

sorted(vl[vl.location.str.contains(" - ")].location)


