import json
from flask import Flask, request, Response
app = Flask(__name__)

@app.route("/")
def index():

  retval = {}
  retval['status'] = "ok"
  retval['v1'] = "http://epandda.whirl-i-gig.com/api/v1/"

  resp = Response(response=json.dumps(retval), status=200, mimetype="application/json")
  return resp

@app.route("/api/v1/occurrence", methods=['GET'])
def occurrence():

  retval = {}

  # required
  taxon_name = request.args.get('taxon_name')
  taxon_auth = request.args.get('taxon_auth')

  if taxon_name and taxon_auth:

    retval['status'] = "ok"
    retval['matches'] = []

    resp = Response(response=json.dumps(retval), status=200, mimetype="application/json")
  else:
  
    retval['status'] = "err"
    retval['msg'] = "Taxon Name and Taxon Authority are required fields"

    resp = Response(response=json.dumps(retval), status=422, mimetype="application/json")

  return resp


@app.route("/api/v1/publication", methods=['GET'])
def publication():

  retval = {}

  # required
  scientific_name = request.args.get('scientific_name')
  if scientific_name:

    retval['status'] = "ok"
    retval['matches'] = []

    resp = Response(response=json.dumps(retval), status=200, mimetype="application/json")
  else:
    retval['status'] = "err"
    retval['msg'] = "Scientific Name is a required field"
    retval['matches'] = []

    resp = Response(response=json.dumps(retval), status=422, mimetype="application/json")

  return resp

@app.route("/api/v1/fossilmodern", methods=['GET'])
def fossilModern():

  retval = {}

  #required
  scientific_name = request.args.get('scientific_name')
  taxon_auth      = request.args.get('taxon_auth')

  if scientific_name and taxon_auth:

    retval['status'] = "ok"
    retval['matches'] = []

    resp = Response(response=json.dumps(retval), status=200, mimetype="application/json")
  else:

    retval['status'] = "err"
    retval['msg'] = "Scientific Name and Taxon Authority are required fields"

    resp = Response(response=json.dumps(retval), status=422, mimetype="application/json")

  return resp

@app.route("/api/v1/stratigraphy", methods=['GET'])
def stratigraphy():

  retval = {}

  # required
  strat_layer = request.args.get('strat_layer')
  strat_auth  = request.args.get('strat_auth')

  if strat_layer and strat_auth:

    retval['status'] = "ok"
    retval['matches'] = []

    resp = Response(response=json.dumps(retval), status=200, mimetype="application/json")
  else:

    retval['status'] = "err"
    retval['msg'] = "Stratigraphic Layer and Stratigraphic Authority are required fields"

    resp = Response(response=json.dumps(retval), status=422, mimetype="application/json")

  return resp

@app.errorhandler(404)
def page_not_found(e):
  
  retval = {}
  retval['status'] = "error"
  retval['msg'] = "The request could not be completed"

  resp = Response(response=json.dumps(retval), status=404, mimetype="application/json")
  return resp

if __name__ == '__main__':
    app.run()
