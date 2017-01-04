# Flask Test Suite Skeleton
import os
import json
import unittest

from api import app


class FlaskTestCase(unittest.TestCase):

  def setUp(self):
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    self.app = app.test_client()


  def tearDown(self):
    app.config['TESTING'] = False
    self.app = None

  # ---------------------------------------
  # ePANDDA API Endpoint Tests
  # ---------------------------------------
  
  # make sure our base url just returns something
  def test_base_url(self):
    rv = self.app.get('/')
    assert rv.data != ''
  
  def test_api_v1(self):
    rv = self.app.get('/api/v1')
    assert rv.data != ''

  # Check fail on no required params
  def test_occurences_no_required(self):
    rv = self.app.get('/api/v1/occurrence')
    retobj = json.loads(rv.data) 

    assert retobj['status'] == 'err'
    assert retobj['msg'] != ''

  # Occurences ( Required Params: Taxon Name, Taxon Auth )
  def test_occurrences(self):
    test_taxon_name = 'coleoptera'
    test_taxon_auth = 'gbif'
    test_limit = '10'
    rv = self.app.get('/api/v1/occurrence?taxon_name='+ test_taxon_name + '&taxon_auth=' + test_taxon_auth + '&limit=' + test_limit)
    retobj = json.loads(rv.data)

    assert retobj['status'] == 'ok'
    assert isinstance(retobj['matches'], list) == True
    assert isinstance(retobj['pbdb_occ'], list) == True
    assert isinstance(retobj['idigbio_occ'], list) == True

  # Publications - Required Params fail check
  def test_publications_no_required(self):
    rv = self.app.get('/api/v1/publication')
    retobj = json.loads(rv.data)

    assert retobj['status'] == 'err'
    assert retobj['msg'] != ''

  # Publications - Success Check
  def test_publications(self):
    test_scientific_name = 'coleoptera'
    test_limit = '10'

    rv = self.app.get('/api/v1/publication?scientific_name=' + test_scientific_name + '&limit=' + test_limit)
    retobj = json.loads(rv.data)

    assert retobj['status'] == 'ok'
    assert isinstance(retobj['matches'], list) == True
    assert isinstance(retobj['pbdb_matches'], list) == True
    assert isinstance(retobj['idigbio_matches'], list) == True 

  # FossilModern - Required Params fail check
  def test_fossilmodern_no_required(self):
    rv = self.app.get('/api/v1/fossilmodern')
    retobj = json.loads(rv.data)

    assert retobj['status'] == 'err'
    assert retobj['msg'] != ''

  # FossilModern - Success Check
  def test_fossilmodern(self):
    test_scientific_name = 'coleoptera'
    test_taxon_auth = 'gbif'
    test_limit = '10'

    rv = self.app.get('/api/v1/fossilmodern?scientific_name=' + test_scientific_name + '&taxon_auth=' + test_taxon_auth + 
      '&limit=' + test_limit)
    retobj = json.loads(rv.data)

    assert retobj['status'] == 'ok'
    assert isinstance(retobj['matches'], list) == True 

  # Stratigraphy - Required Params fail check
  def test_stratigraphy_no_required(self):
    rv = self.app.get('/api/v1/stratigraphy')
    retobj = json.loads(rv.data)

    assert retobj['status'] == 'err'
    assert retobj['msg'] != ''

  # Stratigraphy - Success Check
  def test_stratigraphy(self):
    test_taxon_name = 'coleoptera'
    test_formation = 'wellington'
    test_limit = '10'

    rv = self.app.get('/api/v1/stratigraphy?taxon_name=' + test_taxon_name + '&formation=' + test_formation + '&limit=' + test_limit)
    retobj = json.loads(rv.data)

    assert retobj['status'] == 'ok'
    assert isinstance(retobj['matches'], list) == True
    assert isinstance(retobj['pbdb_matches'], list) == True
    assert isinstance(retobj['idigbio_matches'], list) == True

if __name__ == '__main__':
  unittest.main()
