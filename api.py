import json
import requests
import collections
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

    resp = (("status", "okay"),
            ("matches", []))
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
  locality   = request.args.get('locality')

  if scientific_name and taxon_auth:

    # required parms met, check what optional terms we have?

    # assume genus species if scientific_name has a space, otherwise it's higher up the tree? 

    print "Sci Name: " + scientific_name

    # Get iDigBio Records
    idigbio = requests.get('https://search.idigbio.org/v2/search/records/?rq={"scientificname":"' + scientific_name + '"}')
    if 200 == idigbio.status_code:
      idigbio_json = json.loads( idigbio.content )

      #print idigbio_json

    # check if scientific_name exists in classification path:
    matches_by_class = []
    class_match = db.pbdb_refs.find({'classification_path': { '$regex': scientific_name }})
    for cm in class_match:

      print "looking up coll info for PID: " + cm['pid']
      # Lookup collection information
      coll_info = []
      coll_data = db.pbdb_colls.find({'reference_no': cm['pid']})
      for cd in coll_data:
        print "found coll data match: "
        #print cd

        coll_info.append({"collection_no": cd['collection_no'], 
                          "paleolng": cd['paleolng'], 
                          "paleolat": cd['paleolat'], 
                          "collectors": cd['collectors'], 
                          "collection_name": cd['collection_name'],
                          "formation": cd['formation'],
                          "lat": cd['lat'], 
                          "lng": cd['lng'], 
                          "state": cd['state']})

      matches_by_class.append({"pid": cm['pid'], "title": cm['title'], "pubtitle": cm['pubtitle'], "author": cm['author1'], "coll_info": coll_info})
    
    resp = (("status", "ok"),
            ("query_term", scientific_name),
            ("taxon_authority", taxon_auth),
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
