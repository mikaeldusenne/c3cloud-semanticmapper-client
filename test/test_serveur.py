import json
from c3_cloud_client import client
from c3_cloud_client import objects
import pandas as pd
import jsondiff

client.__init__()
client.baseurl = 'https://rubis.limics.upmc.fr/c3-cloud/'
# client.baseurl = 'http://localhost:8000/c3-cloud/'

def comparedicts(a, b):
    d = jsondiff.diff(a, b)
    if len(d):
        print(a)
        print('========')
        print(b)
        print('================')
        print(d)
    assert len(d) == 0

def loadjsonfile(f):
    with open(f) as f:
        js = json.load(f)
    return js

def test_albuminuria_cdsm_osaki():
    answer = loadjsonfile('testdata/albuminuria_cdsm_osaki.json')
    req = client.translate(code = 'albuminuria',
                           code_system = 'http://www.c3-cloud.eu/fhir/clinical-concept',
                           fromSite = 'CDSM',
                           toSite = 'OSAKI')
    reqjs = json.loads(req.text)
    ansjs = loadjsonfile('testdata/albuminuria_cdsm_osaki_result.json')
    comparedicts(reqjs, ansjs)

def test_upload():
    c, cs, uri, des, con, si = "code1", "cs1", "uri1", "des1", "test", "EFG"
    m = objects.Mapping(**{
        "codes": [
                {"code": c,
                "code_system": {"code_system": cs, "uri": uri},
                "designation": des}],
        "concept": con, "site": si})
    
    client.upload_mapping(m)
    ans = client.sendrequest('mappings', get = {'site':'EFG', 'concept':'test'}).text
    print("test upload ans:", ans)
    assert json.loads(ans)['data'] == [{'code': c, 'code_system': cs, 'code_system_uri': uri, 'concept': con, 'designation': des, 'site': si}]

    
def test_unauthorized_request():
    key = client.APIKEY
    client.APIKEY = "wrongapikey"
    ans = client.upload_concept("test")
    print("test upload concept:", ans)
    client.APIKEY = key
    assert ans.status_code == 401

    
def test_delete_concept():
    concept = "test"
    print(client.delete_concept(concept))
    ans = client.sendrequest('concepts', get = {'concept':concept})
    print(ans)
    assert json.loads(ans.text)['count'] == 0


def test_get_terminology():
    css = pd.read_csv('../data/data_2019_02_07/terminologies.csv')[['code_system','code_system_uri']]
    def check(r):
        print(f'checking terminology {r}')
        cs = client.get_code_system(r['code_system'])
        if not cs.uri == r['code_system_uri']:
            print(cs.uri)
            print(r['code_system_uri'])
            print('no')
            raise            
    css.apply(check, axis = 1)

def translatorchecker(c,cs,f,t,shouldbe):
    req = client.translate(code = c,
                           code_system = cs,
                           fromSite = f,
                           toSite = t)
    
    req = json.loads(req.text)
    ref = shouldbe
    comparedicts(ref, req)


def translatorcheckerr(c,cs,f,t,shouldbe):
    translatorchecker(c,
                      client.get_code_system(cs).uri,
                      f,
                      t,
                      loadjsonfile(shouldbe))    
    

def test_multi_code_translate_structural_renal_tract_disease():
    translatorcheckerr('118642009',
                       'SNOMED CT',
                       'CDSM',
                       'OSAKI',
                       './testdata/structural_renal_tract_disease_cdsm_osaki_result.json')


## print(translate("BRO", get_code_system('HL7-ROLE').uri, 'CDSM', 'OSAKI'))
def test_hl7_role():
    translatorcheckerr('BRO',
                       'HL7-ROLE',
                       'CDSM',
                       'OSAKI',
                       './testdata/hl7_bro_cdsm_osaki_result.json')


def test_hl7_role():
     translatorcheckerr("influenza_vaccines",
                        'C3-Cloud',
                        'OSAKI',
                        'RJH',
                        './testdata/c3dp_influenza_osaki_rjh_result.json')


def test_update_existing_mapping():
    d = loadjsonfile("./testdata/mapping_update_hfca_lipid__data.json")
    dd = loadjsonfile("./testdata/mapping_update_hfca_lipid__data.json")
    dd['codes'][0]['designation'] = "TEST"

    mmodif = objects.Mapping(**dd)
    morig = objects.Mapping(**d)

    client.upload_mapping(mmodif)
    ans = client.upload_mapping(morig)

    m = client.get_mapping(site=d['site'], concept=d['concept'])
    print("original: ", morig)
    print("modified: ", mmodif)
    print("observed: ", m)
    
    assert m == morig
    
    