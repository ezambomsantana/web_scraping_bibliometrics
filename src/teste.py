import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import sys  
import re
import networkx as nx

reload(sys)  
sys.setdefaultencoding('utf8')

df_excel = pd.read_excel('/home/eduardo/Downloads/SIGraDi2018_metadata.xls', sheetname='Papers Ordered by Tracks')

lista = []
for s in df_excel['references']:
    kws = s.split('(')  
    for k in kws:
        print(k.strip().lower())