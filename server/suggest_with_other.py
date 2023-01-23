import json
import requests
import hashlib
import subprocess
from suggest_engine import Suggestion


class ATM_MeSH_Suggestion(Suggestion):
    def __init__(self, params):
        super().__init__(params)
        self.url = self.config['url']
        self.key = self.config['key']

    def suggest(self):
        terms = self.payload['Keywords']
        result = []
        for term in terms:
            mesh_for_single_term = {
                "Keywords": [term],
                "type": "ATM",
                "MeSH_Terms": {}
            }
            url = f'{self.url}?db=pubmed&api_key={self.key}&retmode=json&term={term}'
            response = requests.get(url)
            content = json.loads(response.content)
            print(content)
            translation_stack = content["esearchresult"]["translationset"]
            if len(translation_stack)==0:
                continue
            for item in translation_stack:
                translated_terms = item['to'].split("OR")
                for t in translated_terms:
                    t = t.strip()
                    if t.endswith("[MeSH Terms]"):
                        for char in ['*', '"', '[MeSH Terms]', '"', '"']:
                            mesh = t.replace(char, "")
                        mesh_for_single_term['MeSH_Terms'][len(mesh_for_single_term['MeSH_Terms'])] = mesh
                result.append(mesh_for_single_term)
        return result


class UMLS_MeSH_Suggestion(Suggestion):
    def __init__(self, params):
        super().__init__(params)
        self.base_url = self.config["umls_url"]

    def suggest(self):
        terms = self.payload['Keywords']
        result = []

        for term in terms:
            umls_terms = set()
            res = requests.get(self.base_url + term)
            dict_set = json.loads(res.text)
            words = dict_set["hits"]["hits"]
            for word in words:
                #score = word["_score"]
                sources = word["_source"]["thesaurus"]
                for source in sources:
                    if "MRCONSO_STR" in source:
                        type = source['MRCONSO_SAB']
                        if type=="MSH":
                            mesh_term = source["MRCONSO_STR"]
                            umls_terms.add(mesh_term)
            m_dict = {i:t for i, t in enumerate(umls_terms)}
            mesh_for_single_term = {
                "Keywords": [term],
                "type": "UMLS",
                "MeSH_Terms": m_dict
            }

            result.append(mesh_for_single_term)
        return result

class MetaMap_MeSH_Suggestion(Suggestion):
    def __init__(self, params):
        super().__init__(params)
        self.base_url = self.config["umls_url"]

    def suggest(self):
        terms = self.payload['Keywords']
        result = []
        for term in terms:
            umls_terms = set()
            metamap_get_terms = subprocess.Popen('echo "' + term + '" | public_mm/bin/metamap -I', shell=True, stdout=subprocess.PIPE).stdout
            metamap_terms = metamap_get_terms.read().decode().split('\n')

            for metamap_term in metamap_terms:
                chunks = metamap_term.split()
                for chunk in chunks:
                    if (":" in chunk) and ("C" in chunk):
                        term_id = chunk.split(":")[0]
                        print(term_id)
                        res = requests.get(self.base_url + "cui:" + term_id)
                        print(res)
                        dict_set = json.loads(res.text)
                        words = dict_set["hits"]["hits"]
                        for word in words:
                            # score = word["_score"]
                            sources = word["_source"]["thesaurus"]
                            for source in sources:
                                if "MRCONSO_STR" in source:
                                    type = source['MRCONSO_SAB']
                                    if type == "MSH":
                                        mesh_term = source["MRCONSO_STR"]
                                        umls_terms.add(mesh_term)
            m_dict = {i: t for i, t in enumerate(umls_terms)}
            mesh_for_single_term = {
                "Keywords": [term],
                "type": "ATM",
                "MeSH_Terms": m_dict
            }
            result.append(mesh_for_single_term)
        return result
