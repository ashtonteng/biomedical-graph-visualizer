# This file provides templates for sparql queries

def query_template_taxon(concept, property):
  query = "SELECT ?concept ?conceptLabel ?peripheralConcept ?peripheralConceptLabel WHERE { " + \
          f"?concept (wdt:P279|wdt:P31) wd:{concept}; " + \
                  "wdt:P703 wd:Q15978631; " + \
                  f"wdt:{property} ?peripheralConcept. " + \
          '''SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". } ''' + \
          "}"
  return query

def query_template_no_taxon(concept, property):
 query = "SELECT ?concept ?conceptLabel ?peripheralConcept ?peripheralConceptLabel WHERE { " + \
        f"?concept (wdt:P279|wdt:P31) wd:{concept}; " + \
                f"wdt:{property} ?peripheralConcept. " + \
        '''SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". } ''' + \
        "}"
 return query

def query_template_wildcard(concept, property):
 query = "SELECT ?concept ?conceptLabel ?peripheralConcept ?peripheralConceptLabel WHERE { " + \
        f"?concept (wdt:P279|wdt:P31)* wd:{concept}; " + \
                f"wdt:{property} ?peripheralConcept. " + \
        '''SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". } ''' + \
        "}"
 return query