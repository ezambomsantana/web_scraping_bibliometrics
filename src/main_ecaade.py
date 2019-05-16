import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import sys  
import re
import networkx as nx

def get_synonyms():
    keywords = {}
    with open("/Users/eduardosantana/pesquisa/key - eCAADe.csv") as f:
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

keywords = get_synonyms()

url_ecc = "http://papers.cumincad.org/cgi-bin/works/Search?search=&paint=on&f%3A1=year&e%3A1=%3E%3D+x&v%3A1=1998&f%3A2=year&e%3A2=%3C%3D+x&v%3A2=2018&f%3A3=source&e%3A3=%3D~+m%2Fx%2Fi&v%3A3=eCAADe&f%3A4=&e%3A4=&v%3A4=&f%3A5=&e%3A5=&v%3A5=&grouping=and&days=&sort=DEFAULT&sort1=&sort2=&sort3=&max=3000&fields=id&fields=authors&fields=year&fields=title&fields=source&fields=summary&fields=WOS&fields=keywords&fields=series&fields=type&fields=email&fields=more&fields=content&fields=fullText&fields=references&fields=seeAlso&_form=AdvancedSearchForm&_formname=&format=LONG&frames=NONE"
page = requests.get(url_ecc)

soup = BeautifulSoup(page.text, 'html.parser')

items = soup.find_all(class_='DATA')

G = nx.Graph()

reference_year = []
author_year = []
title_year = []
keyword_year = []
conf_year = []

authors_ref = []

authors = []
title = ''
year = 0

lista = ["parametric design", "digital fabrication", "bim", "collaborative design", "virtual reality", "urban design", "generative design", "shape grammars", "design process", "simulation"]

keys = []

for artist_name in items:

    header = artist_name.find("th")
    data = artist_name.find("td")

    if header.contents[0] == 'authors':
        authors = data.contents[0].split(';') 

    if header.contents[0] == 'year':
        year = data.contents[0]

    if header.contents[0] == 'title':
        title = data.contents[0]

    if header.contents[0] == 'keywords':
        kws = data.contents[0].replace(',',';').replace('/',';').split(';') 
        for k in kws:
            if k != '':
                if k.strip().lower() in keywords:
                    k = keywords[k.strip().lower()]

                if k.strip().lower() in lista:
                    keys.append(k.strip().lower())

#                G.add_node(k)
#                keyword_year.append([k.strip().lower(), year])  
#                achou = False
#                for k2 in kws:
#                    if k2.strip().lower() in keywords:
#                        k2 = keywords[k2.strip().lower()]
#                    if (k == k2):
#                        
#                        achou = True
#                    if achou == True and k != k2:
#                        p1 = k.strip().lower()
#                        p2 = k2.strip().lower()
#                        if G.has_edge(p1, p2):
#                            G[p1][p2]['weight'] += 1
#                        elif G.has_edge(p2, p1):
#                            G[p2][p1]['weight'] += 1
#                        else:
#                            G.add_edge(p1, p2, weight=1)
                         
    if header.contents[0] == 'references':
        title_year.append([title, year])
        for a in authors:
            author_year.append([a.strip().lower(), year])  
        
        refs = data.find_all(width="100%")    
        
        for ref in refs:
            try:
                autores = ref.contents[0].strip().rstrip("\n\r")
                titulo = ref.contents[1].get_text().strip().rstrip("\n\r")
                conferencia = ref.contents[2].strip().rstrip("\n\r").replace(", ", "")

                if 'sigradi' in conferencia.lower():
                    conf_year.append(['ecaade', year])

                reference_year.append([titulo.strip().lower(), conferencia.strip().lower()])  
            except:
                print("An exception occurred")

        if len(keys) > 0:         
            if autores != '':
                autores = autores.split('(')[0]
                if autores != '':
                    kws = autores.replace(' and ',';').replace('., ',';').replace('&',';').split(';') 
                    for k in kws:
                        if k.strip().lower() != '':
                            for key in keys:
                                authors_ref.append([k.strip().lower(), key, year])  
            keys = []            
            
        title = ''
        year = 0
        authors = []      

print(conf_year)
df = pd.DataFrame(conf_year, columns = ['k1', 'year']) 
df = df.groupby(['k1','year']).size()
print(df)

df = pd.DataFrame(authors_ref, columns = ['author', 'key', 'year']) 
teste = df.groupby(['author', 'key', 'year']).size()
teste = teste.reset_index()
teste.columns = ['Author', 'Key', 'Year', 'Count']

teste = teste.sort_values(by=['Year', 'Count'], ascending=False)

for x in range(1999, 2019):
    teste[teste['Year'] == str(x)].to_csv("/Users/eduardosantana/pesquisa/authors_" + str(x) + ".csv", index=False)            

pos = nx.circular_layout(G)
weights = [G[u][v]['weight'] * 4 for u,v in G.edges()]
#nx.draw_networkx(G, pos=pos)
#nx.draw_networkx_edges(G,pos,width=weights, edge_color='g', arrows=False)
#lt.show()

related_keywords = []
for u,v,a in G.edges(data=True):
    related_keywords.append([u,v,a['weight']])

df = pd.DataFrame(related_keywords, columns = ['k1', 'k2', 'count']) 
df = df.sort_values(by=['count'], ascending=False)
df.to_csv("/home/eduardo/keywords_count.csv", index=False)

lista = ["parametric design", "digital fabrication", "bim", "collaborative design", "virtual reality", "urban design", "generative design", "shape grammars", "design process", "architecture"]
conta = {}

for a in lista:
    conta[a] = 0

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
plt.show()

###### get number of papers by year

df = pd.DataFrame(title_year, columns = ['Title', 'Year']) 

teste = df.groupby(df.Year).agg('count')
teste = teste.reset_index()
teste.columns = ['Year', 'Count']

#teste.plot.bar(x='Year', y='Count', rot=0)
#plt.show()

###### Get All Keyords 

df = pd.DataFrame(keyword_year, columns = ['Keyword', 'Year']) 
teste = df.groupby(['Keyword']).size()
teste = teste.reset_index()
teste.columns = ['Keyword', 'Count']

teste = teste.sort_values(by=['Count'], ascending=False)

teste.to_csv("/home/eduardo/keywords.csv", index=False)
teste = teste.head(10)

teste.plot.bar(x='Keyword', y='Count', rot=0)
plt.show()

###### Get Keyords By Year

teste = df.groupby(['Keyword', 'Year']).size()
teste = teste.reset_index()
teste.columns = ['Keyword', 'Year', 'Count']

teste = teste.sort_values(by=['Year', 'Count'], ascending=False)

for x in range(1999, 2019):
    teste[teste['Year'] == str(x)].to_csv("/home/eduardo/keywords/" + str(x) + ".csv", index=False)

teste = teste.head(10)
teste.plot.bar(x='Keyword', y='Count', rot=0)
plt.show()


###### Get count authors 

df = pd.DataFrame(author_year, columns = ['Author', 'Year']) 

teste = df.groupby(df.Author).agg('count')
teste = teste.reset_index()
teste.columns = ['Author', 'Count']

teste = teste.sort_values(by=['Count'], ascending=False)
teste = teste.head(10)

teste.plot.bar(x='Author', y='Count', rot=0)
plt.show()

###### Get count authors 

df = pd.DataFrame(reference_year, columns = ['Titulo', 'Conferencia']) 

teste = df.groupby(df.Titulo).agg('count')
teste = teste.reset_index()
teste.columns = ['Titulo', 'Count']

teste = teste.sort_values(by=['Count'], ascending=False)
teste = teste.head(10)
#print(teste)

teste.plot.bar(x='Titulo', y='Count', rot=0)
plt.show()