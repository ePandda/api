import json
import requests
import collections
import pubmatching
import stratmatching
from pymongo import MongoClient
from flask import Flask, request, Response
app = Flask(__name__)

config = json.load(open('./config.json'))

#mongoDB Setup
client = MongoClient(config['mongo_url'])
db = client.test

@app.route("/")
def index():

  resp = (("status", "ok"),
          ("v1", "http://epandda.whirl-i-gig.com/api/v1/"))
  resp = collections.OrderedDict(resp)

  return Response(response=json.dumps(resp), status=200, mimetype="application/json")
  

@app.route("/api/v1/")
def base():

  resp = (("status", "ok"),
          ("msg", "this should link to epandda documentation page / inform user they've hit the base endpoint"))

  resp = collections.OrderedDict(resp)

  return Response(response=json.dumps(resp), status=200, mimetype="application/json")

@app.route("/api/v1/occurrence", methods=['GET'])
def occurrence():

  retval = {}

  # required
  taxon_name = request.args.get('taxon_name')
  taxon_auth = request.args.get('taxon_auth')

  # optional
  locality         = request.args.get('locality')
  period           = request.args.get('period')
  institution_code = request.args.get('institution_code')

  if taxon_name and taxon_auth:

    sciname_param = '"scientificname": "' + taxon_name + '"'

    # TODO: this needs more thought, what if order, kingdom, phylum is entered?
    # split sciname into genus and species if it contains a space
    genus_param   = ""
    species_param = ""
    if " " in taxon_name:
      sciname_array = taxon_name.split(" ")
      genus_param   = sciname_array[0]
      species_param = sciname_array[1]

    print "genus: " + genus_param
    print "species: " + species_param

    # Required params met, check what optional terms we have
    loc = ""
    if locality is not None and len(locality) > 0:
      loc = ', "locality": "' + str(locality) + '"'

    period_param = ""
    if period is not None and len(period) > 0:
      period_param = ', "period": "' + str(period) + '"'

    inst_param = ""
    if institution_code is not None and len(institution_code) > 0:
      inst_param = ', "institution_code": "' + str(institution_code) + '"'

    print "Sci Name: " + taxon_name
    print "URL: " + config['idigbio_base'] + '{' + sciname_param + loc + period_param + inst_param + '}&limit=250'

    # Get iDigBio Records
    idigbio = requests.get(config['idigbio_base'] + '{' + sciname_param + '}&limit=250')
    if 200 == idigbio.status_code:
      idigbio_json = json.loads( idigbio.content )

    # Get pbdb occurrence fields
    matches_on_occ = []
    #if species_param is not None:
    #  occ_match = db.pbdb_occurrences.find({ '$or': [{'genus_name': genus_param}, {'species_name': species_param}]})
    #else:
    #  occ_match = db.pbdb_refs.find({'genus_name': genus_param})

    occ_match = db.pbdb_occurrences.find({ '$or': [{ 'genus_name': { '$regex': taxon_name, '$options': 'i' }},
                                                   { 'species_name': { '$regex': taxon_name, '$options': 'i'}}]})


    for om in occ_match:

      matches_on_coll = []
      coll_match = db.pbdb_colls.find({'collection_no': om['collection_no']})

      for cm in coll_match:
        matches_on_coll.append({
          "collection_name": cm['collection_name'],
          "collection_no": cm['collection_no'],
          "country": cm['country'],
          "state": cm['state'],
          "county": cm['county'],
          "formation": cm['formation'],
          "member": cm['member'],
          "lat": cm['lat'],
          "lng": cm['lng'],
          "period_max": cm['period_max'],
          "period_min": cm['period_min']})

      matches_on_occ.append({
        "occ_no": om['occurrence_no'],
        "coll_no": om['collection_no'],
        "ref_no": om['reference_no'],
        "genus_name": om['genus_name'],
		"species_name": om['species_name'],
		"comments": om['comments'],
		"abund_unit": om['abund_unit'],
        "abund_value": om['abund_value'],
        "coll_data": matches_on_coll})

    matches = occ_matching.occurrenceMatch(matches_on_occ, idigbio_json['items'])

    resp = (("status", "okay"),
            ("matches", matches),
            ("pbdb_occ", matches_on_occ),
            ("idigbio_occ", idigbio_json['items']))
    resp = collections.OrderedDict(resp)

    return Response(response=json.dumps(resp), status=200, mimetype="application/json")
  else:
  
    resp = (("status", "err"),
            ("msg", "Taxon Name and Taxon Authority are required fields"))

    resp = collections.OrderedDict(resp)

    return Response(response=json.dumps(resp), status=422, mimetype="application/json")


@app.route("/api/v1/publication", methods=['GET'])
def publication():

  print "Publication Handler"

  # required
  scientific_name = request.args.get('scientific_name')
  taxon_auth      = request.args.get('taxon_auth')

  # optional
  order      = request.args.get('order')
  journal    = request.args.get('journal')
  article    = request.args.get('article')
  author     = request.args.get('author')
  state_prov = request.args.get('state_province')
  county     = request.args.get('county')
  locality   = request.args.get('locality')

  if scientific_name and taxon_auth:

    # TODO: Revisit IDB python module - it didn't return results correctly // I abandonded for a reason I don't remember now.

    # required params met, check what optional terms we have?

    # TODO: conditional for when to use order / when sci_name
    sciname_param = '"scientificname": "' + scientific_name + '"'
    sciname_param = '"order": "' + scientific_name + '"'

    stateprov = ""
    if state_prov is not None and len(state_prov) > 0:
      stateprov = ', "stateprovince": "' + str(state_prov) + '"'

    countyparam = ""
    if county is not None and len(county) > 0:
      countyparam = ', "county": "' + str(county) + '"'

    # assume genus species if scientific_name has a space, otherwise it's higher up the tree? 

    print "Sci Name: " + scientific_name
    print "URL: " + config['idigbio_base'] + '{' + sciname_param + stateprov + countyparam + '}&limit=250'

    # Get iDigBio Records
    idigbio = requests.get(config['idigbio_base'] + '{' + sciname_param + stateprov + countyparam + '}&limit=250')
    if 200 == idigbio.status_code:
      idigbio_json = json.loads( idigbio.content )

    # check if scientific_name exists in classification path:
    matches_by_class = []
    if state_prov is not None:
      class_match = db.pbdb_refs.find({ '$and': [{'classification_path': { '$regex': scientific_name }}, { 'states': { '$eq': state_prov}}] })
    else:
      class_match = db.pbdb_refs.find({'classification_path': { '$regex': scientific_name }})    

    for cm in class_match:

      # Lookup collection information
      coll_info = []
      coll_data = db.pbdb_colls.find({'reference_no': cm['pid']})
      for cd in coll_data:

        coll_info.append({
          "collection_no": cd['collection_no'], 
          "paleolng": cd['paleolng'], 
          "paleolat": cd['paleolat'], 
          "collectors": cd['collectors'], 
          "collection_name": cd['collection_name'],
          "collection_aka": cd['collection_aka'],
          "formation": cd['formation'],
          "member": cd['member'],
          "lat": cd['lat'], 
          "lng": cd['lng'], 
          "state": cd['state'],
          "country": cd['country']})

      matches_by_class.append({
          "pid": cm['pid'], 
          "title": cm['title'], 
          "pubtitle": cm['pubtitle'], 
          "author": cm['author1'], 
          "classification_path": cm['classification_path'],
          "states": cm['states'],
          "doi": cm['doi'],
          "coll_info": coll_info})
    

    # TODO: Append to matches by class if PID not present
    #additional = db.pbdb_refs.find({'title': { '$regex': scientific_name}})
    #for add in additional:
    #  print add


    # Send off matches_by_class and idigbio_json['items'] for term matching
    matches = pubmatching.matchPubFields(matches_by_class, idigbio_json['items'])

    resp = (("status", "ok"),
            ("query_term", scientific_name),
            ("taxon_authority", taxon_auth),
            ("matches", matches),
            ("pbdb_matches", matches_by_class),
            ("idigbio_matches", idigbio_json['items']))

    resp = collections.OrderedDict(resp)
    return Response(response=json.dumps(resp), status=200, mimetype="application/json")
  else:

    resp = (("status", "err"),
            ("msg", "Scientific Name and Taxon Authority are required fields"))

    resp = collections.OrderedDict(resp)
    return Response(response=json.dumps(resp), status=422, mimetype="application/json")

@app.route("/api/v1/fossilmodern", methods=['GET'])
def fossilModern():
  # required
  scientific_name = request.args.get('scientific_name')
  taxon_auth      = request.args.get('taxon_auth')

  # optional
  locality = request.args.get('locality')
  period   = request.args.get('period')

  if scientific_name and taxon_auth:

    resp = (("status", "ok"),
            ("matches", []))

    resp = collections.OrderedDict(resp)
    return Response(response=json.dumps(resp), status=200, mimetype="application/json")
  else:

    resp = (("status", "err"),
            ("msg", "Scientific Name and Taxon Authority are required fields"))

    resp = collections.OrderedDict(resp)
    return Response(response=json.dumps(resp), status=422, mimetype="application/json")

@app.route("/api/v1/stratigraphy", methods=['GET'])
def stratigraphy():

  # required
  strat_layer = request.args.get('strat_layer')
  taxon_name  = request.args.get('taxon_name')
  #strat_auth  = request.args.get('strat_auth')

  # optional
  state_prov = request.args.get('state_province')
  county     = request.args.get('county')
  locality   = request.args.get('locality')

  #if strat_layer and strat_auth:
  if strat_layer and taxon_name:

    strat_param = '"earliestperiodorlowestsystem":"' + strat_layer + '","latestperiodorhighestsystem":"' + strat_layer + '"'        
    taxon_param = ', "scientificname": "' + taxon_name + '"'

    stateprov = ""
    if state_prov is not None and len(state_prov) > 0:
      stateprov = ', "stateprovince": "' + str(state_prov) + '"'

    countyparam = ""
    if county is not None and len(county) > 0:
      countyparam = ', "county": "' + str(county) + '"'


    # Get classification path to pull relevant pbdb records.

    print "we looked for: " + taxon_name

    pb_results = []
    lookup_results = db.pbdb_taxon_lookup.find({ "classification_path": { "$regex": taxon_name, "$options": 'i' }}).limit(10)

    print "after look through coll_by_taxon"

    for lp in lookup_results:

      print lp
      for coll_no in lp['coll_no']:

        print "checking for collections for: " + coll_no
        coll_by_taxon = db.pbdb_colls.find({ "$and": [
         {"collection_no": coll_no},
         {"$or":[
           {"period_max": {"$regex": strat_layer,"$options":'i'}},
           {"period_min": {"$regex": strat_layer,"$options":'i'}}
         ]}
        ]})


        for coll in coll_by_taxon:

          coll_occs = []
          pb_occs = db.pbdb_occurrences.find({ "collection_no": coll['collection_no']}).limit(10)
          for oc in pb_occs:
    
           occs = []
           occs.append({
             "occurrence_no": oc['occurrence_no'],
             "reference_no": oc['reference_no'],
             "genus": oc['genus_name'],
             "species": oc['species_name'],
             "comments": oc['comments'],
             "abundance": oc['abund_value'] + ' ' + oc['abund_unit']
           })

          # TODO: Pull in References for classification lookup?

          pb_results.append({
           "paleolng": coll['paleolng'],
           "paleolat": coll['paleolat'],
           "period_min": coll['period_min'],
           "period_max": coll['period_max'],
           "collectors": coll['collectors'],
           "collection_no": coll['collection_no'],
           "country": coll['country'],
           "state": coll['state'],
           "member": coll['member'],
           "formation": coll['formation'],
           "lat": coll['lat'],
           "lng": coll['lng'],
           "collection_name": coll['collection_name'],
           "occurrences": occs 
          })

    print "Now get idigbio results"

    idigbio = requests.get(config['idigbio_base'] + '{' + strat_param + taxon_param + '}&limit=250')
    if 200 == idigbio.status_code:
        idigbio_json = json.loads(idigbio.content)

    # Send of to be matched
    matches = stratmatching.match(idigbio_json['items'], pb_results) 

    resp = (("status", "ok"),
            ("query_term", strat_layer),
            ("matches", matches),
            ("pbdb_matches", pb_results),
            ("idigbio_matches", idigbio_json['items']))
   
    resp = collections.OrderedDict(resp)
    return Response(response=json.dumps(resp), status=200, mimetype="application/json")

  else:

    resp = (("status", "err"),
            ("msg", "Stratigraphic Layer and Stratigraphic Authority are required fields"))

    resp = collections.OrderedDict(resp)
    return Response(response=json.dumps(resp), status=422, mimetype="application/json")

@app.errorhandler(404)
def page_not_found(e):
  
  resp = (("status", "err"),
          ("msg", "The request could not be completed"))

  resp = collections.OrderedDict(resp)
  return Response(response=json.dumps(resp), status=404, mimetype="application/json")

if __name__ == '__main__':
    app.run()
