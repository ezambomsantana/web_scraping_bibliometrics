import pandas as pd

df_excel = pd.read_excel('/home/eduardo/Downloads/SIGraDi2018_metadata.xls', sheetname='Papers Ordered by Tracks')
df_excel = df_excel[['keywords']]

lista = []
for s in df_excel['keywords']:
    kws = s.replace(',',';').replace('/',';').split(';')  
    for k in kws:
        if k != '':
            lista.append([k.strip().lower(), "2018"])   

print(lista)

df_excel['Year'] = '2018'
df_excel.columns = ['Keyword', 'Year']