# Script for matching on occurrence data
# initially matching on:
# lat/lng
# county
# state
# formation
# period
# 
# other fields to come
# import geopy for calculating coordinate difference
from geopy.distance import vincenty

def occurrenceMatch(pbdb, idigbio):

  print "matching started ..."
  matches = []

  for pb in pbdb:

    matched_on = []
    
    for spec in idigbio:
      score = 0 
      idb_match = []
      pbdb_formation = []
      
      for cd in pb['coll_data']:
        
        # match on formation
        if cd['formation']:
          pbdb_formation.append(cd['formation'])
          
        if cd['collection_name']:
          pbdb_formation.append(cd['collection_name'])
        
        if pbdb_formation:
          for form in pbdb_formation:  	
            if "dwc:formation" in spec['data']:
              if spec['data']['dwc:formation'].lower().find( form.lower() ) >= 0:
                idb_match.append("Formation matched: " + form)
                score = score + 1
      
        # match on state
        if cd['state'] is not "" and "dwc:stateProvince" in spec['data']:
          if cd['state'].lower() == spec['data']['dwc:stateProvince'].lower():
            idb_match.append("State matched: " + cd['state'])
            score = score + 1
            
        # match on county
        if cd['county'] is not "" and "dwc:county" in spec['data']:
          if cd['county'].lower() == spec['data']['dwc:county'].lower():
            idb_match.append("County matched: " + cd['county'])
            score = score + 1
            
        # match on lat/lng
        if cd['lat'] is not "" and cd['lng'] is not "":
          pbdb_geo = (cd['lat'], cd['lng'])
          
        if "geopoint" in spec['indexTerms']:
          idb_geo = (spec['indexTerms']['geopoint']['lat'], spec['indexTerms']['geopoint']['lon'])
        
        if idb_geo and pbdb_geo:
          spatial_distance = vincenty(pbdb_geo, idb_geo).miles
          if spatial_distance < 25:
            idb_match.append("Lat-Lng matched: " + str(spatial_distance))
            score = score + 1
		
		# match on period
        if cd['period_min'] and cd['period_max']:
		  if cd['period_min'].lower() == cd['period_max'].lower():
		    pbdb_period = cd['period_max'].lower()
		  else:
		    pbdb_period_list = (cd['period_min'].lower(), cd['period_max'].lower())
        elif cd['period_min']:
		  pbdb_period = cd['period_min'].lower()
        elif cd['period_max']:
          pbdb_period = cd['period_max'].lower()   

        if "dwc:latestPeriodOrHighestSystem" in spec['data'] and "dwc:earliestPeriodOrLowestSystem" in spec['data']:
		  if spec['data']['dwc:latestPeriodOrHighestSystem'].lower() == spec['data']['dwc:earliestPeriodOrLowestSystem'].lower():
		    idb_period = spec['data']['dwc:latestPeriodOrHighestSystem'].lower()
		  else:
		    idb_period_list = (spec['data']['dwc:latestPeriodOrHighestSystem'].lower(), spec['data']['dwc:earliestPeriodOrLowestSystem'].lower())
        elif "dwc:latestPeriodOrHighestSystem" in spec['data']:
		  idb_period = spec['data']['dwc:latestPeriodOrHighestSystem'].lower()
        elif "dwc:earliestPeriodOrLowestSystem" in spec['data']:
		  idb_period = spec['data']['dwc:earliestPeriodOrLowestSystem'].lower()
		  
        if pbdb_period and idb_period:
          if pbdb_period == idb_period:
            idb_match.append("Period matched: " + pbdb_period)
            score = score + 1
        elif pbdb_period and idb_period_list:
          for ip in idb_period_list:
            if pbdb_period.find( ip ) >= 0:
              idb_match.append("Period matched: " + pbdb_period)
              score = score + 1
        elif idb_period and pbdb_period_list:
          for ip in pbdb_period_list:
            if idb_period.find( ip ) >= 0:
              idb_match.append("Period matched: " + idb_period)
              score = score + 1
        elif pbdb_period_list and idb_period_list:
          for ip in idb_period_list:
            for pbp in pbdb_period_list:
              if ip == pbp:
                idb_match.append("Period matched: " + ip)
                score = score + 1      
              
      if score > 1:
        matched_on.append({"idb_id": spec['uuid'], "idb_match": idb_match, "score": score})

    if matched_on:
      matches.append({"occurrence_no": pb['occ_no'], "idb_specimens": matched_on})

  return matches
      
