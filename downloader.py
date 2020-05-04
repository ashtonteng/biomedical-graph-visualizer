from SPARQLWrapper import SPARQLWrapper, JSON
import time

endpoint = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
wd = "PREFIX wd: <http://www.wikidata.org/entity/>"
wdt = "PREFIX wdt: <http://www.wikidata.org/prop/direct/>"


def query(query):
    endpoint.setQuery(query)
    endpoint.setReturnFormat(JSON)
    result = None
    while result is None:
        try:
            result = endpoint.query().convert()
        except:
            print("HTTP Timeout! Sleeping...")
            time.sleep(5)
    return result

    def get_query_for_gene():
        q = """SELECT ?gene ?geneLabel ?association ?associationLabel ?protein ?proteinLabel ?chromosome ?chromosomeLabel ?substitution ?substitutionLabel ?strand ?strandLabel WHERE {
        ?gene (wdt:P279|wdt:P31) wd:Q7187;
                wdt:P703 wd:Q15978631.
        
        OPTIONAL {?gene wdt:P2293 ?association.}
        OPTIONAL {?gene wdt:P688 ?protein.}
        OPTIONAL {?gene wdt:P1057 ?chromosome.}
        OPTIONAL {?gene wdt:P2548 ?strand.}
        OPTIONAL {?gene wdt:P1916 ?substitution.}
        
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        }"""
        return q
