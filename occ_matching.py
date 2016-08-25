# Script for matching on occurrence data
# initially matching on:
# lat/lng
# county
# state
# formation
# 
# 
# other fields to come
# currently not importing anything

def occurrenceMatch(pbdb, idigbio):

  print "matching started ..."
  matches = []

  for pb in pbdb:

    matched_on = []
    
    for spec in idigbio:
      score = 0 
      idb_match = []
      # match on state
      if pb['coll_data']['state'] is not "":
        if pb['coll_data']['state'].lower() == spec['data']['dwc:stateProvince'].lower():
          idb_match.append("State matched")
          score = score + 1

      if pb['coll_data']['county'] is not "":
        if pb['coll_data']['county'].lower() == spec['data']['dwc:county'].lower():
          idb_match.append("County matched")
          score = score + 1

      if score > 0:
        matched_on.append({"idb_id": spec['uuid'], "idb_match": idb_match, "score": score})

    if matched_on:
      matches.append({"occurrence_no": pb['occ_no'], "idb_specimens": matched_on})

  return matches
      
