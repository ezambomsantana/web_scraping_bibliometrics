
import pandas as pd
import matplotlib.pyplot as plt
import sys  
import re
import networkx as nx
import functions as f

reload(sys)  
sys.setdefaultencoding('utf8')

folder = "/home/eduardo/sigradi/"

keywords = f.get_synonyms(folder + "key_sigradi.csv")
print(keywords)

G = nx.Graph()

keyword_year = []
conf_year = []
authors_ref = []
year = 0
keys = []

for paper in f.get_page("http://papers.cumincad.org/cgi-bin/works/Search?search=&paint=on&f%3A1=year&e%3A1=%3E%3D+x&v%3A1=1998&f%3A2=year&e%3A2=%3C%3D+x&v%3A2=2019&f%3A3=source&e%3A3=%3D~+m%2Fx%2Fi&v%3A3=sigradi&f%3A4=&e%3A4=&v%3A4=&f%3A5=&e%3A5=&v%3A5=&grouping=and&days=&sort=DEFAULT&sort1=&sort2=&sort3=&max=3000&fields=authors&fields=year&fields=title&fields=source&fields=keywords&fields=references&_form=AdvancedSearchForm&_formname=&format=LONG&frames=NONE"):

    header = paper.find("th")
    data = paper.find("td")

    if header.contents[0] == 'year':
        year = data.contents[0]

    if header.contents[0] == 'keywords':
        kws = data.contents[0].replace(',',';').replace('/',';').split(';') 
        for k in kws:
            if k != '':
                if k.strip().lower() in keywords:
                    k = keywords[k.strip().lower()]

                if k.strip().lower() != '':
                    keys.append(k.strip().lower())
                    G.add_node(k.strip().lower())
                    keyword_year.append([k.strip().lower(), year])  
                    achou = False
                    for k2 in kws:
                        if k2.strip().lower() != '':
                            if k2.strip().lower() in keywords:
                                k2 = keywords[k2.strip().lower()]
                            if (k == k2):                        
                                achou = True
                            if achou == True and k != k2:
                                p1 = k.strip().lower()
                                p2 = k2.strip().lower()
                                if G.has_edge(p1, p2):
                                    G[p1][p2]['weight'] += 1
                                elif G.has_edge(p2, p1):
                                    G[p2][p1]['weight'] += 1
                                else:
                                    G.add_edge(p1, p2, weight=1)
                         
    if header.contents[0] == 'references':
        refs = data.find_all(width="100%")

        autores = ""
        
        for ref in refs:
            try:

                autores = ref.contents[0].strip().rstrip("\n\r")
                titulo = ref.contents[1].get_text().strip().rstrip("\n\r")
                conferencia = ref.contents[2].strip().rstrip("\n\r").replace(", ", "")
          
                if autores != '':
                    autores = autores.split('(')[0]
                    if autores != '':
                        kws = autores.replace(' y ',';').replace(' e ',';').replace(' and ',';').replace('., ',';').replace('&',';').split(';') 
                        for k in kws:
                            if k.strip().lower() != '':
                                for key in keys:
                                    authors_ref.append([k.strip().lower(), key, year])  
                    

                if 'ecaade' in conferencia.lower():
                    conf_year.append(['ecaade', year])
            except:
                print("An exception occurred")
 
        keys = []    
        year = 0  

lista = ["parametric design", "digital fabrication", "bim", "architecture", "design", "heritage", "design process", "architectural design", "shape grammar", "virtual reality"]

f.generate_network(G, lista)

df = pd.DataFrame(keyword_year, columns = ['Keyword', 'Year']) 
df = df.append(f.read_excel(folder, keywords))

f.get_all_keywords(keyword_year, folder)
f.generate_keywords_by_year(keyword_year, folder)
f.authors_by_keywords(authors_ref, keyword_year, folder + "authors/sigradi/")
f.generate_cross_ref(conf_year, folder)
