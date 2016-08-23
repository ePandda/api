# ePANDDA API Documentation

The ePANDDA public API supports HTTP GET requests for data read operations. EPANDDA is a RESTFul web service that returns JSON data objects.
The focus of this API is to correlate data from various providers into a single data set that provides utilities for clustering along
various axes

## Providers
- iDigBio
- PaleoBioDB
- iDigPaleo

## API Base URL:
`http://epandda.whirl-i-gig.com/api/v1/`


## Bibliographic Reference and Associated Specimens
Utilizes a fuzzy matching approach to join iDigBio and iDigPaleo specimen data with Paleo Biology Data Base's Bibliographic References.
Where possible Biological Heritage Library's OCR Text API has been used to scan the full article content to provide as many data points as possible to match.
All results are scored based on composite field matching to determine confidence in a given specimen's association to the literature.

* #### URL
  `http://epandda.whirl-i-gig.com/api/v1/publication`

* #### Method
  `GET`

* #### Params

  ##### Required
  `scientific_name | taxon_auth`

  ##### Optional
  `state_prov | locality`

* #### Sample Call:
  `ex: http://epandda.whirl-i-gig.com/api/v1/publication?scientific_name=coleoptera&taxon_auth=gbif`


## Return Object
ePANDDA will return a compact data object with persistent identifiers to original records to allow for data inflation

``` javascript
{ 
  "pbdb_identifiers": ["pid:XXXX"],
  "idigbio_identifiers": ["UUID"],
  "matched_on" : ["field", "field", "field", "field", "field"],
  "annotations": [{ // open annotation if applicable }]
}
```
