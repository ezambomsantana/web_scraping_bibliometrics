import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import sys  
import re

reload(sys)  
sys.setdefaultencoding('utf8')

url_ecc = "http://papers.cumincad.org/cgi-bin/works/Search?search=&paint=on&f%3A1=year&e%3A1=%3E%3D+x&v%3A1=1998&f%3A2=year&e%3A2=%3C%3D+x&v%3A2=2018&f%3A3=source&e%3A3=%3D~+m%2Fx%2Fi&v%3A3=eCAADe&f%3A4=&e%3A4=&v%3A4=&f%3A5=&e%3A5=&v%3A5=&grouping=and&days=&sort=DEFAULT&sort1=&sort2=&sort3=&max=3000&fields=id&fields=authors&fields=year&fields=title&fields=source&fields=summary&fields=WOS&fields=keywords&fields=series&fields=type&fields=email&fields=more&fields=content&fields=fullText&fields=references&fields=seeAlso&_form=AdvancedSearchForm&_formname=&format=LONG&frames=NONE"
url_sigradi = "http://papers.cumincad.org/cgi-bin/works/Search?search=&paint=on&f%3A1=year&e%3A1=%3E%3D+x&v%3A1=1998&f%3A2=year&e%3A2=%3C%3D+x&v%3A2=2018&f%3A3=source&e%3A3=%3D~+m%2Fx%2Fi&v%3A3=sigradi&f%3A4=&e%3A4=&v%3A4=&f%3A5=&e%3A5=&v%3A5=&grouping=and&days=&sort=DEFAULT&sort1=&sort2=&sort3=&max=30000&fields=authors&fields=year&fields=title&fields=source&fields=keywords&fields=references&_form=AdvancedSearchForm&_formname=&format=LONG&frames=NONE"
page = requests.get(url_sigradi)

soup = BeautifulSoup(page.text, 'html.parser')

items = soup.find_all(class_='DATA')

i = 0

reference_year = []
author_year = []
title_year = []
keyword_year = []

authors = []
title = ''
year = 0

i = 1
for artist_name in items:

    header = artist_name.find("th")
    data = artist_name.find("td")

    if header.contents[0] == 'authors':
        i = i + 1
        authors = data.contents[0].split(';') 

    if header.contents[0] == 'year':
        year = data.contents[0]

    if header.contents[0] == 'title':
        title = data.contents[0]

    if header.contents[0] == 'keywords':
        kws = data.contents[0].replace(',',';').replace('/',';').split(';')  
        for k in kws:
            if k != '':
                keyword_year.append([k.strip().lower(), year])             
        
    if header.contents[0] != 'references':
        print(data.contents[0])
    else:
        title_year.append([title, year])
        for a in authors:
            author_year.append([a.strip().lower(), year])  
        title = ''
        year = 0
        authors = [];
        print('----------- REFS ---------' + str(i))
        refs = data.find_all(width="100%")
        
        for ref in refs:
            try:
                autores = ref.contents[0].strip().rstrip("\n\r")
                titulo = ref.contents[1].get_text().strip().rstrip("\n\r")
                conferencia = ref.contents[2].strip().rstrip("\n\r").replace(", ", "")
                reference_year.append([titulo.strip().lower(), conferencia.strip().lower()])  
            except:
                print("An exception occurred")



###### get number of papers by year

df = pd.DataFrame(title_year, columns = ['Title', 'Year']) 

teste = df.groupby(df.Year).agg('count')
teste = teste.reset_index()
teste.columns = ['Year', 'Count']

#teste.plot.bar(x='Year', y='Count', rot=0)
#plt.show()


###### Read 2018 sigradi data

df_excel = pd.read_excel('/home/eduardo/Downloads/SIGraDi2018_metadata.xls', sheetname='Papers Ordered by Tracks')
df_excel = df_excel[['keywords']]

lista = []
for s in df_excel['keywords']:
    kws = s.replace(',',';').replace('/',';').split(';')  
    for k in kws:
        if k != '':
            lista.append([k.strip().lower(), "2018"])   

df_excel = pd.DataFrame(lista, columns = ['Keyword', 'Year']) 
df = pd.DataFrame(keyword_year, columns = ['Keyword', 'Year']) 
df = df.append(df_excel)

###### Get All Keyords

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

teste = teste.sort_values(by=['Count'], ascending=False)

teste.to_csv("/home/eduardo/keywords_year.csv", index=False)
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