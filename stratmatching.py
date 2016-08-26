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

def match(idigbio, pbdb):

  print "matching started ..."
  matches = []

  for pb in pbdb:

    for specimen in idigbio:

      score = 0;
      matched_on = []
      pb['genus_names'] = []
      pb['species_names'] = []

      if 'occurrences' in pb:
        for occ in pb['occurrences']:
      
          if occ['genus'].lower() not in pb['genus_names'] and occ['genus'] is not "":
            pb['genus_names'].append( occ['genus'].lower() )

          if occ['species'].lower() not in pb['genus_names'] and occ['species'] is not "":
            pb['species_names'].append( occ['species'].lower() )

      print "condense occurrence data done .. "

      if "dwc:formation" in specimen['data']:

       if specimen['data']['dwc:formation'].lower().find( pb['formation'].lower() ) >= 0:
         score = score + 1
         matched_on.append("PBDB:formation == dwc:formation")

      print "done formation"

      if "dwc:country" in specimen['data']:
 
        print "IDB country: " + specimen['data']['dwc:country']
        print "pbdb country: " + pb['country']

        if specimen['data']['dwc:country'].lower().find( pb['country'].lower() ) >= 0:
          score = score + 1
          matched_on.append("PBDB:country == dwc:country")      

      print "done country"

      if "dwc:stateProvince" in specimen['data']:
        if specimen['data']['dwc:stateProvince'].lower().find( pb['state'].lower() ) >= 0:
          score = score + 1
          matched_on.append("PBDB:state == dwc:stateProvince")

      if "dwc:scientificName" in specimen['data']:
        for gn in pb['genus_names']:

          if specimen['data']['dwc:scientificName'].lower().find( gn.lower() ) >= 0:
            score = score + 1
            matched_on.append("PBDB:genus_name == dwc:scientificName")

      print "done sci name"

      if "dwc:Identification" in specimen['data']:
        for ident in specimen['data']['dwc:Identification']:
        
          for gn in pb['genus_names']:
          
            if ident['dwc:scientificName'].lower().find( gn.lower() ) >= 0:
              score = score + 1
              matched_on.append("PBDB:genus_name == dwc:Identification -> dwc:scientificName")

          for sn in pb['species_names']:
 
            if ident['dwc:scientificName'].lower().find( sn.lower() ) >= 0:
              score = score + 1
              matched_on.append("PBDB:species_name == dwc:Identification -> dwc:scientificName")
      
      print "done Ident"

      print "Score: " + str(score)
      if score > 1:
        matches.append({"pbdb_id": pb['collection_no'], "idig_id": specimen['uuid'], "score": score, "matched_on": '[%s]' % ', '.join(map(str, matched_on)) })

  # Sort matches by descending score  
  sorted_matches = sorted(matches, key=lambda match: match['score'], reverse=True)
  return sorted_matches