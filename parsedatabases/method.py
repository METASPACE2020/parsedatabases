from parsedatabases.io import HmdbXml, Sdf, SwissLipidsCsv, Pamdb, LipidMaps, Metlin
import argparse
import logging

def lipid_maps():
    return None

def metlin():
    return None

def hmdb(fn_in, fn_out):
    db = HmdbXml(fn_in)
    db.write(fn_out)

def swisslipids(fn_in, fn_out):
    db = SwissLipidsCsv(fn_in)
    db.write(fn_out)

def pamdb(fn_in, fn_out):
    db = Pamdb(fn_in)
    db.write(fn_out)

def chebi(fn_in, fn_out):
    db = Sdf(fn_in)
    db.write(fn_out)

def lipidmaps(fn_in, fn_out):
    db = LipidMaps(fn_in)
    db.write(fn_out)

def metlin(fn_in, fn_out):
    db = Metlin(fn_in)
    db.write(fn_out)

if __name__ == "__main__":
    # execute only if run as a script
    parser = argparse.ArgumentParser(description='Export a database.')
    parser.add_argument('fn_in', type=str,
                        help='input database filename')
    parser.add_argument('fn_out', type=str,
                        help='destination (METASPACE formatted) database filename')
    parser.add_argument('dbase', type=str,
                        help='tell me which database you are processing [lipid_maps, hmdb, swisslipids, metlin]')
    args = parser.parse_args()
    logger = logging.getLogger("parse_database")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(args.fn_out + ".log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    globals()[args.dbase](args.fn_in, args.fn_out)