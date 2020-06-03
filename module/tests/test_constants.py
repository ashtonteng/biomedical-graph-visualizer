# Test cases
ADHD = {
    'ID': 'Q181923',
    'Name': 'attention deficit hyperactivity disorder',
    'Link': 'https://www.wikidata.org/wiki/Q181923',
    'DrugIDs': ['Q410441', 'Q419008', 'Q423288', 'Q1706418', 
                'Q898407', 'Q1207210', 'Q58396', 'Q834280',
                'Q412221', 'Q402633', 'Q191924', 'Q179452', 
                'Q417240', 'Q61387', 'Q1706418', 'Q2506823',
                'Q5613599', 'Q1207210', 'Q419008','Q422112'],
    'DrugNames': ['modafinil', 'pemoline', 'desipramine', 'dextroamphetamine', 
                  'venlafaxine', 'dexmethylphenidate', 'imipramine', 'bupropion',
                  'clonidine', '(±)-deprenyl', 'D-methamphetamine', 'DL-amphetamine',
                  'atomoxetine', 'nortriptyline', 'dextroamphetamine', '(R)-amphetamine',
                  'guanfacine', 'dexmethylphenidate', 'pemoline', 'methylphenidate'],
    'FDADrugIDs': ['Q1706418', 'Q2506823', 'Q5613599', 'Q1207210', 
                   'Q419008','Q422112'],
    'FDADrugNames': ['dextroamphetamine', '(R)-amphetamine', 'guanfacine', 'dexmethylphenidate', 
                     'pemoline', 'methylphenidate']
}

DEPRESSION = {
    'ID': 'Q42844',  
    'Name': 'major depressive disorders',
    'Link': 'https://www.wikidata.org/wiki/Q42844',
    'DrugIDs':['Q2622367', 'Q2273909', 'Q834280', 'Q238544',
               'Q395229', 'Q58356', 'Q6535779', 'Q27139037', 
               'Q418361', 'Q411932', 'Q1452256', 'Q243547', 
               'Q334477', 'Q208144'],
    'DrugNames': ['Mood stabilizer', 'serotonin–norepinephrine reuptake inhibitor', 'bupropion', 'oxitriptan'
                  'agomelatine', 'amoxapine', 'levomilnacipran', 'vilazodone hydrochloride', 
                  'maprotiline', 'duloxetine', 'levosulpiride', 'ketamine',
                  'selective serotonin reuptake inhibitor', 'antipsychotic'], 
    'FDADrugIDs':['Q834280', 'Q238544', 'Q395229', 'Q58356', 
                  'Q6535779', 'Q27139037', 'Q418361', 'Q411932', 
                  'Q1452256'],
    'FDADrugNames': ['bupropion', 'oxitriptan','agomelatine', 'amoxapine', 
                     'levomilnacipran', 'vilazodone hydrochloride', 'maprotiline', 'duloxetine', 
                     'levosulpiride']
}

DIABETES = {
    'ID': 'Q3025883',  
    'Name': 'type-2 diabetes',
    'Link': 'https://www.wikidata.org/wiki/Q3025883',
    'DrugIDs':['Q27275212', 'Q772735', 'Q409898', 'Q15269678',
               'Q899036', 'Q27077223', 'Q15269682', 'Q954845'
               'Q19484', 'Q288280'],
    'DrugNames': ['luseogliflozin', 'miglitol', 'dapagliflozin', 'teneligliptin'
                  'Colesevelam', 'ertugliflozin', 'anagliptin', 'statin',
                  'metformin', 'ACE inhibitor'],
    'FDADrugIDs':['Q27275212', 'Q772735', 'Q409898', 'Q15269678',
                  'Q899036', 'Q27077223', 'Q15269682'],
    'FDADrugNames': ['luseogliflozin', 'miglitol', 'dapagliflozin', 'teneligliptin'
                    'Colesevelam', 'ertugliflozin', 'anagliptin']
}

PE = {
    'ID': 'Q220570',
    'Name': 'Pulmonary Embolism',
    'Link': 'https://www.wikidata.org/wiki/Q220570',
    'DrugIDs':['Q407431', 'Q3617574', 'Q267896', 'Q417169',
               'Q1851701', 'Q410374', 'Q20817252', 'Q416485',
               'Q4765471', 'Q420886', 'Q414462', 'Q6724151',
               'Q27077698', 'Q21011234', 'Q20078502', 'Q420262'
               'Q45769835', 'Q190016', 'Q21011234'],
    'DrugNames': ['warfarin', 'anisindione', 'Phenprocoumon', 'PLAU',
                  'Dalteparin', 'papaverine', 'Tinzaparin', 'Streptokinase', 
                  'Anistreplase', 'dicumarol', 'apixaban', 'macitentan', 
                  'fondaparinux', 'edoxaban', 'dabigatran etexilate', 'rivaroxaban'
                  'Alteplase', 'heparin', 'edoxaban']
}

AIDS = {
    'ID': 'Q12199',  
    'Name': 'AIDS',
    'Link': 'https://www.wikidata.org/wiki/Q12199',
    'DrugIDs':['Q370244', 'Q422654', 'Q425490', 'Q304330',
               'Q422645', 'Q198504', 'Q422585', 'Q422618', 
               'Q422606', 'Q422631', 'Q155954', 'Q423984',
               'Q423366', 'Q422198', 'Q263713', 'Q2344582',
               'Q423327', 'Q3765251', 'Q27132753', 'Q421552', 
               'Q6482030'],
    'DrugNames': ['delavirdine', 'saquinavir', 'indinavir', 'abacavir',
                  'efavirenz', 'zidovudine', 'lopinavir', 'ritonavir',
                  'didanosine', 'lamivudine', 'tenofovir', 'stavudine',
                  'nelfinavir', 'amprenavir', 'nevirapine', 'zalcitabine',
                  'enfuvirtide', 'darunavir', 'tenofovir disoproxil', 'raltegravir',
                  'Lamivudine/zidovudine']
}

TEST_CONDITIONS = [ADHD, PE, AIDS, DEPRESSION, DIABETES]
FDA_TEST_CONDITIONS = [ADHD, DEPRESSION, DIABETES]