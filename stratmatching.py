# any imports we need
import annotation

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

def match(idigbio, pbdb):

  print "matching started ..."

  matches = []

  for pb in pbdb:

    for specimen in idigbio:

      print "going through specimens ... "

      score = 0
      matched_on = []
      
      print "checking if strat colls"

      for sc in pb['strat_colls']:

        if 'member' not in sc:
          sc['member'] = ''

        print "Process Strat Coll Info here ..... "
        print " -- --- --- \n"
        print sc
        print " -- --- ---- -- ---- --- ---"

        if "dwc:formation" in specimen['data']:
          if specimen['data']['dwc:formation'].lower().find( sc['formation'].lower() ) >= 0:
            if "PBDB:formation == dwc:formation" not in matched_on:
              score = score + 1
              matched_on.append("PBDB:formation == dwc:formation")
         
        if "dwc:member" in specimen['data']:
          if specimen['data']['dwc:member'].lower().find( sc['member'].lower() ) >= 0:
            if "PBDB:member == dwc:member" not in matched_on:
              score = score + 1
              matched_on.append("PBDB:member == dwc:member")

        if "dwc:county" in specimen['data']:
          if specimen['data']['dwc:county'].lower().find( sc['county'].lower() ) >= 0:
            if "PBDB:county == dwc:county" not in matched_on:
              score = score + 1
              matched_on.append("PBDB:county == dwc:county")

        if "dwc:stateProvince" in specimen['data']:
          if specimen['data']['dwc:stateProvince'].lower().find( sc['state'].lower() ) >= 0:
            if "PBDB:state/province == dwc:stateProvince" not in matched_on:
              score = score + 1
              matched_on.append("PBDB:state/province == dwc:stateProvince")

        if "dwc:locality" in specimen['data']:
          if specimen['data']['dwc:locality'].lower().find( sc['collection_name'].lower() ) >= 0:
            if "PBDB:collection_name == dwc:locality" not in matched_on:
              score = score + 1
              matched_on.append("PBDB:collection_name == dwc:locality")

          if specimen['data']['dwc:locality'].lower().find( sc['collection_aka'].lower() ) >= 0:
            if "PBDB:collection_aka == dwc:locality" not in matched_on:
              score = score + 1
              matched_on.append("PBDB:collection_aka == dwc:locality")
      
      if "dwc:scientificName" in specimen['data']:
        for gn in pb['taxon_item']['genus']:

          if specimen['data']['dwc:scientificName'].lower().find( gn.lower() ) >= 0:
            score = score + 1
            matched_on.append("PBDB:genus_name == dwc:scientificName")

      if "dwc:Identification" in specimen['data']:
        for ident in specimen['data']['dwc:Identification']:
        
          for gn in pb['taxon_item']['genus']:
          
            if ident['dwc:scientificName'].lower().find( gn.lower() ) >= 0:
              score = score + 1
              matched_on.append("PBDB:genus_name == dwc:Identification -> dwc:scientificName")

          for sn in pb['taxon_item']['species']:
 
            if ident['dwc:scientificName'].lower().find( sn.lower() ) >= 0:
              score = score + 1
              matched_on.append("PBDB:species_name == dwc:Identification -> dwc:scientificName")
      
      print "done Ident"

      if score > 1:
        matches.append({
          "pbdb_coll_id": map('https://paleobiodb.org/data1.2/colls/single.json?show=loc,stratext&id={0}'.format, pb['taxon_item']['coll_no']),
          "pbdb_occ_id": map('https://paleobiodb.org/data1.2/occs/single.json?show=loc&id={0}'.format, pb['taxon_item']['occ_no']),
          "pbdb_ref_id": 'https://paleobiodb.org/data1.2/refs/single.json?show=both&id=' + pb['taxon_item']['ref_no'],
          "idig_id": 'http://search.idigbio.org/v2/view/records/' + specimen['uuid'],
          "score": score,
          "matched_on": '[%s]' % ',\n'.join(map(str, matched_on)) })

  print str(len(matches)) + " matches returned"
  # Sort matches by descending score  
  sorted_matches = sorted(matches, key=lambda match: match['score'], reverse=True)
  return sorted_matches
