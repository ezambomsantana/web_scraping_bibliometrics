import requests
from bs4 import BeautifulSoup
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def get_synonyms(file):
    keywords = {}
    with open(file) as f:
        lis = [line.split(",") for line in f]     
        for i, x in enumerate(lis):            
            first = ''
            for i2, x2 in enumerate(x):  
                if x2.strip().lower() == '':
                    continue 
                if i2 == 0 and x2 != '':
                    first = x2.strip().lower()
                if i2 > 1 and x2 != '':
                    keywords[x2.strip().lower()] = first
    return keywords

def get_page(url):
    page = requests.get(url)

    soup = BeautifulSoup(page.text, 'html.parser')
    items = soup.find_all(class_='DATA')
    return items


###### Get All Keyords 
def get_all_keywords(keyword_year, file):
    df = pd.DataFrame(keyword_year, columns = ['Keyword', 'Year']) 
    teste = df.groupby(['Keyword']).size()
    teste = teste.reset_index()
    teste.columns = ['Keyword', 'Count']

    teste = teste.sort_values(by=['Count'], ascending=False)

    teste.to_csv(file + "keywords_sigradi.csv", index=False)

###### Get Keyords By Year

def generate_keywords_by_year(keyword_year, file):
    df = pd.DataFrame(keyword_year, columns = ['Keyword', 'Year']) 
    teste = df.groupby(['Keyword', 'Year']).size()
    teste = teste.reset_index()
    teste.columns = ['Keyword', 'Year', 'Count']

    teste = teste.sort_values(by=['Year', 'Count'], ascending=False)

    for x in range(1999, 2019):
        teste[teste['Year'] == str(x)].to_csv(file + "/keywords_" + str(x) + ".csv", index=False)

def generate_cross_ref(conf_year, file):      
    df = pd.DataFrame(conf_year, columns = ['k1', 'year']) 
    df = df.groupby(['k1','year']).size()
    df = df.reset_index()
    df.columns = ['Key', 'Year', 'Count']
    df.to_csv(file + "/num_sigradi_ecaade.csv", index=False)

def read_excel(file, keywords):
    df_excel = pd.read_excel(file + '/SIGraDi2018_metadata.xls', sheetname='Papers Ordered by Tracks')
    df_excel = df_excel[['keywords']]

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

    df_excel = pd.DataFrame(lista, columns = ['Keyword', 'Year']) 
    return df_excel

def authors_by_keywords(authors_ref, keyword_year, file):
    df = pd.DataFrame(authors_ref, columns = ['author', 'key', 'year']) 
    teste = df.groupby(['author', 'key', 'year']).size()
    teste = teste.reset_index()
    teste.columns = ['Author', 'Key', 'Year', 'Count']

    teste = teste.sort_values(by=['Author'], ascending=True)

    df = pd.DataFrame(keyword_year, columns = ['Keyword', 'Year']) 
    keys = df.groupby(['Keyword', 'Year']).size()
    keys = keys.reset_index()
    keys.columns = ['Keyword', 'Year', 'Count']

    keys = keys.sort_values(by=['Year', 'Count'], ascending=False)
    for x in range(1999, 2019):
        keys_year = keys[keys['Year'] == str(x)]
        keys_year = keys_year[~keys_year['Keyword'].isin(['architecture', 'design', 'education'])]
        for y in keys_year['Keyword'].head(5):
            teste2 = teste[teste['Key'] == y]
            teste2[teste2['Year'] == str(x)].to_csv(file + str(x) + "_" + y + "_sigradi_authors_" + ".csv", index=False)

def generate_network(G, lista):
    conta = {}

    for a in lista:
        conta[a] = 0

    related_keywords = []
    for u,v,a in G.edges(data=True):
        related_keywords.append([u,v,a['weight']])

    df = pd.DataFrame(related_keywords, columns = ['k1', 'k2', 'count']) 

    G = nx.Graph()
    for index, row in df.iterrows():

        if row['k1'] in lista or row['k2'] in lista:
            if row['k1'] in conta:
                if conta[row['k1']] >= 4:
                    continue

            if row['k2'] in conta:
                if conta[row['k2']] >= 4:
                    continue

            if row['k1'] in conta:
                conta[row['k1']] = conta[row['k1']] + 1

            if row['k2'] in conta:
                conta[row['k2']] = conta[row['k2']] + 1

            G.add_node(row['k1'])
            G.add_node(row['k2'])
            G.add_edge(row['k1'], row['k2'], weight=row['count'] / 2)

    pos = nx.circular_layout(G)
    weights = [G[u][v]['weight'] for u,v in G.edges()]
    nx.draw_networkx(G, pos=pos)
    nx.draw_networkx_edges(G,pos,width=weights, edge_color='g', arrows=False)
    plt.axis('off')
    plt.show()