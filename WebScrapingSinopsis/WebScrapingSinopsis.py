from bs4 import BeautifulSoup
import requests
import pandas as pd

df_links=pd.read_csv('links.csv')
df_links_final = df_links.dropna()
id = df_links_final["tmdbId"]
csv = open('sinopsis.csv', "w+", encoding="ANSI")
for n in id:
    link = int(n)
    
    completo = "https://www.themoviedb.org/movie/" + str(link)
    page = requests.get(completo)
    soup = BeautifulSoup (page.content, 'html.parser')
    sinopsis = soup.find('div',class_='overview')

    try:
        for s in sinopsis.find('p'):
            csv.write(s.get_text().strip()+";"+"\n") 
            print(s.get_text().strip())
    except:
        print("Error")
     