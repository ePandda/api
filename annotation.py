# ePANDDA Open Annotation Implementation
#
# @author: Jon Lauters
#
# Simple function to fascilitate construction of annotations for ePANDDA and iDigBio Consumption

import json
import time
import datetime
import uuid

def create(target, body):

  print "in create annotation"

  # Timestamp and annotation uuid
  anno_uuid = uuid.uuid4()
  datestamp = datetime.datetime.fromtimestamp( time.time() ).strftime('%Y-%m-%d %H:%M:%S %Z')

  target_uuid = str(target['uuid'])

  # TODO: Check if body has doi
  # TODO: Allow for body to pass in annotator?
  # TODO: Determine if we need to also push this into a mongoDB? Maybe a flag on the constructor?

  open_annotation = {}
  open_annotation['@context'] = ["https://www.w3.org/ns/oa.jsonld", {"dwc": "http://rs.tdwg.org/dwc/terms/"}] 
  open_annotation['@id'] = "https://epandda.org/annotations/" + str(anno_uuid)
  open_annotation['@type'] = "oa:Annotation"
  open_annotation['annotatedAt'] = str(datestamp)
  open_annotation['annotatedBy'] = {
    "@id": "http://grab.by/PuPq", 
    "@type": "foaf:Project",
    "mbox": { "@id": "mailto:annotation@epandda.org" },
    "name": "ePANDDA Annotation Bot"
  }

  # check for None/Nulls
  title = ''
  if body['ref']['title'] is not None:
    title = body['ref']['title']

  doi = ''
  if body['ref']['doi'] is not None:
    doi = body['ref']['doi']

  open_annotation['hasBody'] = {
    "! cnt:chars": "{\"dwc:occurrenceRemarks\": " + title + "}",
    "@id": "https://epannda.org/annotation_body/" + doi,
    "@type": ["dwc:Occurrence", "cnt:ContentAsText"],
    "dc:format": "application/json"
  }

  open_annotation['hasTarget'] = {
    "@id": "urn:uuid:" + target_uuid,
    "@type": "oa:SpecificResource",
    "hasSource": { "@id" : "http://search.idigbio.org/v2/view/records/" + target_uuid }
  }

  return open_annotation
