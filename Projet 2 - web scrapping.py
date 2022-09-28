
import requests
from bs4 import BeautifulSoup
import pandas
urlstart = "http://books.toscrape.com/"
page = requests.get(urlstart)
soup = BeautifulSoup(page.content, 'html.parser')
#Récupération du nombre de pages à éplucher
nbpages=soup.find("li",class_="current").string.strip().split()[-1]
print(nbpages)

links=[] #création d'une variable qui contiendra les liens vers les pages individuelles de chaque livre
for page in range(1,int(nbpages)+1): #Loop sur chaque page : on récupère l'url complet de la page
    url=str(urlstart+"/catalogue/page-"+str(page)+".html")
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    for link in soup.find_all('a'): #Loop pour chaque lien identifié : on l'enregistre dans la liste de links
        if not "category" in str(link) and link.get('href')!="../index.html":
            links.append(link.get('href'))

print(links)


#Test avec une page produit
url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
page = requests.get(url)
soup = BeautifulSoup(page.content,'html.parser')
print(soup)