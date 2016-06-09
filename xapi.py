# API Request Dispatch Layer
# Flask microframework driven RESTful API Dispatcher

import json
from flask import Flask, request, Response
app = Flask(__name__)


# Home 
@app.route("/")
def index():
  return "ePANDDA Linked Biodiversity Data Search API!"

# Occurrence / Specimen Matching
@app.route("/api/v1/occurrence", methods=['GET'])
def occurrence():

  # required
  taxon            = request.args.get('taxon')
  taxon_auth       = request.args.get('taxon_auth')

  # optional
  locality         = request.args.get('locality')
  period           = request.args.get('period')
  institution_code = request.args.get('inst_code')

  if taxon and taxon_auth:
    return "Searching for specimen - occurrence matches for taxon: " + taxon + " with authority: " + taxon_auth
  else:
    return "Taxon and Taxon Auth were not supplied"

# Publication / Specimen Matching ( optionally could return associated occurrences )
@app.route("/api/v1/publication", methods=['GET'])
def publication():

  # required
  scientific_name = request.args.get('sciname')
  order           = request.args.get('order')
  journal         = request.args.get('journal')
  article         = request.args.get('article')
  taxon_auth      = request.args.get('taxon_auth')  

  # optional
  author          = request.args.get('author')
  state_prov      = request.args.get('state_province')
  locality        = request.args.get('locality')

  # Either Way this is going to call iDigBio and PBDB ( BHL )  
  if scientific_name or order:
    search_term = scientific_name if scientific_name else order
    matches = matching.matchName( search_term )

    retval = {}
    retval['status']  = "okay"
    retval['results'] = matches

    resp = Response(response=json.dumps(retval), status=200, mimetype="application/json")
    return resp 

  elif journal or article or author:
    return "Searching Publications from publication. Journal: " + journal + " article: " + article
  else:
    return "Required Params Missing!"

# Fossil / Modern specimen matching based on taxonomic heirarchy
@app.route("/api/v1/fossilmodern", methods=['GET'])
def fossilModern():

  # required
  scientific_name = request.args.get('sciname')
  taxon_auth      = request.args.get('taxon_auth')
  
  # optional
  locality        = request.args.get('locality')
  period          = request.args.get('period')

  if scientific_name and taxon_auth:
    return "Fossil/Modern search for " + scientific_name + " using taxon_auth: " + taxon_auth
  else:
    return "Missing Required Params"

# Stratigraphic matching
@app.route("/api/v1/stratigraphy", methods=['GET'])
def stratigraphy():

  # required
  strat      = request.args.get('strat')
  strat_auth = request.args.get('strat_auth')

  if strat and strat_auth:
    return "Stratigraphic search for term: " + strat + " using perferred time scale: " + strat_auth
  else:
    return "Missing Required Params"

# Matching based on person as linking factor
@app.route("/api/v1/person", methods=['GET'])
def person():

  # required
  person          = request.args.get('person')
  scientific_name = request.args.get('sciname')

  if person and scientific_name:
    return "Person search for person: " + person + " associated with sciname: " + scientific_name
  else:
    return "Missing Required Params"

@app.errorhandler(404)
def page_not_found(e):
  return "404 - No PANDDAS Here"

if __name__ == '__main__':
  app.run( debug = True )
