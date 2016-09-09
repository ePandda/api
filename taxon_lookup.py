import json
from pymongo import MongoClient

config = json.load(open('./config.json'))

# mongoDB setup
client = MongoClient(config['mongo_url'])
db = client.test

# Taxon Lookup Module
#

def lookupBySciName(sciname, state_prov):

  print "in lookup BySciName"
  print "searching for " + sciname

  print "located in " + state_prov

  inflated = []
  sciname_lookup = db.pbdb_taxon_lookup.find({'$and': [{'classification_path': { '$regex': sciname, '$options': 'i'}},
                                                       {'states': { '$regex': state_prov, '$options': 'i'}}]})
  for tm in sciname_lookup:


    print "tm result.... "
    print tm

    print "Checking for reference for ref_no: " + tm['ref_no']

    # get references
    pb_ref = db.pbdb_refs.find({'pid': tm['ref_no']})

    ref_result = {}
    print "ref search returned .... "
    for ref in pb_ref:
      ref_result = ref


    print "Ref Result: "
    print ref_result

    ref_colls = []
    for cn in tm['coll_no']:
      print "checking collections for coll_no: " + cn
      pb_colls = db.pbdb_colls.find({'collection_no': cn })
      for pc in pb_colls:
        print "adding pc to list"
        print pc
        ref_colls.append(pc)

    ref_occs = []
    for on in tm['occ_no']:
      print "checking occurrences for occ_no: " + on
      pb_occs = db.pbdb_occs.find({'occurrence_no': on })
      for po in pb_occs:
        ref_occs.append(po)

    inflated.append({"ref": ref_result, "collections": ref_colls, "occurrences": ref_occs, "classification_path": tm['classification_path']})

  return inflated


def lookupByRefNo(ref_no):

  refno_lookup = db.pbdb_taxon_lookup.find({"ref_no": ref_no})
  return refno_lookup


def lookupByCollNo(coll_no):

  collno_lookup = db.pbdb_taxon_lookup.find({"coll_no": { '$eq': coll_no}})
  return collno_lookup


def lookupByOccNo(occ_no):

  occno_lookup = db.pbdb_taxon_lookup.find({"occ_no": { '$eq': occ_no}})
  return occno_lookup


def lookupByGenus(genus_name):

  genus_lookup = db.pbdb_taxon_lookup.find({"genus": { '$eq': genus_name}})
  return genus_lookup


def lookupBySpecies(species_name):

  species_lookup = db.pbdb_taxon_lookup.find({"species": { '$eq': species_name}})
  return species_lookup
