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
  print "searching for " + sciname + "located in " + state_prov

  inflated = []
  sciname_lookup = db.pbdb_taxon_lookup.find({'$and': [{'classification_path': { '$regex': sciname, '$options': 'i'}},
                                                       {'states': { '$regex': state_prov, '$options': 'i'}}]}, {'_id': 0})
  for tm in sciname_lookup:

    # inflate references
    ref_result = {}
    pb_ref = db.pbdb_refs.find({'pid': tm['ref_no']}, {'_id': 0})
    for ref in pb_ref:
      ref_result = ref

    # inflate collections
    ref_colls = []
    for cn in tm['coll_no']:
      pb_colls = db.pbdb_colls.find({ '$and': [{'collection_no': cn }, {'state': { '$regex': state_prov, '$options': 'i'}}]}, {'_id': 0})
      for pc in pb_colls:
        ref_colls.append(pc)

    # inflate occurrences
    ref_occs = []
    for on in tm['occ_no']:
      pb_occs = db.pbdb_occs.find({'occurrence_no': on }, {'_id': 0})
      for po in pb_occs:
        ref_occs.append(po)

    inflated.append({"ref": ref_result, "collections": ref_colls, "occurrences": ref_occs, "classification_path": tm['classification_path']})

  return inflated

def lookupByFormation( sciname, state_prov, formation ):
  print "in lookupByStratLayer"
  print "Searching for a " + str(sciname) + " in " + str(state_prov) + " from the " + str(formation)
  
  inflated = []
  if state_prov:
    state_prov = state_prov.lower()
    sciname_lookup = db.pbdb_taxon_lookup.find({'$and': [{'classification_path': { '$regex': sciname, '$options': 'i'}},
                                                         {'states': { '$regex': state_prov, '$options': 'i'}}]}, {'_id': 0})

  else:
    sciname_lookup = db.pbdb_taxon_lookup.find({'classification_path': { '$regex': sciname, '$options': 'i'}}, {'_id': 0})

  lookup_count = sciname_lookup.count()

  print "Lookup returned: " + str(lookup_count) + " results"
  print "taxon_lookup finished"

  for item in sciname_lookup:

    if "states" not in item:
      item['states'] = []

    strat_colls = []
    for coll_no in item['coll_no']:
      coll_by_taxon = db.pbdb_colls.find({"$and": [
        {"collection_no": coll_no},
        {"formation": formation}
      ]}, {'_id': 0})

      for coll in coll_by_taxon:

        if state_prov is not None:
          if coll['state'].lower() == state_prov:
            strat_colls.append(coll)
        else:
          strat_colls.append(coll)
          

    inflated.append({"strat_colls": strat_colls, "taxon_item": item})

  return inflated

def lookupByRefNo(ref_no):

  refno_lookup = db.pbdb_taxon_lookup.find({"ref_no": ref_no}, {'_id': 0})
  return refno_lookup


def lookupByCollNo(coll_no):

  collno_lookup = db.pbdb_taxon_lookup.find({"coll_no": { '$eq': coll_no}}, {'_id': 0})
  return collno_lookup


def lookupByOccNo(occ_no):

  occno_lookup = db.pbdb_taxon_lookup.find({"occ_no": { '$eq': occ_no}}, {'_id': 0})
  return occno_lookup


def lookupByGenus(genus_name):

  genus_lookup = db.pbdb_taxon_lookup.find({"genus": { '$eq': genus_name}}, {'_id': 0})
  return genus_lookup


def lookupBySpecies(species_name):

  species_lookup = db.pbdb_taxon_lookup.find({"species": { '$eq': species_name}}, {'_id': 0})
  return species_lookup
