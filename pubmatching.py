# any imports we need
#
# lev distance
# utls for normalized strings


# method to take publication results from api matching
# 
# match on:
# People ( collector, author name, identified by )
# Locality / Collection Name, collection aka, Locality is often in title
# Geo Coords if available
# City
# State
# County
# Country

def matchPubFields(pbdb, idigbio):

  matches = []

  for pb in pbdb:

    for specimen in idigbio:

      if "dwc:scientificNameAuthorship" in specimen:
        # Check if Author, Collector name matches

        # TODO: converto to lev distance threshold
        if pb['author'].lower() == specimen['dwc:scientificNameAuthorship'].lower():
          print "== == == Author matched == == =="
 

      if "dwc:identificationRemarks" in specimen:
        # Check for People      

        if pb['author'].lower() == specimen['dwc:identificationRemarks']:
          print "== == == Author matched Ident Remarks == == =="

      if "dcterms:bibliographicCitation" in specimen:
        # Check if author, article title, journal title exists in here
    
        if pb['author'].lower() == specimen['dcterms:bibliographicCitation'].lower():
          print "== == == Author matched BibCit == == =="

        if pb['title'].lower() == specimen['dcterms:bibliographicCitation'].lower():
          print "== == == Title matched BibCit == == =="

        if pb['pubtitle'].lower() == specimen['dcterms:bibliographicCitation'].lower():
          print "== == == Pubtitle matched BibCit == == =="

      #if "dwc:occurrenceRemarks" in specimen:
        # Taxon Name, Locality, Stratigraphic Identifier?

      if "dwc:identificationReferences" in specimen:
        # People,

        if pb['author'].lower() == specimen['dwc:identificationReference'].lower():
          print "== == == Author matched IdentRef == == =="

      if "dwc:recordedBy" in specimen:
        # People.

        if pb['author'].lower() == specimen['dwc:recordedBy'].lower():
          print "== == == Author Matched recordedBy == == =="
 
      if "dwc:identifiedBy" in specimen:
        # People

        if pb['author'].lower() == specimen['dwc:identifiedBy'].lower():
          print "== == == Author matched identBy == == =="

      #if "dwc:eventDate" in specimen:
        # Collection Date

      #if "dwc:dateIdentified" in specimen:
        # Occurence Date

      #if "dwc:scientificName" in specimen:
        # should match classification path 

      #if "dwc:order" in specimen:
        # should match classification path

      if "dwc:stateProvince" in specimen:
        # should match collection info

        for state in pb['states']:
          if state == specimen['dwc:stateProvince'].lower():
            print "== == == State Matched == == =="

      #if "dwc:locality" in specimen:
        # should match collection info

      #if "dwc:formation" in specimen:
        # should match collection info

  return matches
