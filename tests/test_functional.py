from parsedatabases.io import HmdbXml, Sdf, SwissLipidsCsv, Pamdb, LipidMaps, Metlin

def test_hmdb_xml():
    fn = "tests/data/test_data.xml"
    db = HmdbXml(fn)
    assert len(db.database) == 5
    db.write("tests/data/test_write.tsv")
    with open("tests/data/test_write.tsv") as f:
        line = f.readline()
    assert line =="id\tname\tmf\tinchi\n"


def test_pamdb():
    fn = "tests/data/test_data_pamet.xlsx"
    db = Pamdb(fn)
    assert(len(db.database)) == 9
    db.write("tests/data/test_write.tsv")
    with open("tests/data/test_write.tsv") as f:
        line = f.readline()
    assert line == "id\tname\tmf\tinchi\n"

def test_chebi_sdf():
    fn = "tests/data/test_chebi.sdf"
    db = Sdf(fn, "chebi id", "chebi name")
    assert (len(db.database)) == 4
    db.write("tests/data/test_write.tsv")
    with open("tests/data/test_write.tsv") as f:
        line = f.readline()
    assert line == "id\tname\tmf\tinchi\n"

def test_swisslipids():
    fn = "tests/data/test_swisslipids.csv"
    db = SwissLipidsCsv(fn)
    assert (len(db.database)) == 16
    db.write("tests/data/test_write.tsv")
    with open("tests/data/test_write.tsv") as f:
        line = f.readline()
    assert line == "id\tname\tmf\tinchi\n"

def test_lipidmaps():
    fn = "tests/data/test_lipidmaps"
    db = LipidMaps(fn)
    assert (len(db.database)) == 10
    db.write("tests/data/test_write.tsv")
    with open("tests/data/test_write.tsv") as f:
        line = f.readline()
    assert line == "id\tname\tmf\tinchi\n"

def test_metlin():
    fn = "tests/data/test_metlin.json"
    db = Metlin(fn)
    assert (len(db.database)) == 9
    db.write("tests/data/test_write.tsv")
    with open("tests/data/test_write.tsv") as f:
        line = f.readline()
    assert line == "id\tname\tmf\tinchi\n"