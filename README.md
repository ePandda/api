# ePANDDA API Documentation

The ePANDDA public API supports HTTP GET requests for data read operations. EPANDDA is a RESTFul web service that returns JSON data objects.
The focus of this API is to correlate data from various providers into a single data set that provides utilities for clustering along
various axes

## Providers
- iDigBio
- PaleoBioDB
- iDigPaleo

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
