
import pandas as pd
import matplotlib.pyplot as plt
import sys  
import re
import networkx as nx
import functions as f

df_excel = pd.read_excel('/home/eduardo/sigradi/SIGraDi2018_metadata.xls', sheetname='Papers Ordered by Tracks')

reload(sys)  
sys.setdefaultencoding('utf8')

folder = "/home/eduardo/sigradi/"

keywords = f.get_synonyms(folder + "key_sigradi.csv")

lista = []
for s in df_excel['keywords']:
    kws = s.replace(',',';').replace('/',';').split(';')  

    for k in kws:
        if k.strip().lower() in keywords:
            if 'reblock' in k:
                continue
        if k.strip().lower() in keywords:
            k = keywords[k.strip().lower()]
        if k != '':
            lista.append([k.strip().lower(), "2018"])   
            

keys = pd.DataFrame(lista, columns = ['Keyword', 'Year']) 
keys = keys.groupby(['Keyword','Year']).size()
keys = keys.reset_index()
keys.columns = ['Keyword','Year', 'Count']
keys = keys.sort_values(by=['Count'], ascending=False)

print(keys)

keys = ['parametric design',
'digital fabrication',
'bim',
'virtual reality',
'shape grammar']


authors_ref = []
for index, row in df_excel.iterrows():
    ks = []
    kws = row['keywords'].replace(',',';').replace('/',';').split(';')  
    for k in kws:
        if k.strip().lower() in keys:
            if k.strip().lower() in keywords:
                k = keywords[k.strip().lower()]
            print(k)
            ks.append(k.strip().lower())

    if isinstance(row['references'], unicode):
        k = row['references']
        for x in ks:
            authors_ref.append([k.strip().lower(), x])  

keys2 = pd.DataFrame(authors_ref, columns = ['Author', 'Keyword']) 
keys2 = keys2.groupby(['Author','Keyword']).size()
keys2 = keys2.reset_index()
keys2.columns = ['Author','Keyword', 'Count']
keys2 = keys2.sort_values(by=['Author'], ascending=True)
print(keys2)

for y in keys:
    teste2 = keys2[keys2['Keyword'] == y]
    teste2.to_csv("/home/eduardo/sigradi/2018_" + y + "_sigradi_authors_" + ".csv", index=False)