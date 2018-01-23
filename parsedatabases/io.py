import numpy as np
import os
import pandas as pd
from xml.etree.cElementTree import iterparse
import logging

logger = logging.getLogger('parse_database')

def mf_from_inchi(inchi):
    return inchi.split('/')[1]

class MolecularDatabase():
    def __init__(self, filename):
        self.database = {}
        self._required_fields = ['name', 'mf', 'inchi']
        self.parse_database(filename)
        self.assert_required_fields()

    def parse_database(self, filename):
        raise NotImplementedError('should be subclassed')

    def assert_required_fields(self):
        for entry in self.database:
            for key in self._required_fields:
                assert key in self.database[entry]

    def write(self, filename_out, header=True, sep='\t'):
        db = pd.DataFrame(self.database).T[self._required_fields]
        db = db.loc[db.mf.notnull()]
        db.to_csv(filename_out, sep=sep, index=True, index_label= "id", header=header)


class Sdf(MolecularDatabase):
    def __init__(self, filename, id_field, name_field):
        self.id_field = id_field
        self.name_field = name_field
        super().__init__(filename)


    def parse_sdf(self, sdf_str):
        key = 'struct'
        val = []
        sdf = {}
        for line in sdf_str.split("\n"):
            if line.startswith('>'):
                sdf[key.replace('<', "").replace(">", "").strip().lower()] = " ".join(val).strip()
                key = line
                val = []
            else:
                val.append(line)
        if 'inchi' in sdf:
            sdf['formula'] = mf_from_inchi(sdf['inchi'])
        else:
            sdf['formula'] = ""
        return sdf

    def parse_database(self, filename):
        with open(filename) as f:
            sdf_str = ''
            for line in f.readlines():
                if '$$$$' in line: #end of molecule
                    try:
                        sdf = self.parse_sdf(sdf_str)
                        self.database[sdf[self.id_field]] = sdf
                    except:
                        print(sdf_str)
                        raise
                    sdf_str = ''
                else:
                    sdf_str+=line
        df = pd.DataFrame(self.database).T[[self.name_field, 'formula', 'inchi']]
        df.columns = ['name', 'mf', 'inchi']
        self.database = df.T.to_dict()


class HmdbXml(MolecularDatabase):
    def __init__(self, filename):
        super().__init__(filename)

    def tagwithns(self, ns, tag):
        return  "{}{}".format("{"+ns[1]+"}", tag)


    def parse_database(self, filename):
        events = ("end", "start-ns", "end-ns")
        namespaces = []
        for event, elem in iterparse(filename, events=events):
            if event == "start-ns":
                namespaces.insert(0, elem)
                metabolite_tag  = self.tagwithns(namespaces[0], "metabolite")
            elif event == "end-ns":
                namespaces.pop(0)
            else:
                if elem.tag == metabolite_tag:
                    accession, formatted_metabolite = self.process_metabolite(namespaces[0], elem)
                    self.database[accession] = formatted_metabolite
                    elem.clear()

    def process_metabolite(self, ns, elem):
        metabolite = {}
        for child in elem:
            if child.tag == self.tagwithns(ns, "name"):
                metabolite['name'] = child.text
            elif child.tag == self.tagwithns(ns, "inchi"):
                metabolite['inchi'] = child.text
            elif child.tag == self.tagwithns(ns, "chemical_formula"):
                metabolite['mf'] = child.text
            elif child.tag == self.tagwithns(ns, "accession"):
                accession = child.text
            child.clear()
        return accession, metabolite


class SwissLipidsCsv(MolecularDatabase):
    def __init__(self, filename):
        super().__init__(filename)

    def parse_database(self, filename):
        df = pd.read_csv(filename, sep='\t', index_col=False).fillna("")
        df = df.loc[df['Level'] == 'Isomeric subspecies']
        df = df.set_index("Lipid ID")[['Name', "InChI (pH7.3)"]]
        df.columns = ['name', 'inchi']
        logger.warning("missing inchi for {}".format(df.index[df.inchi == ""].values))
        df = df.loc[~(df.inchi == "")]
        df['mf'] = df.inchi.apply(mf_from_inchi)


        self.database = df.T.to_dict()

class Pamdb(MolecularDatabase):

    def __init__(self, filename):
        super().__init__(filename)

    def parse_database(self, filename):
        cols = ['Name', 'InChI']
        df = pd.read_excel(filename, sheet='Sheet1')
        df = df.set_index('MetID')[cols]
        df.columns = ['name', 'inchi']
        logger.warning("missing inchi for {}".format(df.index[df.inchi == ""].values))
        df = df.loc[~(df.inchi == "")]
        df['mf'] = df['inchi'].apply(mf_from_inchi)
        self.database = df.T.to_dict()

class LipidMaps(MolecularDatabase):
    def __init__(self, folder):
        super().__init__(folder)

    def parse_database_file(self, filename):
        sdf = Sdf(filename, "lm_id", "common_name")
        return sdf.database

    def parse_database(self, folder):
        files = [f for f in os.listdir(folder) if f.startswith('LMSD')]
        for file in files:
            self.database.update(self.parse_database_file(os.path.join(folder, file)))


class Metlin(MolecularDatabase):
    def __init__(self, filename):
        super().__init__(filename)

    def parse_database(self, filename):
        import json
        with open(filename) as f:
            db =[json.loads(line.strip().strip("[]").strip(",")) for line in f]
        db = pd.DataFrame(db)
        db = db.set_index("molid")[["name", "inchi_file"]]
        db.columns = ["name", "inchi"]
        logger.warning("missing inchi for {}".format(db.index[db.inchi == ""].values))
        db = db.loc[~(db.inchi == "")]
        db["mf"] = db['inchi'].apply(mf_from_inchi)
        self.database = db.T.to_dict()
