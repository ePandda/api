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

  print "matching started ..."
  matches = []

  for pb in pbdb:

    pb['member'] = []
    pb['formation'] = []
    pb['localities'] = []
    pb['collectors'] = []

    print "Parsing coll_info for [" + pb['pid'] + "]"
    for coll_info in pb['coll_info']:
      print coll_info 

      # condense state into one state list
      if coll_info['state'].lower() not in pb['states'] and coll_info['state'] is not "":
        pb['states'].append( coll_info['state'].lower() )

      # condense member into one member list
      if coll_info['member'].lower() not in pb['member'] and coll_info['member'] is not "":
        pb['member'].append( coll_info['member'].lower() )
      
      # condense formation into one list
      if coll_info['formation'].lower() not in pb['formation'] and coll_info['formation'] is not "":
        pb['formation'].append( coll_info['formation'].lower() )

      # condense locality into one list
      if coll_info['collection_name'].lower() not in pb['localities'] and coll_info['collection_name'] is not "":
        pb['localities'].append( coll_info['collection_name'].lower() )

      if coll_info['collection_aka'].lower() not in pb['localities'] and coll_info['collection_aka'] is not "":
        pb['localities'].append( coll_info['collection_aka'].lower() )

      # condense collectors into one list
      if coll_info['collectors'].lower() not in pb['collectors'] and coll_info['collectors'] is not "":
        pb['collectors'].append( coll_info['collectors'].lower() )

    for specimen in idigbio:

      score = 0;
      matched_on = []

      if "dwc:scientificNameAuthorship" in specimen['data']:
        # Check if Author, Collector name matches

        if specimen['data']['dwc:scientificNameAuthorship'].lower().find( pb['author'].lower() ) >= 0:
          print "== == == Author matched SciNameAuth == == =="

          score = score + 1
          matched_on.append("PBDB:author == dwc:scientificNameAuthorship")

      if "dwc:identificationRemarks" in specimen['data']:
        # Check for People      

        if specimen['data']['dwc:identificationRemarks'].lower().find( pb['author'].lower() ) >= 0:
          print "== == == Author matched Ident Remarks == == =="
 
          score = score + 1
          matched_on.append("PBDB:author == dwc:identificationRemarks")

      if "dcterms:bibliographicCitation" in specimen['data']:
        # Check if author, article title, journal title exists in here ( genus species )
    
        if specimen['data']['dcterms:bibliographicCitation'].lower().find( pb['author'].lower() ) >= 0:
          print "== == == Author matched BibCit == == =="

          score = score + 1
          matched_on.append("PBDB:author == dcterms:bibliographicCitation")

        if specimen['data']['dcterms:bibliographicCitation'].lower().find( pb['title'].lower() ) >= 0:
          print "== == == Title matched BibCit == == =="

          score = score + 1
          matched_on.append("PBDB:title == dcterms:bibliographicCitation")

        if specimen['data']['dcterms:bibliographicCitation'].lower().find( pb['pubtitle'].lower() ) >= 0:
          print "== == == Pubtitle matched BibCit == == =="

          score = score + 1
          matched_on.append("PBDB:pubtitle == dcterms:bibliographicCitation")

      if "dwc:associatedReferences" in specimen['data']:
        # Author Name, Article, Pub title, volume, issue

        if specimen['data']['dwc:associatedReferences'].lower().find( pb['author'].lower() ) >= 0:
          print "== == == Author foudn in dwc:associatedReferences == == =="

          score = score + 1
          matched_on.append("PBDB:author == dwc:associatedReferences")

        # TODO Tweak to allow lev distance +/- 5
        if specimen['data']['dwc:associatedReferences'].lower().find( pb['title'].lower() ) >= 0:
          print "== == == Article title found in Associated Refs == == =="

          score = score + 1
          matched_on.append("PBDB:title == dwc:associatedReferences")

        if specimen['data']['dwc:associatedReferences'].lower().find( pb['pubtitle'].lower() ) >= 0:
          print "== == == Pub title found Assoc Refs == == =="

          score = score + 1
          matched_on.append("PBDB:pubtitle == dwc:associatedReferences")

      if "dwc:occurrenceRemarks" in specimen['data']:
        # Taxon Name, Locality, State, County,  Stratigraphic Identifier?

        for locality in pb['localities']:
          if specimen['data']['dwc:occurrenceRemarks'].lower().find( locality.lower() ) >= 0:
            print "== == == PB Locality found in OccRem == == =="

            score = score + 1
            matched_on.append("PBDB:locality == dwc:occurrenceRemarks")

        for state in pb['states']:
          if specimen['data']['dwc:occurrenceRemarks'].lower().find( state ) >= 0:
            print "== == == PB State found in OccRem == == =="

            score = score + 1
            matched_on.append("PBDB:states == dwc:occurrenceRemarks") 

        for member in pb['member']:
          if specimen['data']['dwc:occurrenceRemarks'].lower().find( member ) >= 0:
            print "== == == PB member foun in OccRem == == ==" 
          
            score = score + 1
            matched_on.append("PBDB:member == dwc:occurrenceRemarks")

        for form in pb['formation']:
          if specimen['data']['dwc:occurrenceRemarks'].lower().find( form ) >= 0:
            print "== == == PB formation found in OccRem == == =="
 
            score = score + 1
            matched_on.append("PBDB:formation == dwc:occurrenceRemarks")

      if "dwc:identificationReferences" in specimen['data']:
        # People,

        if pb['author'].lower() == specimen['data']['dwc:identificationReference'].lower():
          print "== == == Author matched IdentRef == == =="

          score = score + 1
          matched_on.append("PBDB:author == dwc:identificationReference")

      if "dwc:recordedBy" in specimen['data']:
        # People.

        if pb['author'].lower() == specimen['data']['dwc:recordedBy'].lower():
          print "== == == Author Matched recordedBy == == =="
 
          score = score + 1
          matched_on.append("PBDB:author == dwc:recordedBy")

      if "dwc:identifiedBy" in specimen['data']:
        # People

        if specimen['data']['dwc:identifiedBy'].lower().find( pb['author'].lower() ) >= 0:
          print "== == == Author matched identBy == == =="

          score = score + 1
          matched_on.append("PBDB:author == dwc:identifiedBy")

      if "dwc:formation" in specimen['data']:
      
        if pb['title'].lower().find( specimen['data']['dwc:formation'].lower() ) >= 0:
          print "== == == Formation found in Title == == =="

          score = score + 1
          matched_on.append("PBDB:title == dwc:formation")

      #if "dwc:eventDate" in specimen:
        # Collection Date

      #if "dwc:dateIdentified" in specimen:
        # Occurence Date

      if "dwc:scientificName" in specimen['data']:
        # should match classification path 
      
        for path in pb['classification_path']:
          if path.lower().find( specimen['data']['dwc:scientificName'].lower() ) >= 0:
            print "== == == Classification Path matched scientificName == == =="

            score = score + 1
            matched_on.append("PBDB:Classification Path == dwc:scientificName")

      # TODO: dedupe classification path
      #if "dwc:order" in specimen['data']:
        # should match classification path, sci_names

      #  for path in pb['classification_path']:
      #    if path.lower().find( specimen['data']['dwc:order'].lower() ) >= 0:
      #      print "== == == Classification Path matched order == == =="

      #      score = score + 1
      #      matched_on.append("PBDB:Classification Path == dwc:order")

      if "dwc:stateProvince" in specimen['data']:
        # should match collection info

        for state in pb['states']:
          if state == specimen['data']['dwc:stateProvince'].lower():
            print "== == == State Matched == == =="

            score = score + 1
            matched_on.append("PBDB:state == dwc:stateProvince")
 

      if "dwc:locality" in specimen['data']:
        # should match collection info

        if pb['title'].lower().find( specimen['data']['dwc:locality'].lower() ) >= 0:
          print "== == == dwc:locality found in title == == =="

          score = score + 1
          matched_on.append("PBDB:title == dwc:locality")

        for locality in pb['localities']:
          if locality.lower().find( specimen['data']['dwc:locality'].lower() ) >= 0:
            print "== == == Locality matched dwc:locality == == =="

            score = score + 1
            matched_on.append("PBDB:localities == dwc:locality")

      
      if score > 1:
        matches.append({"pbdb_id": pb['pid'], "idig_id": specimen['uuid'], "score": score, "matched_on": '[%s]' % ', '.join(map(str, matched_on)) })

  # Sort matches by descending score  
  sorted_matches = sorted(matches, key=lambda match: match['score'], reverse=True)
  return sorted_matches
