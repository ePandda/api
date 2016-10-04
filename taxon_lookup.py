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

def lookupByFormation( sciname, state_prov, formation ):
  print "in lookupByStratLayer"
  print "Searching for a " + str(sciname) + " in " + str(state_prov) + " from the " + str(formation)
  
  inflated = []
  if state_prov:
    state_prov = state_prov.lower()
    sciname_lookup = db.pbdb_taxon_lookup.find({'$and': [{'classification_path': { '$regex': sciname, '$options': 'i'}},
                                                         {'states': { '$regex': state_prov, '$options': 'i'}}]})

  else:
    sciname_lookup = db.pbdb_taxon_lookup.find({'classification_path': { '$regex': sciname, '$options': 'i'}})

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
      ]})

      for coll in coll_by_taxon:

        print item['ref_no'] + "coll object"
        print coll

        if state_prov is not None:
          if coll['state'].lower() == state_prov:

            strat_colls.append({
              "paleolng": coll['paleolng'],
              "period_min": coll['period_min'],
              "paleolat": coll['paleolat'],
              "collectors": coll['collectors'],
              "collection_aka": coll['collection_aka'],
              "collection_no": coll['collection_no'],
              "country": coll['country'],
              "reference_no": coll['reference_no'],
              "county": coll['county'],
              "state": coll['state'],
              "memeber": coll['member'],
              "formation": coll['formation'],
              "collection_name": coll['collection_name'],
              "lat": coll['lat'],
              "lng": coll['lng'],
              "period_max": coll['period_max']
            })

        else:

          strat_colls.append({
            "paleolng": coll['paleolng'],
            "period_min": coll['period_min'],
            "paleolat": coll['paleolat'],
            "collectors": coll['collectors'],
            "collection_aka": coll['collection_aka'],
            "collection_no": coll['collection_no'],
            "country": coll['country'],
            "reference_no": coll['reference_no'],
            "county": coll['county'],
            "state": coll['state'],
            "memeber": coll['member'],
            "formation": coll['formation'],
            "collection_name": coll['collection_name'],
            "lat": coll['lat'],
            "lng": coll['lng'],
            "period_max": coll['period_max']
          })

    inflated.append({"strat_colls": strat_colls, 
                       "taxon_item": {
                         "classification_path": item['classification_path'],
                         "coll_no": item['coll_no'],
                         "occ_no": item['occ_no'],
                         "ref_no": item['ref_no'],
                         "genus": item['genus'],
                         "species": item['species'],
                         "states": item['states']
                       }
    })

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
