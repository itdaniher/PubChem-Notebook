#!/usr/bin/python
# Ian Daniher - 2012.06.01
# Beerware

import gzip
import json
import urllib
import io
import sys
# get ChEBI database from the European Bioinformatics Institute

sdfFullText = gzip.open(sys.argv[1]).read()
#virtualsdfgz = io.BytesIO(urllib.urlopen("ftp://ftp.ebi.ac.uk/pub/databases/chebi/SDF/ChEBI_complete.sdf.gz").read())
#sdfFullText = gzip.GzipFile(fileobj=virtualsdfgz, mode="rb").read()

## start parsing SDF

# split string by "$$$$", the SD file segmenter
sdfFullText = sdfFullText.split("$$$$")

# normalize Molfile data to match formatting for the rest of the file
sdfFullText = ["\n> <Molfile>\n"+item for item in sdfFullText]

# subsegment by looking for "\n> <tag>"
sdfFullText = [item.split("\n> <") for item in sdfFullText]

# clean up subsegments
stripNewlines = lambda inList: [ item.strip("\n") for item in inList ]
sdfFullText = map(stripNewlines, sdfFullText)

# split subsegments into key-value pairs
listToTuples = lambda inList: [ string.split('>\n') for string in inList ]
sdfFullText = map(listToTuples, sdfFullText)

# trim off first (garbage/empty) object
sdfFullText = [item[1:-1] for item in sdfFullText]

# split the values into lists by newline
tupleSplitter = lambda inList: dict([ (item[0], item[1].split('\n')) if item[0] != "Molfile" else item for item in inList])
sdfFullText = map(tupleSplitter, sdfFullText)

#keys = ["PUBCHEM_"+x for x in "TOTAL_CHARGE IUPAC_INCHI MOLECULAR_FORMULA OPENEYE_ISO_SMILES COMPOUND_CID MOLECULAR_WEIGHT".split()]
keys = ['PUBCHEM_IUPAC_INCHI', 'PUBCHEM_COMPOUND_CID', 'PUBCHEM_OPENEYE_ISO_SMILES', 'PUBCHEM_MOLECULAR_FORMULA', 'PUBCHEM_TOTAL_CHARGE', 'PUBCHEM_EXACT_MASS', 'PUBCHEM_IUPAC_NAME']

def cleanup(obj):
        res = {}
        for key in obj.keys():
            if key in keys:
                if key == "PUBCHEM_EXACT_MASS":
                    res[key] = float(obj[key][0])
                elif key in ["PUBCHEM_TOTAL_CHARGE", "PUBCHEM_COMPOUND_CID"]:
                    res[key] = int(obj[key][0])
                else:
                    res[key] = obj[key][0]
        if 'PUBCHEM_IUPAC_NAME' in [x for x in obj.keys()]:
            res['PUBCHEM_IUPAC_NAME'] = '||'.join(list(set([y[0] for (x,y) in obj.items() if 'NAME' in x])))
        if len([x for x in res.items()]) != len(keys):
            return None
        return res

gzip.open(sys.argv[1].replace('sdf', 'json'), 'w').write('\n'.join([json.dumps(x) for x in [cleanup(x) for x in sdfFullText] if x != None]))
