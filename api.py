import json
import requests
import collections
import pubmatching
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
    
    # split sciname into genus and species if it contains a space
    if " " in sciname_param:
      sciname_array = sciname_param.split(" ")
      genus_param = sciname_array[0]
      species_param = sciname_array[1]

    # Required params met, check what optional terms we have
    loc = ""
    if locality is not None and len(locality) > 0:
      loc = ', "locality": "' + str(locality) + '"'

    period_param = ""
    if period is not None and len(period) > 0:
      period_param = ', "period": "' + str(period) + '"'

    inst_param = ""
    if institution_code is not None and len(institution_code) > 0:
      inst_param = ', "instution_code": "' + str(institution_code) + '"'

    print "Sci Name: " + scientific_name
    print "URL: " + config['idigbio_base'] + '{' + sciname_param + loc + period_param + inst_param + '}&limit=250'

    # Get iDigBio Records
    idigbio = requests.get(config['idigbio_base'] + '{' + sciname_param + loc + period_param + inst_param + '}&limit=250')
    if 200 == idigbio.status_code:
      idigbio_json = json.loads( idigbio.content )

    # Get pbdb occurrence fields
    matches_on_occ = []
    if species_param is not None:
      occ_match = db.pbdb_occurrences.find({ '$or': [{'genus_name': genus_param}, {'species_name': species_param}]})
    else:
      occ_match = db.pbdb_refs.find({'genus_name': genus_param})
    for om in occ_match:
      matches_on_occ.append({"occ_no": om['occurrence_no'],
			     "genus_name": om['genus_name'],
			     "species_name": om['species_name'],
			     "comments": om['comments'],
			     "abund_units": om['abund_units'],
			     "abund_value": om['abund_value']})

    resp = (("status", "okay"),
            ("matches", []),
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

        coll_info.append({"collection_no": cd['collection_no'], 
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

      matches_by_class.append({"pid": cm['pid'], 
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
  strat_auth  = request.args.get('strat_auth')

  # optional
  # TODO: Determine optional fields of interest for stratigraphic queries

  if strat_layer and strat_auth:

    resp = (("status", "ok"),
            ("matches", []))
   
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
