import json
import requests
import collections
import pubmatching
import stratmatching
import occ_matching
import taxon_lookup
from pymongo import MongoClient
from flask import Flask, request, Response
app = Flask(__name__)
app.debug = True
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
    sciname_param = '"scientificname": "' + scientific_name + '"'
    #sciname_param = '"order": "' + scientific_name + '"'

    stateprov = ""
    if state_prov is not None and len(state_prov) > 0:
      stateprov = ', "stateprovince": "' + str(state_prov) + '"'

    countyparam = ""
    if county is not None and len(county) > 0:
      countyparam = ', "county": "' + str(county) + '"'

    # Think about this part more ....
    # assume genus species if scientific_name has a space, otherwise it's higher up the tree? 

    print "Sci Name: " + scientific_name
    print "URL: " + config['idigbio_base'] + '{' + sciname_param + stateprov + countyparam + '}&limit=250'

    # Get iDigBio Records
    idigbio = requests.get(config['idigbio_base'] + '{' + sciname_param + stateprov + countyparam + '}&limit=250')
    if 200 == idigbio.status_code:
      idigbio_json = json.loads( idigbio.content )

    # taxon_lookup
    pbdb_items = taxon_lookup.lookupBySciName( scientific_name, state_prov )

    # Send off matches_by_class and idigbio_json['items'] for term matching
    matches = pubmatching.matchPubFields(pbdb_items, idigbio_json['items'])

    print "gutcheck matches .. "
    print "match count: " + str(len(matches))

    # TODO: Shrink return object, or figure out how to send massive amount of data back?
    resp = (("status", "ok"),
            ("query_term", scientific_name),
            ("taxon_authority", taxon_auth),
            ("matches", matches),
            ("pbdb_matches", pbdb_items), 
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
  taxon_name  = request.args.get('taxon_name')
  formation   = request.args.get('formation')

  # optional
  state_prov = request.args.get('state_province')
  county     = request.args.get('county')
  locality   = request.args.get('locality')

  if formation and taxon_name:

    #strat_param = '"earliestperiodorlowestsystem":"' + strat_layer + '","latestperiodorhighestsystem":"' + strat_layer + '"'        
    formation_param = '"formation":"' + formation + '"'
    taxon_param = ', "scientificname": "' + taxon_name + '"'

    stateprov = ""
    if state_prov is not None and len(state_prov) > 0:
      stateprov = ', "stateprovince": "' + str(state_prov) + '"'

    countyparam = ""
    if county is not None and len(county) > 0:
      countyparam = ', "county": "' + str(county) + '"'


    # Get classification path to pull relevant pbdb records.

    print "we looked for: " + taxon_name

    idigbio_items = []
    idigbio = requests.get(config['idigbio_base'] + '{' + formation_param + taxon_param + stateprov + '}&limit=250')
    if 200 == idigbio.status_code:
        idigbio_json = json.loads(idigbio.content)

        if 'items' in idigbio_json:
          idigbio_items = idigbio_json['items']

    pb_results = []
    pb_results = taxon_lookup.lookupByFormation( taxon_name, state_prov, formation )

    matches = []
    if idigbio_items and pb_results:
      # Send of to be matched
      matches = stratmatching.match(idigbio_items, pb_results) 

    pbdb_return = []
    for pb in pb_results:
      if pb['strat_colls']:
        pbdb_return.append({"ref_id": pb['taxon_item']['ref_no'], "strat_data": pb['strat_colls']})

    resp = (("status", "ok"),
            ("query_term", formation),
            ("matches", matches),
            ("pbdb_matches", pbdb_return),
            ("idigbio_matches", idigbio_items))
   
    resp = collections.OrderedDict(resp)
    return Response(response=json.dumps(resp), status=200, mimetype="application/json")

  else:

    resp = (("status", "err"),
            ("msg", "Formation and Taxon Name are required fields"))

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
