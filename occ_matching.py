cript for matching on occurrence data
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

  score = 0

  for pb in pbdb:

    matched_on = []
    
    for spec in idigbio:
      
      idb_match = []
      # match on state
      if pb['coll_data']['state'] is not "" and "dwc:stateProvince" in spec['data']:
        if pb['coll_data']['state'].lower().find(spec['data']['dwc:stateProvince'].lower()) >= 0:
          idb_match.append("State matched: " + pb['coll_data']['state'])
          score = score + 1


      if pb['coll_data']['county'] is not "" and "dwc:county" in spec['data']:
        if pb['coll_data']['county'].lower().find(spec['data']['dwc:county'].lower()) >= 0:
          idb_match.append("State matched: " + pb['coll_data']['county'])
          score = score + 1

      if score > 0:
        matched_on.append({"idb_id": spec['uuid'], "idb_match": idb_match})

    if matched_on:
      matches.append({"occurrence_no": pb['occ_no'], "matches": matched_on})

  return matches
      
