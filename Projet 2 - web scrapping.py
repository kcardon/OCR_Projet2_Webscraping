# Import des packages
import requests
from bs4 import BeautifulSoup
import pandas as pd

urlStart = "http://books.toscrape.com/"
page = requests.get(urlStart)
if page.ok:
    html = BeautifulSoup(page.content, "html.parser")
    # Récupération du nombre de pages à éplucher
    nbPages = html.find("li", class_="current").string.strip().split()[-1]
    print(nbPages)

    links = (
        []
    )  # création d'une variable qui contiendra les liens vers les pages individuelles de chaque livre
    for page in range(
        1, int(nbPages) + 1
    ):  # Loop sur chaque page : on récupère l'url complet de la page
        url = str(urlStart + "/catalogue/page-" + str(page) + ".html")
        page = requests.get(url)
        html = BeautifulSoup(page.content, "html.parser")
        for link in html.find_all(
            "a"
        ):  # Loop pour chaque lien identifié : on l'enregistre dans la liste de links
            if not "category" in str(link) and link.get("href") != "../index.html":
                if urlStart + "catalogue/" + link.get("href") not in links:
                    links.append(urlStart + "catalogue/" + link.get("href"))

    BeautifulSoup(requests.get(links[0]).content, "html.parser")

    # Création d'un data frame pandas permettant de récupérer toutes les infos désirées

    col = [
        "product_page_url",
        "universal_ product_code (upc)",
        "title",
        "price_including_tax",
        "price_excluding_tax",
        "number_available",
        "product_description",
        "category",
        "review_rating",
        "image_url",
    ]
    DF = pd.DataFrame(columns=col)

    # Outils pour la récupération des données
    import re

    ratingStr = ["Zero", "One", "Two", "Three", "Four", "Five"]
    ratingNum = ["0", "1", "2", "3", "4", "5"]

    for i in range(len(links)):
        bookHtml = BeautifulSoup(requests.get(links[i]).content, "html.parser")
        bookData = [  # récupération des données
            # Page URL
            links[i],
            # UPC
            bookHtml.find("td").text,
            # Titre
            bookHtml.find("h1").text,
            # Prix TTC
            bookHtml.find_all("td")[2],
            # PRIX HT
            bookHtml.find_all("td")[3],
            # Stock (extraction des digits avec "re.findall")
            re.findall("\d+", bookHtml.find_all("td")[5].text)[0],
            # Description
            bookHtml.find_all("p")[-1].text,
            # Categorie
            bookHtml.find_all("a")[-1].text,
            # Score
            ratingNum[
                ratingStr.index(str(bookHtml.find_all("p")[2].attrs["class"][1]))
            ],
            # Lien de l'image
            bookHtml.find("img").attrs["src"],
        ]
        DF.loc[len(DF)] = bookData
    print(DF)
    DF.to_csv("ScrapedBooks.csv")

print("hello world")
